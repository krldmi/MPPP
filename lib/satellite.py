"""This module defines the basic interface for satellites, satellite
instruments, and satellite snapshots.
"""
import numpy as np


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

class SatelliteInstrument(object):
    """This is the satellite instrument class.
    """
    channels = []

    def __init__(self):
        self.channels = []

    def __getitem__(self, key):
        if(isinstance(key, float)):
            channels = [chn for chn in self.channels
                        if(chn.wavelength_range[0] <= key and
                           chn.wavelength_range[2] >= key)]
            return sorted(channels,
                          lambda ch1,ch2:
                              ch1.__cmp__(ch2,key))

        elif(isinstance(key, str)):
            channels = [chn for chn in self.channels
                        if chn.name == key]
            return sorted(channels)

        elif(isinstance(key, int)):
            channels = [chn for chn in self.channels
                        if chn.resolution == key]
            return sorted(channels)

        elif(isinstance(key, (tuple, list))):
            if(len(key) > 1):
                dummy_instance = SatelliteInstrument()
                channels = self[key[0]]
                if channels is None:
                    return None
                dummy_instance.channels = channels
                channels = dummy_instance[key[1:]]
                return channels
            else:
                return self[key[0]]
        else:
            raise KeyError("Malformed key.")
    

class SatelliteSnapshot(SatelliteInstrument):
    """This is the satellite snapshot class.
    """
    time_slot = None
    area = None

    def __init__(self, time_slot = None, area = None, *args, **kwargs):
        super(SatelliteSnapshot, self).__init__(*args, **kwargs)
        self.time_slot = time_slot
        self.area = area


