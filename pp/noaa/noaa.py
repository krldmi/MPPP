"""This is the main module for noaa handling.
"""


import logging
import numpy as np
import ConfigParser
import os.path
import glob

from pp.satellite.satellite import SatelliteSnapshot, SatelliteChannel
import avhrr
from pp.noaa import BASE_PATH


CONF = ConfigParser.ConfigParser()
CONF.read(os.path.join(BASE_PATH, "etc", "noaa.cfg"))

L1B_DIR = CONF.get('dirs_in', 'l1b_dir')

LOG = logging.getLogger("pp.noaa")


NOAA_AVHRR = [["1", (0.58, 0.635, 0.68), 1090],
              ["2", (0.725, 0.81, 1.00), 1090],
              ["3A", (1.58, 1.61, 1.64), 1090],
              ["3B", (3.55, 3.74, 3.93), 1090],
              ["4", (10.30, 10.80, 11.30), 1090],
              ["5", (11.50, 12.00, 12.50), 1090]]

AVHRR_DIR = "/local_disk/data/pps/import/PPS_data/remapped"

class NoaaAvhrrSnapshot(SatelliteSnapshot):
    """A snapshot of Noaa's avhrr instrument.
    """

    def __init__(self, *args, **kwargs):
        super(NoaaAvhrrSnapshot, self).__init__(*args, **kwargs)

        self.satname = "noaa"
        self.number = kwargs.get("number", 0)
        self.channels = []
        
        for name, w_range, resolution in NOAA_AVHRR:
            self.channels.append(SatelliteChannel(name = name,
                                                  wavelength_range = w_range,
                                                  resolution = resolution))
            
    def load(self, channels = None):
        """Load data into the *channels*. Channels* is a list or a tuple
        containing channels we will load data into. If None, all channels are
        loaded.
        """

        
        if self.number != 0:
            number_string = str(self.number)
        else:
            number_string = "??"
        filename = (L1B_DIR+"/noaa"+number_string+
                    "_%Y%m%d_%H%M_?????/hrpt_noaa"+
                    number_string+"_%Y%m%d_%H%M_?????.l1b")

        file_list = glob.glob(self.time_slot.strftime(filename))

        if len(file_list) != 1:
            raise IOError("More than one l1b file matching!")

        avh = avhrr.avhrr(file_list[0])
        avh.get_unprojected()
        instrument_data = avh.build_raw()

        available_channels = set([])
        data_channels = {}
        _channels = set([])
        
        for chn in instrument_data.data:
            channel_name = chn.info.info["channel_id"][3:].upper()
            available_channels |= set([channel_name])
            data_channels[channel_name] = chn.data
        
        if channels is None:
            for chn in NOAA_AVHRR:
                _channels |= set([chn[0]])

        elif(isinstance(channels, (list, tuple, set))):
            for chn in channels:
                try:
                    _channels |= set([self[chn].name])
                except KeyError:
                    LOG.warning("Channel "+str(chn)+" not found,"
                                "thus not loaded.")
        else:
            raise TypeError("Channels must be a list/"
                            "tuple/set of channel keys!")
                

        for chn in _channels:
            if chn in available_channels:
                self[chn].add_data(np.ma.array(data_channels[chn]))
            else:
                LOG.warning("Channel "+str(chn)+" not available,"
                            "thus not loaded.")
            
        

