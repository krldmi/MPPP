"""This module defines the basic interface for satellites, satellite
instruments, and satellite snapshots.
"""
import numpy as np
import copy
import logging
import logging.config

import geo_image
import image_processing
import coverage
import palettes
from msgpp_config import APPLDIR

logging.config.fileConfig(APPLDIR+"/etc/logging.conf")
LOG = logging.getLogger('pp.satellite')


class Satellite(object):
    """This is the satellite class.
    """
    pass

class SatelliteChannel(object):
    """This is the satellite channel class.
    """

    #Channel data.
    data = None

    #Name of the channel.
    name = None

    #Operationnal wavelength range of the channel, in micrometers.
    wavelength_range = None

    #Shape of the channel data.
    shape = None

    #Channel resolution, in meters.
    resolution = 0

    def __init__(self, resolution = 0, 
                 wavelength_range = None, 
                 name = None, data = None):
        self.resolution = resolution
        self.wavelength_range = wavelength_range
        self.name = name
        self.data = data
        if(data is not None):
            self.shape = data.shape
        else:
            self.shape = None

    def __cmp__(self, ch2, key = 0):
        if(self.name == ch2.name):
            return 0
        elif(np.isnan(self.wavelength_range[1]) or
           self.name[0] == '_'):
            return 1
        elif(np.isnan(ch2.wavelength_range[1]) or
             ch2.name[0] == '_'):
            return -1
        else:
            return cmp(self.wavelength_range[1] - key,
                       ch2.wavelength_range[1] - key)

    def __repr__(self):
        return ("'%s: lambda (%.3f,%.3f,%.3f)um, shape %s, resolution %sm'"%
                (self.name, 
                 self.wavelength_range[0], 
                 self.wavelength_range[1], 
                 self.wavelength_range[2], 
                 self.shape, 
                 self.resolution))

    
    # Should be replaced by setitem !!!!
    def add_data(self, data):
        """Set the data of the channel.
        """
        self.data = data
        if isinstance(data, (np.ndarray, np.ma.core.MaskedArray)):
            self.shape = data.shape
        else:
            self.shape = np.nan

    def isloaded(self):
        """Tells if a channel contains loaded data.
        """
        return self.data is not None

    def check_range(self, min_range = 1.0):
        """Check that the data of the channels has a definition domain broader
        than *min_range* and return the data, otherwise return zeros.
        """
        if((self.data.max() - self.data.min()) < min_range):
            return np.ma.zeros(self.data.shape)
        else:
            return self.data

    def project(self, coverage_instance):
        """Make a projected copy of the current channel using the given
        *coverage_instance*.
        """
        res = copy.copy(self)
        if self.isloaded():
            LOG.info("Projecting channel %s (%fum)..."
                     %(self.name, self.wavelength_range[1]))
            res.data = coverage_instance.project_array(self.data)
            return res
        else:
            raise RuntimeError("Can't project, channel %s (%fum) not loaded."
                               %(self.name, self.wavelength_range[1]))
        

class SatelliteInstrument(Satellite):
    """This is the satellite instrument class.
    """
    channels = []

    def __init__(self, *args, **kwargs):
        super(SatelliteInstrument, self).__init__(*args, **kwargs)
        self.channels = []

    def __getitem__(self, key, aslist = False):
        LOG.debug("Getting item %s."%key)
        if(isinstance(key, float)):
            channels = [chn for chn in self.channels
                        if(chn.wavelength_range[0] <= key and
                           chn.wavelength_range[2] >= key)]
            channels = sorted(channels,
                              lambda ch1,ch2:
                                  ch1.__cmp__(ch2,key))
            
        elif(isinstance(key, str)):
            channels = [chn for chn in self.channels
                        if chn.name == key]
            channels = sorted(channels)

        elif(isinstance(key, int)):
            channels = [chn for chn in self.channels
                        if chn.resolution == key]
            channels = sorted(channels)

        elif(isinstance(key, (tuple, list))):
            channels = self[key[0], True]
            if(len(key) > 1 and len(channels) > 0):
                dummy_instance = SatelliteInstrument()
                dummy_instance.channels = channels
                channels = dummy_instance[key[1:]]
        else:
            raise KeyError("Malformed key.")

        if len(channels) == 0:
            raise KeyError("No corresponding channel.")
        elif aslist:
            return channels
        else:
            return channels[0]

    def check_channels(self, *channels):
        """Check if the *channels* are loaded, raise an error otherwise.
        """
        for chan in channels:
            if not self[chan].isloaded():
                raise RuntimeError("Required channel not loaded, aborting.")


    def loaded_channels(self):
        """Return the set of loaded_channels.
        """
        return set([chan for chan in self.channels if chan.isloaded()])

class SatelliteSnapshot(SatelliteInstrument):
    """This is the satellite snapshot class.
    """
    time_slot = None
    area = None

    def __init__(self, time_slot = None, area = None, *args, **kwargs):
        super(SatelliteSnapshot, self).__init__(*args, **kwargs)
        self.time_slot = time_slot
        self.area = area

    def overview(self):
        """Make an overview RGB image composite.
        """
        self.check_channels(0.6, 0.8, 10.8)

        ch1 = self[0.6].check_range()
        ch2 = self[0.8].check_range()
        ch3 = -self[10.8].data
        
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB")
        
        img.enhance(stretch = "crude")
        img.enhance(gamma = 1.6)

        return img
    
    overview.prerequisites = set([0.6, 0.8, 10.8])

    def airmass(self):
        """Make an airmass RGB image composite.
        
        +--------------------+--------------------+--------------------+
        | Channels           | Temp               | Gamma              |
        +====================+====================+====================+
        | WV6.2 - WV7.3      |     -25 to 0 K     | gamma 1            |
        +--------------------+--------------------+--------------------+
        | IR9.7 - IR10.8     |     -40 to 5 K     | gamma 1            |
        +--------------------+--------------------+--------------------+
        | WV6.2              |   243 to 208 K     | gamma 1            |
        +--------------------+--------------------+--------------------+
        """
        self.check_channels(6.2, 7.3, 9.7, 10.8)

        ch1 = self[6.2].data - self[7.3].data
        ch2 = self[9.7].data - self[10.8].data
        ch3 = self[6.2].data

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                self.area,
                                self.time_slot,
                                mode = "RGB",
                                range = ((-25,0),
                                         (-40,5),
                                         (243 - 70, 208 + 20)))
        return img
            
    airmass.prerequisites = set([6.2, 7.3, 9.7, 10.8])

    def ir108(self):
        """Make a black and white image of the IR 10.8um channel.
        """
        self.check_channels(10.8)

        img = geo_image.GeoImage(self[10.8].data,
                                 self.area,
                                 self.time_slot,
                                 mode = "L",
                                 range = (-70+273.15,57.5+273.15))
        img.enhance(inverse = True)
        return img

    ir108.prerequisites = set([10.8])

    def wv_high(self):
        """Make a black and white image of the IR 6.2um channel."""
        self.check_channels(6.2)

        img =  geo_image.GeoImage(self[6.2].data,
                                  self.area,
                                  self.time_slot,
                                  mode = "L")
        img.enhance(inverse = True, stretch = "linear")
        return img
    
    wv_high.prerequisites = set([6.2])

    def wv_low(self):
        """Make a black and white image of the IR 7.3um channel."""
        self.check_channels(7.3)

        img = geo_image.GeoImage(self[7.3].data,
                                 self.area,
                                 self.time_slot,
                                 mode = "L")
        img.enhance(inverse = True, stretch = "linear")
        return img

    wv_low.prerequisites = set([7.3])
        
    def natural(self):
        """Make a Natural Colors RGB image composite.
        """
        self.check_channels(0.6, 0.8, 1.6)
        
        ch1 = self[1.6].check_range()
        ch2 = self[0.8].check_range()
        ch3 = self[0.6].check_range()

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB",
                                 range = ((0,45),
                                          (0,45),
                                          (0,45)))



        img.enhance(gamma = 1.2)

        return img
    
    natural.prerequisites = set([0.6, 0.8, 1.6])
    

    def green_snow(self):
        """Make a Green Snow RGB image composite.
        """
        self.check_channels(0.8, 1.6, 10.8)

        ch1 = self[1.6].check_range()
        ch2 = self[0.8].check_range()
        ch3 = -self[10.8].data
        
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB")

        img.enhance(stretch = "crude")
        img.enhance(gamma = 1.6)

        return img

    green_snow.prerequisites = set([0.8, 1.6, 10.8])

    def red_snow(self):
        """Make a Red Snow RGB image composite.
        """
        self.check_channels(0.6, 1.6, 10.8)        

        ch1 = self[0.6].check_range()
        ch2 = self[1.6].check_range()
        ch3 = -self[10.8].data

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB")

        img.enhance(stretch = "crude")
        
        return img

    red_snow.prerequisites = set([0.6, 1.6, 10.8])

    def convection(self):
        """Make a Severe Convection RGB image composite.
        """
        self.check_channels(0.8, 1.6, 3.9, 6.2, 7.3, 10.8)

        ch1 = self[6.2].data - self[7.3].data
        ch2 = self[3.9].data - self[10.8].data
        ch3 = self[1.6].check_range() - self[0.6].check_range()

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB",
                                 range = ((-30, 0),
                                          (0, 55),
                                          (- 70, 20)))

        img.clip()
        img.enhance(stretch = "crude")

        return img

    convection.prerequisites = set([0.6, 1.6, 3.9, 6.2, 7.3, 10.8])


    def fog(self):
        """Make a Fog RGB image composite.
        """
        self.check_channels(8.7, 10.8, 12.0)

        ch1 = self[12.0].data - self[10.8].data
        ch2 = self[10.8].data - self[8.7].data
        ch3 = self[10.8].data
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB",
                                 range = ((-4, 2),
                                          (0, 6),
                                          (243, 283)))

        img.enhance(gamma = (1.0, 2.0, 1.0))
        
        return img

    fog.prerequisites = set([8.7, 10.8, 12.0])

    def night_fog(self):
        """Make a Night Fog RGB image composite.
        """
        self.check_channels(3.9, 10.8, 12.0)

        ch1 = self[12.0].data - self[10.8].data
        ch2 = self[10.8].data - self[3.9].data
        ch3 = self[10.8].data
        
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB",
                                 range = ((-4, 2),
                                          (0, 6),
                                          (243, 293)))
        
        img.enhance(gamma = (1.0, 2.0, 1.0))
        img.clip()

        return img

    night_fog.prerequisites = set([3.9, 10.8, 12.0])

    def cloudtop(self):
        """Make a Cloudtop RGB image composite.
        """
        self.check_channels(3.9, 10.8, 12.0)

        ch1 = -self[3.9].data
        ch2 = -self[10.8].data
        ch3 = -self[12.0].data

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB")

        img.enhance(stretch = (0.005, 0.005))

        return img
    
    cloudtop.prerequisites = set([3.9, 10.8, 12.0])

    def pge02(self):
        """Make a Cloudtype RGB image composite.
        """
        self.check_channels(["CloudType"])

        ch1 = self["CloudType"].data
        palette = palettes.cms_modified()

        img = geo_image.GeoImage(ch1,
                                 self.area,
                                 self.time_slot,
                                 mode = "P",
                                 palette = palette)

        return img

    pge02.prerequisites = set(["CloudType"])

    def pge02b(self):
        """Make a Cloudtype RGB image composite, depicting low clouds with
        palette colors, and the other as in the IR 10.8 channel.
        """
        self.check_channels([10.8, "CloudType"])

        ctype = self["CloudType"].data
        clouds = self[10.8].data

        palette = palettes.vv_legend()
        clouds = image_processing.crude_stretch(clouds)
        clouds = image_processing.gamma_correction(clouds, 1.6)
        clouds = 1 - clouds
        clouds = (clouds * 248 + 7).astype(np.uint8)
        clouds = np.ma.where(ctype <= 2, ctype, clouds)
        clouds = np.ma.where(4 < ctype < 9, ctype - 2, clouds)
        
        img = geo_image.GeoImage(clouds,
                                 self.area,
                                 self.time_slot,
                                 mode = "P",
                                 palette = palette)

        return img

    pge02b.prerequisites = set(["CloudType", 10.8])

    def pge02b_with_overlay(self):
        """Same as :meth:`pge02b`, with borders overlay.
        """
        self.check_channels([10.8, "CloudType"])
        
        img = self.pge02b()
        
        img.add_overlay()

        return img

    pge02b_with_overlay.prerequisites = set(["CloudType", 10.8])

    def pge02c(self):
        """Make an RGB composite showing clouds as depicted with the IR 10.8um
        channel, and cloudfree areas with land in green and sea in blue.
        """
        self.check_channels([10.8, "CloudType"])
        
        ctype = self["CloudType"].data
        clouds = self[10.8].data

        palette = palettes.tv_legend()

        clouds = (clouds - 205.0) / (295.0 - 205.0)
        clouds = (1 - clouds).clip(0, 1)
        clouds = (clouds * 250 + 5).astype(np.uint8)
        clouds = np.ma.where(ctype <= 4, ctype, clouds)

        img = geo_image.GeoImage(clouds,
                                 self.area,
                                 self.time_slot,
                                 mode = "P",
                                 palette = palette)
        
        return img

    pge02c.prequisites = set(["CloudType", 10.8])
        
    def pge02c_with_overlay(self):
        """Same as :meth:`pge02c` with borders overlay.
        """
        self.check_channels([10.8, "CloudType"])

        img = self.pge02c()

        img.add_overlay()

        return img

    pge02c_with_overlay.prerequisites = set(["CloudType", 10.8])

    def pge02d(self):
        """Same as :meth:`pge02c` with transparent cloud-free areas.
        """
        self.check_channels([10.8, "CloudType"])

        ctype = self["CloudType"].data

        img = self.pge02c()

        alpha = np.ma.where(ctype < 5, 0.0, 1.0)
        alpha = np.ma.where(ctype == 15, 0.5, alpha)
        alpha = np.ma.where(ctype == 19, 0.5, alpha)

        img.putalpha(alpha)
        
        return img
        
    pge02d.prerequisites = set(["CloudType", 10.8])
        
    def pge02e(self):
        """Same as :meth:`pge02d` with clouds as in :meth:`overview`.
        """
        self.check_channels([0.6, 0.8, 10.8, "CloudType"])

        img = self.overview()

        ctype = self["CloudType"].data

        alpha = np.ma.where(ctype < 5, 0.0, 1.0)
        alpha = np.ma.where(ctype == 15, 0.5, alpha)
        alpha = np.ma.where(ctype == 19, 0.5, alpha)

        img.putalpha(alpha)
        
        return img

    pge02e.prerequisites = set(["CloudType", 0.6, 0.8, 10.8])    

    def pge03(self):
        """Make an RGB composite of the CTTH.
        """
        self.check_channels(["CTTH"])

        ctth = self["CTTH"].data
        
        arr = (ctth.height*ctth.h_gain+ctth.h_intercept)
        ctth_data = np.where(ctth.height == ctth.h_nodata, 0, arr / 500.0 + 1)
        ctth_data = np.ma.array(ctth_data)

        palette = palettes.ctth_height()

        img = geo_image.GeoImage(ctth_data.astype(np.uint8),
                                 self.area,
                                 self.time_slot,
                                 mode = "P",
                                 palette = palette)

        return img
        
    pge03.prerequisites = set(["CTTH"])    

    def project(self, dest_area, channels = None):
        """Make a copy of the current snapshot projected onto the
        *dest_area*. Available areas are defined in the main configuration
        file. *channels* tells which channels are going to be present in the
        returned snapshot, and if None, all channels are copied over.

        Note: channels have to be loaded to be projected, otherwise an
        exception is raised.
        """
        if dest_area == self.area:
            return self
        
        _channels = set([])

        if channels is None:
            for chn in self.loaded_channels():
                _channels |= set([chn])

        elif(isinstance(channels, (list, tuple, set))):
            for chn in channels:
                try:
                    _channels |= set([self[chn]])
                except KeyError:
                    LOG.warning("Channel "+str(chn)+" not found,"
                                "thus not projected.")
        else:
            raise TypeError("Channels must be a list/"
                            "tuple/set of channel keys!")

        res = copy.copy(self)
        res.area = dest_area
        res.channels = []

        if not _channels <= self.loaded_channels():
            raise RuntimeError("Cannot project nonloaded channels: %s."
                               %(_channels - self.loaded_channels()))

        cov = {}

        for chan in _channels:
            if chan.resolution not in cov:
                cov[chan.resolution] = \
                    coverage.SatProjCov(self, 
                                        dest_area, 
                                        chan.resolution)
            res.channels.append(chan.project(cov[chan.resolution]))

        return res
            
                
