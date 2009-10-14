


class SatelliteChannel(object):
    
    data = None
    """Channel data."""

    name = None
    """Name of the channel."""

    wavelength_range = None
    """Operationnal wavelength range of the channel"""

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

    def __cmp__(self,y):
        return cmp((self.wavelength_range[1] - self.wavelength_range[0]) -
                   (y.wavelength_range[1] - y.wavelength_range[0]),
                   0)

class SatelliteInstrument(object):
    
    channels = []

    def __getitem__(self, key):
        if(isinstance(key, float)):
            channels = filter(lambda channel: 
                              channel.wavelength_range[0] <= key and 
                              channel.wavelength_range[1] >= key, 
                              self.channels)
            if(len(channels) >= 1):
                channels = sorted(channels)
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
            return None
        
class SatelliteSnapshot(SatelliteInstrument):

    time_slot = None
    area = None


class MeteoSatSeviriData(SatelliteSnapshot):
    
    def load(self, channels = None):
        data = py_msg.get_all_channels(time_utils.time_string(time_slot), 
                                       self.area, 
                                       self._load_rad)
        
        
