import os
import numpy as np
import logging

LOG_FILENAME = '/tmp/logging_example.out'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)
log = logging.getLogger('MET09')

# create filehandler and set level to debug
ch = logging.FileHandler(filename = LOG_FILENAME)
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter("[%(levelname)s: %(asctime)s : %(name)s] %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
log.addHandler(ch)


from satellite import *
import msgpp_config
import time_utils


os.environ['SAFNWC'] = msgpp_config.MSG_DIR
os.environ['SAFNWC_BIN'] = msgpp_config.MSG_DIR+"/bin"
os.environ['SAFNWC_LIB'] = msgpp_config.MSG_DIR+"/lib"
os.environ['PATH'] = os.environ['PATH']+":"+os.environ['SAFNWC_BIN']
os.environ['LD_LIBRARY_PATH'] = os.environ['LD_LIBRARY_PATH']+":"+os.environ['SAFNWC_LIB']
os.environ['BUFR_TABLES'] = os.environ['SAFNWC']+"/src/bufr_000360/bufrtables/"
os.environ['LOCAL_DEFINITION_TEMPLATES'] = os.environ['SAFNWC']+"/src/gribex_000360/gribtemplates/"


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
                            ["HRVIS",(0.50,np.nan,0.90),1000]]

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
        
        _channels = []

        if channels is None:
            for ch in self.channels:
                _channels.append(ch.name)

        elif(isinstance(channels,list) or
             isinstance(channels,tuple)):
            for ch in channels:
                try:
                    _channels.append(self[ch][0].name)
                except TypeError:
                    log.error("Channel "+str(ch)+" could not be loaded.")
        else:
            raise TypeError("Channels must be a list or a tuple of names!")
        
        
        data = py_msg.get_channels(time_utils.time_string(self.time_slot), 
                                   self.area, 
                                   _channels,
                                   False)
        for ch in data:
            self[ch][0]._add_data(np.ma.array(data[ch]["CAL"], 
                                              mask = data[ch]["MASK"]))
        
if __name__ == "__main__":
    import datetime
    time_slot = datetime.datetime(2009,10,8,14,30)
    a = MeteoSatSeviriSnapshot(area = "EuropeCanary", time_slot = time_slot)
    print a[0.0]
    a.load([0.0,6.2])
    print "loading done"
    print a[0.6]
    print a[6.2]
