#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009.

# SMHI,
# Folkborgsvägen 1,
# Norrköping, 
# Sweden

# Author(s):
 
#   Martin Raspaud <martin.raspaud@smhi.se>
#   Adam Dybbroe <adam.dybbroe@smhi.se>

# This file is part of the MPPP.

# MPPP is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# MPPP is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with MPPP.  If not, see <http://www.gnu.org/licenses/>.

"""This is the main module for noaa handling.
"""


import logging
import numpy as np
import ConfigParser
import os.path
import glob
import math

from pp.satellite.satellite import SatelliteSnapshot
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

class NoaaAvhrrSnapshot(SatelliteSnapshot):
    """A snapshot of Noaa's avhrr instrument.
    """

    def __init__(self, *args, **kwargs):

        self.channel_list = NOAA_AVHRR
        
        super(NoaaAvhrrSnapshot, self).__init__(*args, **kwargs)

        self.satname = "noaa"
        self.number = kwargs.get("number", 0)

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

        self.file = file_list[0]

        if self.number == 0:
            self.number = self.file[-26:-24]
            
        self.area = self.time_slot.strftime(str(self.number)+"_%Y%m%d%H%M")
        
    def load(self, channels = None):
        """Load data into the *channels*. Channels* is a list or a tuple
        containing channels we will load data into. If None, all channels are
        loaded.

        Note that with the current version of Ahamap (1.55), on which this
        library depends, it is not possible to load one channel at the time, so
        the user should read as many channels as needed at once.
        """
        super(NoaaAvhrrSnapshot, self).load(channels)
        
        avh = avhrr.avhrr(self.file)
        avh.get_unprojected()
        instrument_data = avh.build_raw()

        available_channels = set([])
        data_channels = {}
        
        for chn in instrument_data.data:
            channel_name = chn.info.info["channel_id"][3:].upper()
            available_channels |= set([channel_name])
            data_channels[channel_name] = chn.data
        
        for chn in self.channels_to_load:
            if chn in available_channels:
                if chn in ["1", "2", "3A"]:
                    gain = instrument_data.info["vis_gain"]
                    intercept = instrument_data.info["vis_intercept"]
                else:
                    gain = instrument_data.info["ir_gain"]
                    intercept = instrument_data.info["ir_intercept"]

                self[chn] = np.ma.array(data_channels[chn])
                np.ma.masked_equal(self[chn].data,
                                   instrument_data.info["missing_data"])
                np.ma.masked_equal(self[chn].data,
                                   instrument_data.info["nodata"])
                self[chn].data =  self[chn].data * gain + intercept
                
            else:
                LOG.warning("Channel "+str(chn)+" not available, not loaded.")
            
        self.lat = instrument_data.latdata / math.pi * 180
        self.lon = instrument_data.londata / math.pi * 180
        

    def get_lat_lon(self, resolution):
        """Get the latitude and longitude grids of the current region for the
        given *resolution*.
        """
        if not isinstance(resolution, int):
            raise TypeError("Resolution must be an integer number of meters.")

        return self.lat, self.lon
