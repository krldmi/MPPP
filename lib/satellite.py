"""This module defines the basic interface for satellites, satellite
instruments, and satellite snapshots.
"""
import numpy as np

import geo_image

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
        if np.isnan(self.wavelength_range[1]):
            return 1
        elif np.isnan(ch2.wavelength_range[1]):
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
        self.shape = data.shape

    def isloaded(self):
        """Tells if a channel contains loaded data.
        """
        return self.data is not None

class SatelliteInstrument(object):
    """This is the satellite instrument class.
    """
    channels = []

    def __init__(self):
        self.channels = []

    def __getitem__(self, key, aslist = False):
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
    

class SatelliteSnapshot(SatelliteInstrument):
    """This is the satellite snapshot class.
    """
    time_slot = None
    area = None

    def __init__(self, time_slot = None, area = None, *args, **kwargs):
        super(SatelliteSnapshot, self).__init__(*args, **kwargs)
        self.time_slot = time_slot
        self.area = area

    def check_channels(self, *channels):
        """Check if the *channels* are loaded, raise an error otherwise.
        """

        for chan in channels:
            if not self[chan].isloaded():
                raise RuntimeError("Channel not loaded.")

    def overview(self):
        """Make an overview RGB image composite.
        """
        self.check_channels(0.6, 0.8, 10.8)

        ch1 = check_range(self[0.6].data)
        ch2 = check_range(self[0.8].data)
        ch3 = -self[10.8].data
        
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB")
        
        img.enhance(stretch = "crude")
        img.enhance(gamma = 1.6)

        return img
    
    overview.prerequisites = (0.6, 0.8, 10.8)

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
            
    airmass.prerequisites = (6.2, 7.3, 9.7, 10.8)

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

    ir108.prerequisites = (10.8)

    def wv_high(self):
        """Make a black and white image of the IR 6.2um channel."""
        self.check_channels(6.2)

        img =  geo_image.GeoImage(self[6.2].data,
                                  self.area,
                                  self.time_slot,
                                  mode = "L")
        img.enhance(inverse = True, stretch = "linear")
        return img
    
    wv_high.prerequisites = (6.2)

    def wv_low(self):
        """Make a black and white image of the IR 7.3um channel."""
        self.check_channels(7.3)

        img = geo_image.GeoImage(self[7.3].data,
                                 self.area,
                                 self.time_slot,
                                 mode = "L")
        img.enhance(inverse = True, stretch = "linear")
        return img

    wv_low.prerequisites = (7.3)
        
    def natural(self):
        """Make a Natural Colors RGB image composite.
        """
        self.check_channels(0.6, 0.8, 1.6)
        
        ch1 = check_range(self[1.6].data)
        ch2 = check_range(self[0.8].data)
        ch3 = check_range(self[0.6].data)

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB",
                                 range = ((0,45),
                                          (0,45),
                                          (0,45)))



        img.enhance(gamma = 1.2)

        return img
    
    natural.prerequisites = (0.6, 0.8, 1.6)
    

    def green_snow(self):
        """Make a Green Snow RGB image composite.
        """
        self.check_channels(0.8, 1.6, 10.8)

        ch1 = check_range(self[1.6].data)
        ch2 = check_range(self[0.8].data)
        ch3 = -self[10.8].data
        
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB")

        img.enhance(stretch = "crude")
        img.enhance(gamma = 1.6)

        return img

    green_snow.prerequisites = (0.8, 1.6, 10.8)

    def red_snow(self):
        """Make a Red Snow RGB image composite.
        """
        self.check_channels(0.6, 1.6, 10.8)        

        ch1 = check_range(self[0.6].data)
        ch2 = check_range(self[1.6].data)
        ch3 = -self[10.8].data

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB")

        img.enhance(stretch = "crude")
        
        return img

    red_snow.prerequisites = (0.6, 1.6, 10.8)

    def convection(self):
        """Make a Severe Convection RGB image composite.
        """
        self.check_channels(0.8, 1.6, 3.9, 6.2, 7.3, 10.8)

        ch1 = self[6.2].data - self[7.3].data
        ch2 = self[3.9].data - self[10.8].data
        ch3 = check_range(self[0.6].data) - check_range(self[1.6].data)

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

    convection.prerequisites = (0.6, 1.6, 3.9, 6.2, 7.3, 10.8)


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

    fog.prerequisites = (8.7, 10.8, 12.0)

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

# Old version, without co2 correction
#        im.enhance(gamma = (1.0, 2.0, 1.0))
#        im.clip()
#        im.enhance(stretch = "crude")
        return img

    night_fog.prerequisites = (3.9, 10.8, 12.0)

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

        img.enhance(stretch = (0.005,0.005))

        return img
    
    cloudtop.prerequisites = (3.9, 10.8, 12.0)

def check_range(arr, min_range = 1.0):
    """Check that the given array *arr* has a definition domain broader than
    *min_range*, otherwise return zeros.
    """
    if((arr.max() - arr.min()) < min_range):
        return np.ma.zeros(arr.shape)
    else:
        return arr
