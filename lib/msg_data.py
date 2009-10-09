"""This module acts as an interface to the MSG software package. In
particular, it allows the retrieval of data from raw Seviri data.
"""

import os
import msgpp_config

os.environ['SAFNWC'] = msgpp_config.MSG_DIR
os.environ['SAFNWC_BIN'] = msgpp_config.MSG_DIR+"/bin"
os.environ['SAFNWC_LIB'] = msgpp_config.MSG_DIR+"/lib"
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
import geo_image
import image_processing
import msg_ctype
import msg_ctth
import msg_communications
import glob
import pps_array2image
import smhi_safnwc_legends

MODULE_ID = "MSG DATA"

class MSGSeviriChannels:
    """This class defines a container to Seviri data. It holds 12
    slots for the 12 Seviri channels.
    """

    cloudtype = None
    ctth = None

    def __init__(self, time_slot, area_id, hr = True,rad = True):
        self.time_slot = time_slot
        self.area_id = area_id
        self.nb_channels = 12
        self._load_hr = hr
        self._load_rad = rad
        self.channels = [None,None,None,None,None,None,
                         None,None,None,None,None,None]
        self.cloudtype = None
        self.ctth = None


    def load(self,channels = "all"):
        """Load the data into the Seviri structure. *channels* can be
        specified, otherwise (or when set to "all") all the channels are
        loaded.
        """
        time_slot = self.time_slot
        area_id = self.area_id

        area_filename = "safnwc_" + area_id + ".cfg"

        if channels == "all":
            
            _data = py_msg.get_all_channels(time_utils.time_string(time_slot), 
                                            area_filename, 
                                            self._load_rad)
            if(self._load_hr):
                _hrdata = MSGChannel(time_slot, 
                                     area_id, 
                                     "HRVIS",
                                     rad = self._load_rad)
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

        else:
            # This is dirty. py_msg module should allow individual channel
            # selection on loading. -- Martin, 2009-10-08.
            for ch in channels:
                self.channels[ch-1] = MSGChannel(time_slot, 
                                               area_id, 
                                               ch, 
                                               rad = self._load_rad)
        self._co2corr_bt39
            
            

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
        if(key == "CAL" or key == "REFL" or key == "BT" or key == "RAD"):
            return self.strip(key)

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
            if(ch is not None and
               (ch["RAD"] is not None or 
                ch["CAL"] is not None)):
                if(ch.channel_id == "HRVIS" or
                   ch.channel_id == "12" or
                   ch.channel_id == 12):
                    hr_coverage = msg_coverage.SatProjCov(self.area_id, dest_area, True)
                    res.channels.append(ch.project(dest_area,hr_coverage))
                else:
                    res.channels.append(ch.project(dest_area,coverage))

            else:
                res.channels.append(None)

        if self.cloudtype is not None:
            res.cloudtype = self.cloudtype.project(coverage, dest_area)

        if self.ctth is not None:
            res.ctth = self.ctth.project(coverage, dest_area)

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

    def _co2corr_bt39(self):
        """CO2 correction of the brightness temperature of the MSG 3.9 um
        channel:
        
        T4_CO2corr = (BT(IR3.9)^4 + Rcorr)^0.25
        Rcorr = BT(IR10.8)^4 - (BT(IR10.8)-dt_CO2)^4
        dt_CO2 = (BT(IR10.8)-BT(IR13.4))/4.0
        
        """
        if(self[4] is None or
           self[9] is None or
           self[11] is None):
            msg_communications.msgwrite_log("WARNING","CO2 correction not performed, not enough channels loaded.",moduleid=MODULE_ID)
            return

        epsilon = 0.001
        bt039 = self[4]["BT"]
        bt108 = self[9]["BT"]
        bt134 = self[11]["BT"]
        
        dt_co2 = (bt108-bt134)/4.0
        a = bt108*bt108*bt108*bt108
        b = (bt108-dt_co2)*(bt108-dt_co2)*(bt108-dt_co2)*(bt108-dt_co2)
        
        Rcorr = a - b
        
        a = bt039*bt039*bt039*bt039
        x = numpy.where(a+Rcorr > 0.0,(a + Rcorr), 0)
                
        self.channels[3]._bt = x ** 0.25
    

    def load_cloudtype(self):
        """Load cloudtype information into the current object.
        """
        time_string = time_utils.time_string(self.time_slot)

        prefix="SAFNWC_MSG?_CT___%s_%s"%(time_string,
                                         self.area_id)
        
        msgctype_filename=None
        for ext in msgpp_config.MSG_PGE_EXTENTIONS:
            match_str = "%s/%s*%s"%(msgpp_config.CTYPEDIR_IN,prefix,ext)
            msg_communications.msgwrite_log("INFO","file-match: ",match_str,moduleid=MODULE_ID)
            flist = glob.glob(match_str)
            msgctype=None
            if len(flist) > 1:
                msg_communications.msgwrite_log("ERROR","More than one matching input file: N = ",len(flist),moduleid=MODULE_ID)
            elif len(flist) == 0:
                msg_communications.msgwrite_log("WARNING","No matching input file",moduleid=MODULE_ID)
            else:
                # File found:
                msg_communications.msgwrite_log("INFO","MSG CT file found: ",flist[0],moduleid=MODULE_ID)
                msgctype_filename = flist[0]
                break

        if msgctype_filename:
            # Read the MSG file if not already done...
            msg_communications.msgwrite_log("INFO","Read MSG CT file: ",msgctype_filename,moduleid=MODULE_ID)
            self.cloudtype = msg_ctype.msgCloudType()
            self.cloudtype.read_msgCtype(msgctype_filename)
        else:
            msg_communications.msgwrite_log("ERROR","No MSG CT input file found!",moduleid=MODULE_ID)
            self.cloudtype = None

    def save_cloudtype(self,filename):
        ctype = msg_ctype.msg_ctype2ppsformat(self.cloudtype)
        epshdf.write_cloudtype(filename, ctype, 6)

    def get_cloudtype(self):
        """Return the cloudtype structure.
        """
        if self.cloudtype is None:
            self.load_cloudtype
            
        return self.cloudtype

    def pps_cloudtype(self):
        """Return the cloudtype structure, in pps format.
        """
        if self.cloudtype is None:
            self.load_cloudtype
            
        return msg_ctype.msg_ctype2ppsformat(self.cloudtype)
        
    def load_ctth(self):
        """Load ctth information into the current object.
        """
        time_string = time_utils.time_string(self.time_slot)

        prefix="SAFNWC_MSG?_CTTH_%s_%s"%(time_string,
                                         self.area_id)
        msgctth_filename=None
        for ext in msgpp_config.MSG_PGE_EXTENTIONS:
            match_str = "%s/%s*%s"%(msgpp_config.CTTHDIR_IN,prefix,ext)
            msg_communications.msgwrite_log("INFO","file-match: ",match_str,moduleid=MODULE_ID)
            flist = glob.glob(match_str)
            msgctth=None
            if len(flist) > 1:
                msg_communications.msgwrite_log("ERROR","More than one matching input file: N = ",len(flist),moduleid=MODULE_ID)
            elif len(flist) == 0:
                msg_communications.msgwrite_log("WARNING","No matching input file",moduleid=MODULE_ID)
            else:
                # File found:
                msg_communications.msgwrite_log("INFO","MSG CTTH file found: ",flist[0],moduleid=MODULE_ID)
                msgctth_filename = flist[0]
                break
             
        if msgctth_filename:
            # Read the MSG file if not already done...
            msg_communications.msgwrite_log("INFO","Read MSG CTTH file: ",msgctth_filename,moduleid=MODULE_ID)
            self.ctth = msg_ctth.msgCTTH()
            self.ctth.read_msgCtth(msgctth_filename)
        else:
            msg_communications.msgwrite_log("ERROR","No MSG CT input file found!",moduleid=MODULE_ID)
            self.ctth = None

    def save_ctth(self,filename):
        ctth = msg_ctth.msg_ctth2ppsformat(self.ctth)
        epshdf.write_cloudtop(filename, ctth, 6)
            
    def get_ctth(self):
        """Return the ctth structure.
        """
        if self.ctth is None:
            self.load_ctth
        
        return self.ctth

    def pps_ctth(self):
        """Return the ctth structure in pps format.
        """
        if self.ctth is None:
            self.load_ctth
        
        return msg_ctth.msg_ctth2ppsformat(self.ctth)

    def pge02(self):
        if self.cloudtype is None:
            return None
        
        cloudtype = msg_ctype.msg_ctype2ppsformat(self.cloudtype).cloudtype
        palette = _convert_palette(pps_array2image.get_cms_modified())
        
        cloudtype = numpy.ma.array(cloudtype)

        im = geo_image.GeoImage(cloudtype,
                                self.area_id,
                                self.time_slot,
                                mode = "P",
                                palette = palette)

        return im
        

    def pge02b(self):
        if(self[9] is None or
           self.cloudtype is None):
            return None

        cloudtype = msg_ctype.msg_ctype2ppsformat(self.cloudtype).cloudtype

        cloudtype = numpy.ma.array(cloudtype)

        palette = _convert_palette(smhi_safnwc_legends.get_vv_legend())
        arr = geo_image.crude_stretch(self[9]["BT"])
        arr = image_processing.gamma_correction(arr,1.6)
        arr = 1 - arr
        arr = (arr * 248 + 7).astype(numpy.uint8)
        arr = numpy.where(cloudtype <= 2, cloudtype, arr)
        for i in range(5,9):
            arr = numpy.where(cloudtype == i, i - 2, arr)
        
        im = geo_image.GeoImage(arr,
                                self.area_id,
                                self.time_slot,
                                mode = "P",
                                palette = palette)

        return im

    def pge02b_with_overlay(self):
        if(self[9] is None or
           self.cloudtype is None):
            return None
        
        im = self.pge02b()
        
        im.add_overlay()

        return im

    def pge02c(self):
        if(self[9] is None or
           self.cloudtype is None):
            return None

        cloudtype = msg_ctype.msg_ctype2ppsformat(self.cloudtype).cloudtype

        cloudtype = numpy.ma.array(cloudtype)

        palette = _convert_palette(smhi_safnwc_legends.get_tv_legend())

        arr = (self[9]["BT"] - 205.0) / (295.0 - 205.0)
        arr = (1 - arr).clip(0,1)
        arr = (arr * 250 + 5).astype(numpy.uint8)
        arr = numpy.where(cloudtype <= 4, cloudtype, arr)

        im = geo_image.GeoImage(arr,
                                self.area_id,
                                self.time_slot,
                                mode = "P",
                                palette = palette)
        
        return im
        
    def pge02c_with_overlay(self):
        if(self[9] is None or
           self.cloudtype is None):
            return None
        
        im = self.pge02c()

        im.add_overlay()

        return im

    def pge02d(self):
        if(self[9] is None or
           self.cloudtype is None):
            return None

        cloudtype = msg_ctype.msg_ctype2ppsformat(self.cloudtype).cloudtype
        cloudtype = numpy.ma.array(cloudtype)

        palette = _convert_palette(smhi_safnwc_legends.get_tv_legend())
        
        arr = (self[9]["BT"] - 205.0) / (295.0 - 205.0)
        arr = (1 - arr).clip(0,1)
        arr = (arr * 250 + 5).astype(numpy.uint8)
        arr = numpy.where(cloudtype <= 4, cloudtype, arr)

        alpha = numpy.where(cloudtype < 5, 0.0, 1.0)
        alpha = numpy.where(cloudtype == 15, 0.5, alpha)
        alpha = numpy.where(cloudtype == 19, 0.5, alpha)



        im = geo_image.GeoImage((arr,alpha),
                                self.area_id,
                                self.time_slot,
                                mode = "PA",
                                palette = palette)
        
        return im
        
        
    def pge02e(self):
        if(self[1] is None or
           self[2] is None or
           self[9] is None or
           self.cloudtype is None):
            return None

        im = self.overview()

        cloudtype = msg_ctype.msg_ctype2ppsformat(self.cloudtype).cloudtype
        cloudtype = numpy.ma.array(cloudtype)

        alpha = numpy.where(cloudtype < 5, 0.0, 1.0)
        alpha = numpy.where(cloudtype == 15, 0.5, alpha)
        alpha = numpy.where(cloudtype == 19, 0.5, alpha)

        im.putalpha(alpha)
        
        return im
    

    def pge03(self):
        if(self[9] is None or
           self.ctth is None):
            return None
        
        ctth = msg_ctth.msg_ctth2ppsformat(self.ctth)

        arr = (ctth.height*ctth.h_gain+ctth.h_intercept)
	a = numpy.where(ctth.height == ctth.h_nodata, 0, arr / 500.0 + 1)
	palette = _convert_palette(pps_array2image.ctth_height_legend())

        a = numpy.ma.array(a)


        im = geo_image.GeoImage(a.astype(numpy.uint8),
                                self.area_id,
                                self.time_slot,
                                mode = "P",
                                palette = palette)

        return im
        
        

    def airmass(self):
        """Make an Airmass RGB image composite from SEVIRI channels.
        
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
        if(self[5] is None or
           self[6] is None or
           self[8] is None or
           self[9] is None):
            return None

        im = geo_image.GeoImage((self[5]["BT"]-self[6]["BT"],
                                 self[8]["BT"]-self[9]["BT"],
                                 self[5]["BT"]),
                                self.area_id,
                                self.time_slot,
                                mode = "RGB",
                                range = ((-25,0),
                                         (-40,5),
                                         (243 - 70, 208 + 20)))
        return im
            
    def ir9(self):
        """Make a black and white image of SEVIRI channel 9."""
        if(self[9] is not None):
            im = geo_image.GeoImage(self[9]["BT"],
                                    self.area_id,
                                    self.time_slot,
                                    mode = "L",
                                    range = (-70+273.15,57.5+273.15))
            
            im.enhance(inverse = True)
            return im
        else:
            return None

    def wv_high(self):
        """Make a black and white image of SEVIRI channel 5."""
        if(self[5] is not None):
            im =  geo_image.GeoImage(self[5]["BT"],
                                     self.area_id,
                                     self.time_slot,
                                     mode = "L")
            im.enhance(inverse = True, stretch = "linear")
            return im
        else:
            return None

    def wv_low(self):
        """Make a black and white image of SEVIRI channel 6."""
        if(self[6] is not None):
            im = geo_image.GeoImage(self[6]["BT"],
                                    self.area_id,
                                    self.time_slot,
                                    mode = "L")

            im.enhance(inverse = True, stretch = "linear")
            return im
        else:
            return None
        
    def overview(self):
        """Make an Overview RGB image composite from SEVIRI channels.
        """
        if(self[1] is None or
           self[2] is None or
           self[9] is None):
            return None
        
        ch1 = check_range(self[1]["REFL"])
        ch2 = check_range(self[2]["REFL"])

        im = geo_image.GeoImage((ch1,
                                 ch2,
                                 -self[9]["BT"]),
                                self.area_id,
                                self.time_slot,
                                mode = "RGB")

        im.enhance(stretch = "crude")
        im.enhance(gamma = 1.6)

        return im

    def hr_overview(self):
        """Make a High Resolution Overview RGB image composite from SEVIRI
        channels.
        """
        if(self[1] is None or
           self[2] is None or
           self[9] is None or
           self[12] is None):
            return None

        ch1 = check_range(self[1]["REFL"])
        ch2 = check_range(self[2]["REFL"])


        im = geo_image.GeoImage((ch1,
                                 ch2,
                                 -self[9]["BT"]),
                                self.area_id,
                                self.time_slot,
                                mode = "RGB")

        im.enhance(stretch = "crude")
        im.enhance(gamma = [1.6,1.6,1.1])
        
        luminance = self[12]["REFL"]

        luminance = geo_image.crude_stretch(luminance)
        
        luminance = image_processing.gamma_correction(luminance,2)

        im.replace_luminance(luminance)
        
        return im
    


    def green_snow(self):
        """Make a Green Snow RGB image composite from SEVIRI channels.
        """
        if(self[3] is None or
           self[2] is None or
           self[9] is None):
            return None

        ch2 = check_range(self[2]["REFL"])
        ch3 = check_range(self[3]["REFL"])
        
        im = geo_image.GeoImage((ch3,
                                 ch2,
                                 -self[9]["BT"]),
                                self.area_id,
                                self.time_slot,
                                mode = "RGB")

        im.enhance(stretch = "crude")
        im.enhance(gamma = 1.6)

        return im

    def red_snow(self):
        """Make a Red Snow RGB image composite from SEVIRI channels.
        """
        if(self[1] is None or
           self[3] is None or
           self[9] is None):
            return None
        
        im = geo_image.GeoImage((self[1]["REFL"],
                                 self[3]["REFL"],
                                 -self[9]["BT"]),
                                self.area_id,
                                self.time_slot,
                                mode = "RGB")

        im.enhance(stretch = "crude")

        return im


    def convection(self):
        """Make a Severe Convection RGB image composite from SEVIRI channels.
        """
        if(self[1] is None or
           self[3] is None or
           self[4] is None or
           self[5] is None or
           self[6] is None or
           self[9] is None):
            return None

        
        ch1 = check_range(self[1]["REFL"])
        ch3 = check_range(self[3]["REFL"])

        im = geo_image.GeoImage((self[5]["BT"] - self[6]["BT"],
                                 self[4]["BT"] - self[9]["BT"],
                                 ch3 - ch1),
                                self.area_id,
                                self.time_slot,
                                mode = "RGB",
                                range = ((-30, 0),
                                         (0, 55),
                                         (- 70, 20)))

        return im


    def fog(self):
        """Make a Fog RGB image composite from SEVIRI channels.
        """
        if(self[7] is None or
           self[9] is None or
           self[10] is None):
            return None
        
        im = geo_image.GeoImage((self[10]["BT"] - self[9]["BT"],
                                 self[9]["BT"] - self[7]["BT"],
                                 self[9]["BT"]),
                                self.area_id,
                                self.time_slot,
                                mode = "RGB",
                                range = ((-4, 2),
                                         (0, 6),
                                         (243, 283)))

        im.enhance(gamma = (1.0, 2.0, 1.0))
        
        return im

    def night_fog(self):
        """Make a Night Fog RGB image composite from SEVIRI channels.
        """
        if(self[4] is None or
           self[9] is None or
           self[10] is None):
            return None
        
        im = geo_image.GeoImage((self[10]["BT"] - self[9]["BT"],
                                 self[9]["BT"] - self[4]["BT"],
                                 self[9]["BT"]),
                                self.area_id,
                                self.time_slot,
                                mode = "RGB",
                                range = ((-4, 2),
                                         (0, 6),
                                         (243, 293)))

        im.enhance(gamma = (1.0, 2.0, 1.0))

        return im

    def cloudtop(self):
        """Make a Cloudtop RGB image composite from SEVIRI channels.
        """
        if(self[4] is None or
           self[9] is None or
           self[10] is None):
            return None
        
        im = geo_image.GeoImage((- self[4]["BT"],
                                 - self[9]["BT"],
                                 - self[10]["BT"]),
                                self.area_id,
                                self.time_slot,
                                mode = "RGB")

        im.enhance(stretch = (0.005,0.005))

        return im
        
def _getkey(item,key):
    return item[key]

def check_range(arr,min_range = 1.0):
    if((arr.max() - arr.min()) < min_range):
        return numpy.ma.zeros(arr.shape)
    else:
        return arr

class MSGChannel:
    def __init__(self, time_slot, area_id, channel_id, data = None, rad = True):
        area_filename = "safnwc_" + area_id + ".cfg"
        self.time_slot = time_slot
        self.area_id = area_id
        self.channel_id = channel_id
        self.wavelength = None
        if (data is None):
            if isinstance(channel_id, int):
                channel_id = "%d"%channel_id
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
                                       mask = data["MASK"],
                                       fill_value = py_msg.missing_value())

        if (channel_id == "HRVIS" or
            channel_id == "VIS06" or
            channel_id == "VIS08" or
            channel_id == "IR16" or
            channel_id == "1" or
            channel_id == "2" or
            channel_id == "3" or
            channel_id == "12" or
            channel_id == 1 or
            channel_id == 2 or
            channel_id == 3 or
            channel_id == 12):
            self._refl = numpy.ma.array(data["CAL"],
                                        mask = data["MASK"],
                                        fill_value = py_msg.missing_value())
            self._bt = None
        else:
            self._bt = numpy.ma.array(data["CAL"],
                                      mask = data["MASK"],
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
        if(coverage is None):
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


def _convert_palette(p):
    palette = []
    for i in p:
        palette.append((i[0] / 255.0,
                        i[1] / 255.0,
                        i[2] / 255.0))
#    print palette
    return palette
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

