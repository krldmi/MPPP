"""This module implements the meteosat 09 geostationnary satellite and
its Seviri instrument.
"""

import os
import numpy as np
import logging
import logging.config
import glob

from msgpp_config import APPLDIR
import py_msg
from satellite import SatelliteSnapshot, SatelliteChannel
import geo_image
import msgpp_config
import time_utils
import msg_ctype
import msg_ctth
from msg_ctype2radar import NordRadCType

logging.config.fileConfig(APPLDIR+"/etc/logging.conf")
LOG = logging.getLogger("pp.meteosat09")

os.environ['SAFNWC'] = msgpp_config.MSG_DIR
os.environ['SAFNWC_BIN'] = msgpp_config.MSG_DIR+"/bin"
os.environ['SAFNWC_LIB'] = msgpp_config.MSG_DIR+"/lib"
os.environ['PATH'] = os.environ['PATH']+":"+os.environ['SAFNWC_BIN']
os.environ['LD_LIBRARY_PATH'] = (os.environ['LD_LIBRARY_PATH']+
                                 ":"+os.environ['SAFNWC_LIB'])
os.environ['BUFR_TABLES'] = (os.environ['SAFNWC']+
                             "/src/bufr_000360/bufrtables/")
os.environ['LOCAL_DEFINITION_TEMPLATES'] = (os.environ['SAFNWC']+
                                            "/src/gribex_000360/gribtemplates/")

MET09_SEVIRI = [["VIS06", (0.56, 0.635, 0.71), 3000],
                ["VIS08", (0.74, 0.81, 0.88), 3000],
                ["IR16", (1.50, 1.64, 1.78), 3000],
                ["IR39", (3.48, 3.92, 4.36), 3000],
                ["WV62", (5.35, 6.25, 7.15), 3000],
                ["WV73", (6.85, 7.35, 7.85), 3000],
                ["IR87", (8.30, 8.70, 9.10), 3000],
                ["IR97", (9.38, 9.66, 9.94), 3000],
                ["IR108", (9.80, 10.80, 11.80), 3000],
                ["IR120", (11.00, 12.00, 13.00), 3000],
                ["IR134", (12.40, 13.40, 14.40), 3000],
                ["HRVIS", (0.50, np.nan, 0.90), 1000]]

class MeteoSatSeviriSnapshot(SatelliteSnapshot):
    """This class implements the MeteoSat snapshot as captured by the seviri
    instrument. It's constructor accepts the same arguments as
    :class:`SatelliteSnapshot`.
    """
    
    def __init__(self, *args, **kwargs):
        super(MeteoSatSeviriSnapshot, self).__init__(*args, **kwargs)
        self.channels = [None] * len(MET09_SEVIRI)
        
        i = 0
        for name, w_range, resolution in MET09_SEVIRI:
            self.channels[i] = SatelliteChannel(name = name,
                                                wavelength_range = w_range,
                                                resolution = resolution)
            i = i + 1
            
        

    def load(self, channels = None):
        """Load data into the *channels*. *Channels* is a list or a tuple
        containing channels we will load data into. If None, all channels are
        loaded.
        """
        LOG.info("Loading channels...")
        _channels = set([])

        do_correct = False

        if channels is None:
            for chn in self.channels:
                _channels |= set([chn.name])

        elif(isinstance(channels, (list, tuple, set))):
            for chn in channels:
                if chn == "_IR39Corr":
                    do_correct = True
                elif chn == "CloudType":
                    if chn not in self.channels:
                        self.channels.append(self.cloudtype_channel())
                elif chn == "CTTH":
                    if chn not in self.channels:
                        self.channels.append(self.ctth_channel())
                else:
                    try:
                        _channels |= set([self[chn].name])
                    except KeyError:
                        LOG.warning("Channel "+str(chn)+" not found,"
                                    "thus not loaded.")
        else:
            raise TypeError("Channels must be a list/"
                            "tuple/set of channel keys!")
        
        if do_correct:
            for chn in self.co2corr.prerequisites:
                _channels |= set([self[chn].name])
        
        data = py_msg.get_channels(time_utils.time_string(self.time_slot), 
                                   self.area, 
                                   list(_channels),
                                   False)

        for chn in data:
            self[chn].add_data(np.ma.array(data[chn]["CAL"], 
                                               mask = data[chn]["MASK"]))

        if do_correct:
            self.channels.append(self.co2corr())
        LOG.info("Loading channels done.")

    def ctth_channel(self):
        """Create and return a ctth channel.
        """
        time_string = time_utils.time_string(self.time_slot)

        prefix = ("SAFNWC_MSG?_CTTH_%s_%s"%(time_string, self.area))

        msgctth_filename = None
        for ext in msgpp_config.MSG_PGE_EXTENTIONS:
            match_str = ("%s/%s.%s"
                         %(msgpp_config.CTTHDIR_IN, prefix, ext))
            LOG.info("file-match: %s"%match_str)
            flist = glob.glob(match_str)

            if len(flist) > 1:
                LOG.error("More than one matching input file: N = %d"
                          %len(flist))
                raise RuntimeError("Cannot choose input CTTH file.")
            elif len(flist) == 0:
                LOG.warning("No matching input file.")
            else:
                # File found:
                LOG.info("MSG CTTH file found: %s"%flist[0])
                msgctth_filename = flist[0]
                break
             
        if msgctth_filename is not None:
            # Read the MSG file if not already done...
            LOG.info("Read MSG CTTH file: %s"%msgctth_filename)
            ctth = msg_ctth.MsgCTTH(resolution = 3000)
            ctth.read_msgCtth(msgctth_filename)
            LOG.debug("MSG CTTH area: %s"%ctth.region_name)
            return ctth
        else:
            LOG.error("No MSG CT input file found!")
            raise RuntimeError("No input CTTH file.")

    def cloudtype_channel(self):
        """Create and return a cloudtype channel.
        """
        time_string = time_utils.time_string(self.time_slot)

        prefix = ("SAFNWC_MSG?_CT___%s_%s"%(time_string, self.area))
        
        msgctype_filename = None
        
        for ext in msgpp_config.MSG_PGE_EXTENTIONS:
            match_str = ("%s/%s.%s"%(msgpp_config.CTYPEDIR_IN, prefix, ext))
            LOG.info("file-match: %s"%match_str)
            flist = glob.glob(match_str)

            if len(flist) > 1:
                LOG.error("More than one matching input file: N = %d"
                          %len(flist))
                raise RuntimeError("Cannot choose input CType file.")
            elif len(flist) == 0:
                LOG.warning("No matching input file")
            else:
                # File found:
                LOG.info("MSG CT file found: %s"%flist[0])
                msgctype_filename = flist[0]
                break

        if msgctype_filename is not None:
            LOG.info("Read MSG CT file: %s"%msgctype_filename)
            ctype = msg_ctype.MsgCloudType(resolution = 3000)
            ctype.read_msg_ctype(msgctype_filename)
            LOG.debug("MSG CT area: %s"%ctype.region_name)
            return ctype
        else:
            LOG.error("No MSG CT input file found!")
            raise RuntimeError("No input CType file.")


    def co2corr(self):
        """CO2 correction of the brightness temperature of the MSG 3.9um
        channel:
        
        T4_CO2corr = (BT(IR3.9)^4 + Rcorr)^0.25
        Rcorr = BT(IR10.8)^4 - (BT(IR10.8)-dt_CO2)^4
        dt_CO2 = (BT(IR10.8)-BT(IR13.4))/4.0
        """
        try:
            self.check_channels(3.9, 10.8, 13.4)
        except RuntimeError:
            LOG.warning("CO2 correction not performed, channel data missing.")
            return



        bt039 = self[3.9].data
        bt108 = self[10.8].data
        bt134 = self[13.4].data
        
        dt_co2 = (bt108-bt134)/4.0
        rcorr = bt108 ** 4 - (bt108-dt_co2) ** 4
        
        
        t4_co2corr = bt039 ** 4 + rcorr
        t4_co2corr = np.ma.where(t4_co2corr > 0.0, t4_co2corr, 0)
        t4_co2corr = t4_co2corr ** 0.25
        
        ir39corr = SatelliteChannel(name = "_IR39Corr",
                                    wavelength_range = 
                                    self[3.9].wavelength_range,
                                    resolution = 
                                    self[3.9].resolution,
                                    data = t4_co2corr)

        

        return ir39corr

    co2corr.prerequisites = set([3.9, 10.8, 13.4])

    def cloudtop(self):
        """Make a Cloudtop RGB image composite from Seviri channels.
        """
        self.check_channels("_IR39Corr", 10.8, 12.0)

        ch1 = -self["_IR39Corr"].data
        ch2 = -self[10.8].data
        ch3 = -self[12.0].data

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB")

        img.enhance(stretch = (0.005, 0.005))

        return img
    
    cloudtop.prerequisites = set(["_IR39Corr", 10.8, 12.0])

    def night_fog(self):
        """Make a Night Fog RGB image composite from Seviri channels.
        """
        self.check_channels("_IR39Corr", 10.8, 12.0)

        ch1 = self[12.0].data - self[10.8].data
        ch2 = self[10.8].data - self["_IR39Corr"].data
        ch3 = self[10.8].data
        
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB",
                                 crange = ((-4, 2),
                                           (0, 6),
                                           (243, 293)))
        
        img.enhance(gamma = (1.0, 2.0, 1.0))
        img.clip()

# Old version, without co2 correction
#        im.enhance(gamma = (1.0, 2.0, 1.0))
#        im.clip()
#        im.enhance(stretch = "crude")
        return img

    night_fog.prerequisites = set(["_IR39Corr", 10.8, 12.0])


    def hr_overview(self):
        """Make a High Resolution Overview RGB image composite from Seviri
        channels.
        """
        self.check_channels(0.6, 0.8, 10.8, "HRVIS")

        ch1 = self[0.6].check_range()
        ch2 = self[0.8].check_range()
        ch3 = -self[10.8].data

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 mode = "RGB")

        img.enhance(stretch = "crude")
        img.enhance(gamma = [1.6, 1.6, 1.1])
        
        luminance = geo_image.GeoImage((self["HRVIS"].data),
                                       self.area,
                                       self.time_slot,
                                       mode = "L")

        luminance.enhance(stretch = "crude")
        luminance.enhance(gamma = 2.0)

        img.replace_luminance(luminance.channels[0])
        
        return img

    hr_overview.prerequisites = set(["HRVIS", 0.6, 0.8, 10.8])

    def get_lat_lon(self, resolution):
        """Get the latitude and longitude grids of the current region for the
        given *resolution*.
        """
        if not isinstance(resolution, int):
            raise TypeError("Resolution must be an integer number of meters.")
        channel = self[0.6, resolution]
        return py_msg.lat_lon_from_region(self.area, channel.name)

    def cloudtype(self):
        """Return the cloudtype.
        """
        return self["CloudType"]
    
    cloudtype.prerequisites = set(["CloudType"])

    def nordrad(self):
        """Return the cloudtype in NordRad format.
        """
        datestr = self.time_slot.strftime("%Y%m%d%H%M")
        return NordRadCType(self["CloudType"], datestr)
    
    nordrad.prerequisites = set(["CloudType"])

    def ctth(self):
        """Return the ctth.
        """
        return self["CTTH"]
    
    ctth.prerequisites = set(["CTTH"])
    

def _dummy():
    """dummy function.
    """
    return None

_dummy.prerequisites = set([])


import Queue
import threading

queue = Queue.Queue()
          
class ThreadSave(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, myqueue):
        threading.Thread.__init__(self)
        self.queue = myqueue

    def run(self):
        """Run the thread.
        """
        while True:
            tosave = self.queue.get()
            tosave[0].save(tosave[1])
            self.queue.task_done()



if __name__ == "__main__":
    import datetime
    T = datetime.datetime(2009, 10, 8, 14, 30)
    #A = MeteoSatSeviriSnapshot(area = "EuropeCanary", time_slot = T)
    #A.load([0.6, 0.8, 10.8, 6.2, 7.3, 9.7, 38.0])
    #A.load(A.red_snow.prerequisites)
    #print "loading done"
    #print A[0.6]
    #print A[0.8]
    #print A[10.8]
    #print A.overview.prerequisites
    #A.wv_low().save("./test.png")
    #A.red_snow().save("./test.png")
    #A.overview().save("./test.png")

    from products import PRODUCTS

    metsat_data = MeteoSatSeviriSnapshot(time_slot = T, area = "EuropeCanary")
    
    cases = {
        "overview": metsat_data.overview,
        "natural": metsat_data.natural,
        "fog": metsat_data.fog,
        "nightfog": metsat_data.night_fog,
        "convection": metsat_data.convection,
        "airmass": metsat_data.airmass,
        "ir9": metsat_data.ir108,
        "wv_low": metsat_data.wv_low,
        "wv_high": metsat_data.wv_high,
        "greensnow": metsat_data.green_snow,
        "redsnow": metsat_data.red_snow,
        "cloudtop": metsat_data.cloudtop,
        "hr_overview": metsat_data.hr_overview,
        "PGE02": metsat_data.pge02,
        "PGE02b": metsat_data.pge02b,
        "PGE02bj": metsat_data.pge02b_with_overlay,
        "PGE02c": metsat_data.pge02c,
        "PGE02cj": metsat_data.pge02c_with_overlay,
        "PGE02d": metsat_data.pge02d,
        "PGE02e": metsat_data.pge02e,
        "PGE03": metsat_data.pge03,
        "CtypeHDF": metsat_data.cloudtype,
        "NordRad": metsat_data.nordrad,
        "CtthHDF": metsat_data.ctth
        }

    _channels = set([])


    t = ThreadSave(queue)
    t.setDaemon(True)
    t.start()


    for akey in PRODUCTS:
        for pkey in PRODUCTS[akey]:
            fun = cases.get(pkey, _dummy)
            _channels |= fun.prerequisites

    metsat_data.load(_channels)
    
    LOG.debug("Loaded %s"%metsat_data.loaded_channels())

    for akey in PRODUCTS:
        if akey == "globe":
            continue
        _channels = set([])
        for pkey in PRODUCTS[akey]:
            LOG.debug("Getting prerequisites for %s."%pkey)
            fun = cases.get(pkey, _dummy)
            _channels |= fun.prerequisites
        local_data = metsat_data.project(akey, _channels)
        cases = {
            "overview": local_data.overview,
            "natural": local_data.natural,
            "fog": local_data.fog,
            "nightfog": local_data.night_fog,
            "convection": local_data.convection,
            "airmass": local_data.airmass,
            "ir9": local_data.ir108,
            "wv_low": local_data.wv_low,
            "wv_high": local_data.wv_high,
            "greensnow": local_data.green_snow,
            "redsnow": local_data.red_snow,
            "cloudtop": local_data.cloudtop,
            "hr_overview": local_data.hr_overview,
            "PGE02": local_data.pge02,
            "PGE02b": local_data.pge02b,
            "PGE02bj": local_data.pge02b_with_overlay,
            "PGE02c": local_data.pge02c,
            "PGE02cj": local_data.pge02c_with_overlay,
            "PGE02d": local_data.pge02d,
            "PGE02e": local_data.pge02e,
            "PGE03": local_data.pge03,
            "CtypeHDF": local_data.cloudtype,
            "NordRad": local_data.nordrad,
            "CtthHDF": local_data.ctth
            }

        for pkey in PRODUCTS[akey]:
            LOG.debug("Getting prerequisites for %s."%pkey)
            fun = cases.get(pkey, _dummy)

            LOG.info("Running %s..."%pkey)
            rgb = fun()
            LOG.info("Done running %s."%pkey)
            if rgb is not None:
                for filename in PRODUCTS[akey][pkey]:
                    if(isinstance(filename, tuple) and
                       len(filename) == 2 and
                       isinstance(rgb, geo_image.GeoImage)):
                        filename0 = T.strftime(filename[0])
                        filename1 = T.strftime(filename[1])
                        LOG.info("Saving to %s."%(filename0))
                        LOG.info("Saving to %s."%(filename1))
                        rgb.double_save(filename0, filename1)
                        LOG.info("Savings done.")
                    else:
                        filename0 = T.strftime(filename)
                        LOG.info("Saving to %s."%(filename0))
                        queue.put((rgb, filename0))
                        #rgb.save(filename0)
                        LOG.info("Saving done.")
    queue.join()
