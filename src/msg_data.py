"""This module acts as an interface to the MSG software package. In
particular, it allows the retrieval of data from raw Seviri data.
"""

import os
import msgpp_config

os.environ['SAFNWC'] = os.environ['HOME']+"/usr/src/msg"
os.environ['SAFNWC_BIN'] = os.environ['SAFNWC']+"/bin"
os.environ['SAFNWC_LIB'] = os.environ['SAFNWC']+"/bin"
os.environ['PATH'] = os.environ['PATH']+":"+os.environ['SAFNWC_BIN']
os.environ['LD_LIBRARY_PATH'] = os.environ['LD_LIBRARY_PATH']+":"+os.environ['SAFNWC_LIB']
os.environ['BUFR_TABLES'] = os.environ['SAFNWC']+"/src/bufr_000360/bufrtables/"
os.environ['LOCAL_DEFINITION_TEMPLATES'] = os.environ['SAFNWC']+"/src/gribex_000360/gribtemplates/"

import Image
import numpy
import copy
import py_msg
import area
import time_utils
import msg_coverage


class MSGSeviriChannels:
    """This class defines a container to Seviri data. It holds 12
    slots for the 12 Seviri channels.
    """
    def __init__(self, time_slot, area_id, hr = True,rad = True):
        area_filename = "safnwc_" + area_id + ".cfg"
        self.time_slot = time_slot
        self.area_id = area_id
        self.nb_channels = 12
        _data = py_msg.get_all_channels(time_utils.time_string(time_slot), area_filename, rad)
        if(hr):
            _hrdata = MSGChannel(time_slot, area_id, "HRVIS",rad = rad)
        else:
            _hrdata = None
        self.channels = [MSGChannel(time_slot, area_id, "VIS06",
                                    {"RAD":_data["RAD"][0],
                                     "CAL":_data["CAL"][0],
                                     "MASK":_data["MASK"][0]}),
                         MSGChannel(time_slot, area_id, "VIS08",
                                    {"RAD":_data["RAD"][1],
                                     "CAL":_data["CAL"][1],
                                     "MASK":_data["MASK"][1]}),
                         MSGChannel(time_slot, area_id, "IR16",
                                    {"RAD":_data["RAD"][2],
                                     "CAL":_data["CAL"][2],
                                     "MASK":_data["MASK"][2]}),
                         MSGChannel(time_slot, area_id, "IR39",
                                    {"RAD":_data["RAD"][3],
                                     "CAL":_data["CAL"][3],
                                     "MASK":_data["MASK"][3]}),
                         MSGChannel(time_slot, area_id, "WV62",
                                    {"RAD":_data["RAD"][4],
                                     "CAL":_data["CAL"][4],
                                     "MASK":_data["MASK"][4]}),
                         MSGChannel(time_slot, area_id, "WV73",
                                    {"RAD":_data["RAD"][5],
                                     "CAL":_data["CAL"][5],
                                     "MASK":_data["MASK"][5]}),
                         MSGChannel(time_slot, area_id, "IR87",
                                    {"RAD":_data["RAD"][6],
                                     "CAL":_data["CAL"][6],
                                     "MASK":_data["MASK"][6]}),
                         MSGChannel(time_slot, area_id, "IR97",
                                    {"RAD":_data["RAD"][7],
                                     "CAL":_data["CAL"][7],
                                     "MASK":_data["MASK"][7]}),
                         MSGChannel(time_slot, area_id, "IR108",
                                    {"RAD":_data["RAD"][8],
                                     "CAL":_data["CAL"][8],
                                     "MASK":_data["MASK"][8]}),
                         MSGChannel(time_slot, area_id, "IR120",
                                    {"RAD":_data["RAD"][9],
                                     "CAL":_data["CAL"][9],
                                     "MASK":_data["MASK"][9]}),
                         MSGChannel(time_slot, area_id, "IR134",
                                    {"RAD":_data["RAD"][10],
                                     "CAL":_data["CAL"][10],
                                     "MASK":_data["MASK"][10]}),
                         _hrdata]

    def __getitem__(self,key):
        if(key == "1" or key == "VIS06" or key == 1):
            return self.channels[0]
        if(key == "2" or key == "VIS08" or key == 2):
            return self.channels[1]
        if(key == "3" or key == "IR16" or key == 3):
            return self.channels[2]
        if(key == "4" or key == "IR39" or key == 4):
            return self.channels[3]
        if(key == "5" or key == "WV62" or key == 5):
            return self.channels[4]
        if(key == "6" or key == "WV73" or key == 6):
            return self.channels[5]
        if(key == "7" or key == "IR87" or key == 7):
            return self.channels[6]
        if(key == "8" or key == "IR97" or key == 8):
            return self.channels[7]
        if(key == "9" or key == "IR108" or key == 9):
            return self.channels[8]
        if(key == "10" or key == "IR120" or key == 10):
            return self.channels[9]
        if(key == "11" or key == "IR134" or key == 11):
            return self.channels[10]
        if(key == "12" or key == "HRVIS" or key == 12):
            return self.channels[11]

    def project(self,dest_area):
        """Make a projected copy of the object to
        *dest_area*. Available areas are defined in the main
        configuration file.
        """
        if(dest_area == self.area_id):
            return self

        res = copy.copy(self)
        coverage = msg_coverage.SatProjCov(self.area_id, dest_area, False)
        res.area_id = dest_area
        res.channels = []
        for ch in self.channels:
            if(ch["RAD"] is not None or ch["CAL"] is not None):
                if(ch.channel_id == "HRVIS"):
                    hr_coverage = msg_coverage.SatProjCov(self.area_id, dest_area, True)
                    res.channels.append(ch.project(dest_area,hr_coverage))
                else:
                    res.channels.append(ch.project(dest_area,coverage))
            else:
                res.channels.append(None)
        return res

    def strip(self,key,shift = True):
        """Strip the channels for a given *key* to a list. If *shift*
        is true the data arrays are available in the range
        [1:nb_channels], and in the range [0:nb_channels - 1]
        otherwise.
        """
        ch = map(_getkey,self.channels,[key,key,key,key,key,key,key,key,key,key,key,key])
        if shift:
            ch.insert(0,None)
        return ch

def _getkey(item,key):
    return item[key]

class MSGChannel:
    def __init__(self, time_slot, area_id, channel_id, data = None, rad = True):
        area_filename = "safnwc_" + area_id + ".cfg"
        self.time_slot = time_slot
        self.area_id = area_id
        self.channel_id = channel_id
        if (data is None):
            data = py_msg.get_channel(time_utils.time_string(time_slot), 
                                      area_filename, 
                                      channel_id, 
                                      rad)

        if((data["RAD"] is None) and (data["CAL"] is None)):
            self._rad = None
            self._refl = None
            self._bt = None
            return
        
        if(data["RAD"] is None):
            self._rad = None
        else:
            self._rad = numpy.ma.array(data["RAD"],
                                       mask=data["MASK"],
                                       fill_value = py_msg.missing_value())

        if (channel_id == "HRVIS" or
            channel_id == "VIS06" or
            channel_id == "VIS08" or
            channel_id == "IR16" or
            channel_id == "1" or
            channel_id == "2" or
            channel_id == "3" or
            channel_id == "12"):
            self._refl = numpy.ma.array(data["CAL"],
                                        mask = data["MASK"],
                                        fill_value = py_msg.missing_value())
            self._bt = None
        else:
            self._bt = numpy.ma.array(data["CAL"],
                                      mask=data["MASK"],
                                      fill_value = py_msg.missing_value())
            self._refl = None

    def __getitem__(self,key):
        key = key.upper()
        if(key == "RAD"):
            comp = self._rad
        elif(key == "REFL"):
            comp = self._refl
        elif(key == "BT"):
            comp = self._bt
        elif(key == "CAL"):
            if(self._refl is not None):
                comp = self._refl
            else:
                comp = self._bt
        else:
            comp = None

        return comp

    def component(self,component, inverted = False):

        comp = self[component]

        if(comp is None):
            return None
        
        if(inverted):
            return comp.max() - comp.filled(comp.max())
        else:
            return comp.filled(comp.min())

    def reflectance(self,inverted = False):
            return self.component("REFL", inverted)

    def radiance(self,inverted = False):
        return self.component("RAD", inverted)

    def bt(self,inverted = False):
        return self.component("BT", inverted)

    def calibrated_data(self, inverted = False):
        return self.component("CAL", inverted)
   
    def project(self, dest_area, coverage = None):
        """Make a projected copy of the current channel onto
        *dest_area*. If *coverage* is povided it is used instead of
        computing it on the fly, usefull in case of multiple channels
        projected onto the same area.
        """
        if(dest_area == self.area_id):
            return self

        res = copy.copy(self)
        res.area_id = dest_area
        if(not coverage):
            if(channel_id == "HRVIS" or channel_id == "12"):
                coverage = msg_coverage.SatProjCov(self.area_id, dest_area, True)            
            else:
                coverage = msg_coverage.SatProjCov(self.area_id, dest_area, False)
        if(self._rad is not None):
            res._rad = coverage.project_array(self._rad)
        if(self._refl is not None):
            res._refl = coverage.project_array(self._refl)
        if(self._bt is not None):
            res._bt = coverage.project_array(self._bt)

        return res

# -----------------------------------------------------------------------------
# Test the current module

def normalizeArray(a,maxval):
    return numpy.array(numpy.round(((a-numpy.amin(a))/(numpy.amax(a)-numpy.amin(a)))*maxval),numpy.uint8)

     
if __name__ == "__main__":

    a = MSGSeviriChannels("200909141045","EuropeCanary")
    
    ch1 = a["1"].reflectance()
    ch2 = a["2"].reflectance()
    ch9 = a["9"].bt(inverted = True)
    ch12 = a["12"].reflectance()

    im1 = Image.fromarray(normalizeArray(ch1,255))
    im2 = Image.fromarray(normalizeArray(ch2,255))
    im9i = Image.fromarray(normalizeArray(ch9,255))
    im12 = Image.fromarray(normalizeArray(ch12,255))
    
    visir = Image.merge('RGB',(im1,im2,im9i));
    hrv = im12
    
    v = visir.convert('YCbCr').split()
    im = Image.merge('YCbCr',(hrv,v[1].resize(hrv.size),v[2].resize(hrv.size))).convert('RGB')
    
    im.show()

