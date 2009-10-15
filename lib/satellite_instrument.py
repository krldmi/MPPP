


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
        return cmp(self.wavelength_range[1],y.wavelength_range[1])


    def __repr__(self):
        return ("'%s: lambda (%.3f,%.3f,%.3f)um, shape %s, resolution %sm'"%
                (self.name, 
                 self.wavelength_range[0], 
                 self.wavelength_range[1], 
                 self.wavelength_range[2], 
                 self.shape, 
                 self.resolution))

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
                                  cmp(abs(ch1.wavelength_range[1]-key),
                                      abs(ch2.wavelength_range[1]-key)))

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
            raise IndexError("Malformed key.")
    

class SatelliteSnapshot(SatelliteInstrument):

    time_slot = None
    area = None

    def __init__(self, time_slot = None, area = None):
        self.time_slot = time_slot
        self.area = area



meteosat_seviri_channels = [["VIS06",(0.56,0.635,0.71),3000],
                            ["VIS08",(0.74,0.81,0.88),3000],
                            ["IR16",(1.50,1.64,1.78),3000],
                            ["IR39",(3.48,3.92,4.36),3000],
                            ["WV62",(5.35,6.25,7.15),3000],
                            ["WV73",(6.85,7.35,7.85),3000],
                            ["IR87",(8.30,8.70,9.10),3000],
                            ["IR97",(9.38,9.66,9.94),3000],
                            ["IR108",(9.80,10.80,11.80),3000],
                            ["IR120",(11.00,12.00,13.00),3000],
                            ["IR134",(12.40,13.40,14.40),3000],
                            ["HRVIS",(0.50,0.75,0.90),1000]]

class MeteoSatSeviriSnapshot(SatelliteSnapshot):
    
    def __init__(self,*args,**kwargs):
        super(MeteoSatSeviriSnapshot,self).__init__(*args,**kwargs)
        self.channels = [None] * len(meteosat_seviri_channels)
        
        i = 0
        for name, w_range, resolution in meteosat_seviri_channels:
            self.channels[i] = SatelliteChannel(name = name,
                                                wavelength_range = w_range,
                                                resolution = resolution)
            i = i + 1
            
        

    def load(self, channels = None):
        import py_msg
        if channels is None:
            channels = []
            for ch in self.channels:
                channels.append(ch.name)

        if not isinstance(channels,list):
            raise ValueError("Channels must be a list or a tuple of names!")
        
        data = py_msg.get_all_channels(time_utils.time_string(time_slot), 
                                       self.area, 
                                       self._load_rad)
        
        
def sattest():
    a = MeteoSatSeviriSnapshot()
