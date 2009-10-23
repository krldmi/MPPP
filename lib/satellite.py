import numpy as np


class SatelliteChannel(object):
    
    data = None
    """Channel data."""

    name = None
    """Name of the channel."""

    wavelength_range = None
    """Operationnal wavelength range of the channel, in micrometers"""

    shape = None
    """Shape of the channel data."""

    resolution = 0
    """Channel resolution, in meters."""

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

    def __cmp__(self,y):
        if np.isnan(self.wavelength_range[1]):
            return 1
        elif np.isnan(y.wavelength_range[1]):
            return -1
        else:
            return cmp(self.wavelength_range[1],y.wavelength_range[1])

    def __repr__(self):
        return ("'%s: lambda (%.3f,%.3f,%.3f)um, shape %s, resolution %sm'"%
                (self.name, 
                 self.wavelength_range[0], 
                 self.wavelength_range[1], 
                 self.wavelength_range[2], 
                 self.shape, 
                 self.resolution))
    
    def _add_data(self,data):
        self.data = data
        self.shape = data.shape

def _key_ch_cmp(x,y,key):
    if np.isnan(y.wavelength_range[1]):
        return -1
    elif np.isnan(x.wavelength_range[1]):
        return 1
    else:
        return cmp(x.wavelength_range[1] - key,
                   y.wavelength_range[1] - key)

class SatelliteInstrument(object):
    
    channels = []

    def __init__(self):
        self.channels = []

    def __getitem__(self, key):
        if(isinstance(key, float)):
            channels = filter(lambda channel: 
                              channel.wavelength_range[0] <= key and 
                              channel.wavelength_range[2] >= key, 
                              self.channels)
            if(len(channels) >= 1):
                channels = sorted(channels,
                                  lambda ch1,ch2:
                                  _key_ch_cmp(ch1,ch2,key))

                return channels
            else:
                return None
        elif(isinstance(key,str)):
            channels = filter(lambda channel: 
                              channel.name == key, 
                              self.channels)
            if(len(channels) >= 1):
                channels = sorted(channels)
                return channels
            else:
                return None
        elif(isinstance(key,int)):
            channels = filter(lambda channel: 
                              channel.resolution == key, 
                              self.channels)
            if(len(channels) >= 1):
                channels = sorted(channels)
                return channels
            else:
                return None
        elif(isinstance(key, tuple) or
             isinstance(key, list)):
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

    time_slot = None
    area = None

    def __init__(self, time_slot = None, area = None):
        self.time_slot = time_slot
        self.area = area



