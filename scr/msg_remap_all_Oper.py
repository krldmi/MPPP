# -*- coding: UTF-8 -*-
# **************************************************************************
#
#  COPYRIGHT   : SMHI
#  PRODUCED BY : Swedish Meteorological and Hydrological Institute (SMHI)
#                Folkborgsvaegen 1
#                Norrkoping, Sweden
#
#  PROJECT      : 
#  FILE         : msg_remap_all_Oper.py
#  TYPE         : Python program
#  PACKAGE      : Nowcasting-SAF Post processing for MSG
#
#  SUMMARY      : 
# 
#  DESCRIPTION  :
#
#  SYNOPSIS     :
#
#  OPTIONS      : None
#
# *************************************************************************
#
# CVS History:
#
# $Id: msg_remap_all_Oper.py,v 1.29 2009/05/29 23:06:28 Adam.Dybbroe Exp $
#
# $Log: msg_remap_all_Oper.py,v $
# Revision 1.29  2009/05/29 23:06:28  Adam.Dybbroe
# No more use of swedish letters.
# Added threading to the code. Added doOneArea function.
# Adapted to new SIR, using /local_disk/data/sir saving as a local repository (to be able to debug).
# Documented the code.
#
# Revision 1.28  2008/07/08 12:22:43  adybbroe
# Excluding certain slots, known to have bad quality under certain conditions - equinox problems.
#
# Revision 1.27  2008/04/29 09:38:16  adybbroe
# Adapted to new naming convention as of NWCSAF/MSG version 2008. The
# julian day number and slot number is now replaced by a date-time string.
#
# Revision 1.26  2008/04/29 08:31:57  adybbroe
# Do not sync hdf5 mesanx products at times 23:30, 23:45, and 00 UTC out
# to fileserver. This is the hack introduced on safir April 24, 2008, in
# order to prevent bad classifications entering Mesan. It should be
# turned off again, and anyhow a more general solution should be prepared.
#
# Revision 1.25  2007/10/30 14:39:39  adybbroe
# Changes to bring in and older version from cvs release 0.27, that seem
# to have been lost. The stretching of channel 9 bw data for SVT should
# be less sensitive to diurnal cycle now again - this was in previously
# but was lost in release 0.30. Also added functions to write channel
# data (brighness temperatures, radiances and reflectances) from the
# NWCSAF/MSG temporary binary format in hdf5. This should be useful for
# archiving.
#
#
# *************************************************************************
#
#
#
#
from msgpp_config import *

import _satproj
import epshdf
import area
import glob,os
import pps_array2image

from msg_communications import *

from msg_ctype_remap import *
from msg_ctth_remap import *
from msg_rgb_remap import *

from pps_array2image import get_cms_modified
from smhi_safnwc_legends import *

from msg_rgb_remap_all_Oper import do_sir


MODULE_ID = "MSG_PROD_REMAP"

# -----------------------------------------------------------------------
# In order to utilise more than one CPU at the same time
from threading import Thread

class threadit(Thread):
   def __init__ (self,in_aid,areaid,lon,lat,MetSat,year,month,day,hour,minute,**options):
      Thread.__init__(self)      
      self.output_areaId=areaid
      self.input_areaId=in_aid
      self.lon = lon      
      self.lat = lat
      self.MetSat=MetSat
      self.year=year
      self.month=month
      self.day=day
      self.hour=hour
      self.minute=minute
      
   def run(self):
       doOneArea(self.input_areaId,self.output_areaId,self.lon,self.lat,
                 self.MetSat,self.year,self.month,self.day,self.hour,self.minute)


# -----------------------------------------------------------------------
def inform_sir(saf_name,pge_name,aidstr,status,datestr):
    """
    Send signal to SIR launching SIR-script from system command.

    @return: None
    """
    import string

    msgwrite_log("INFO","inside inform_sir...",moduleid=MODULE_ID)
    msgwrite_log("INFO","aidstr=%s"%aidstr,moduleid=MODULE_ID)
    informsir_params = (string.upper("%s_%s"%(saf_name[0:3],pge_name)),string.upper(aidstr))
    msgwrite_log("INFO","informsir_params: ",informsir_params,moduleid=MODULE_ID)
    cmdstr = "%s %s %s %s %d"%(INFORMSIR_SCRIPT,informsir_params[0],informsir_params[1],datestr,status)
    msgwrite_log("INFO","Inform SIR command: %s"%(cmdstr),moduleid=MODULE_ID)
    os.system(cmdstr)

    return

# -----------------------------------------------------------------------
def inform_sir2(prod_name,aidstr,status,datestr):
    """
    Send signal to SIR launching SIR-script from system command.

    @type prod_name: String
    @param prod_name: Product name to be passed to SIR script
    @type aidstr: String
    @param aidstr: Area id string to be passed to SIR script
    @type status: Int
    @param status: Switch - 0 or 1 (1=ok,0=do nothing)
    @type datestr: String
    @param datestr: Date-time string to be passed to SIR script
    @return: None
    """
    import string

    msgwrite_log("INFO","inside inform_sir...",moduleid=MODULE_ID)
    msgwrite_log("INFO","aidstr=%s"%aidstr,moduleid=MODULE_ID)
    informsir_params = (string.upper(prod_name),string.upper(aidstr))
    msgwrite_log("INFO","informsir_params: ",informsir_params,moduleid=MODULE_ID)
    cmdstr = "%s %s %s %s %d"%(INFORMSIR_SCRIPT,informsir_params[0],informsir_params[1],datestr,status)
    msgwrite_log("INFO","Inform SIR command: %s"%(cmdstr),moduleid=MODULE_ID)
    os.system(cmdstr)

    return
    
# -----------------------------------------------------------------------
def doCloudType(covData,msgctype,areaid,satellite,year,month,day,hour,minute,ctype=None):
    """
    Make Cloud Type images from hdf5 and save to file and send to SIR.
    It reads the MSG Cloud Type in satellite projection, maps it to
    a cartographic area, converts it to PPS-HDF5-format model, and
    generates images and saves results to files.
    
    @type covData: Coverage Instance
    @param covData: Coverage data used when mapping
    @type msgctype: msgCloudTypeData instance
    @param msgctype: NWCSAF/MSG Cloud Type
    @type areaid: String
    @param areaid: Area id
    @type satellite: String
    @param satellite: Satellite
    @type year: String
    @param year: Year
    @type month: String
    @param month: Month (number)
    @type day: String
    @param day: Day of month
    @type hour: String
    @param hour: Hour of day
    @type minute: String
    @param minute: Minute of hour
    @type ctype: CloudType instance (optional)
    @param ctype: PPS Cloud Type instance - MSG cloud type already remapped and converted to PPS format 
    @return: None
    """
    import string

    msgwrite_log("INFO","Area = ",areaid,moduleid=MODULE_ID)
    areaObj = area.area(areaid)

    yystr = ("%.4d"%year)[2:4]
    timestamp = "%s%.2d%.2d%.2d%.2d"%(yystr,month,day,hour,minute)
    
    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")
    outfile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.cloudtype.hdf"%(CTYPEDIR_OUT,satellite,year,month,day,hour,minute,areaid)
    msgwrite_log("INFO","Output file: ",outfile,moduleid=MODULE_ID)
    if not os.path.exists(outfile):
        msgctypeRem = msgCtype_remap_fast(covData,msgctype,areaid,areaObj)
        ctype = msg_ctype2ppsformat(msgctypeRem)
        epshdf.write_cloudtype(outfile,ctype,6)

    if PRODUCT_IMAGES["PGE02"].has_key(areaid) and  PRODUCT_IMAGES["PGE02"][areaid].has_key("standard"):
        imformat = PRODUCT_IMAGES["PGE02"][areaid]["standard"][0]
    else:
        imformat = "png"
    imagelist = glob.glob("%s*.%s"%(string.split(outfile,".hdf")[0],imformat))
    nrgbs = len(imagelist)
    msgwrite_log("INFO","Number of images already there: ",nrgbs,outfile,moduleid=MODULE_ID)
    # Is this okay? Ad, 2006-03-08
    if nrgbs >= 2:
        return

    msgwrite_log("INFO","areaid: ",areaid,moduleid=MODULE_ID)
    msgwrite_log("INFO","SIR_PRODUCTS.has_key(areaid): ",SIR_PRODUCTS.has_key(areaid),moduleid=MODULE_ID)
    if SIR_PRODUCTS.has_key(areaid):
        msgwrite_log("INFO","SIR_PRODUCTS[areaid].keys(): ",SIR_PRODUCTS[areaid].keys(),moduleid=MODULE_ID)
    if SIR_PRODUCTS.has_key(areaid) and "PGE02" in SIR_PRODUCTS[areaid].keys():
	msgwrite_log("INFO","SIR product PGE02 is there",moduleid=MODULE_ID)

    # Make images to distribute via SIR for forecasters and others:
    if SIR_PRODUCTS.has_key(areaid) and "PGE02" in SIR_PRODUCTS[areaid].keys() and \
           len(SIR_PRODUCTS[areaid]["PGE02"]) > 0 and os.path.exists(outfile) and SIR_SIGNAL[areaid]["PGE02"]:
        # Make (extra) image(s) of the result:        
        msgwrite_log("INFO","Make (extra) Cloud Type images for SMHI from the hdf5",moduleid=MODULE_ID)
        legend_name = "standard"
        msgwrite_log("INFO","Call cloudtype2image",moduleid=MODULE_ID)
        msgwrite_log("INFO","Pallete type: %s"%(legend_name),moduleid=MODULE_ID)
        if PGE02_SIR_NAMES.has_key(legend_name):
            legend = PGE02_LEGENDS[legend_name]
        else:
             msgwrite_log("ERROR","legend not registered! Stop...",moduleid=MODULE_ID)
             return
         
        if not ctype:
            ctype = epshdf.read_cloudtype(outfile,1,0,0)
                
        im = pps_array2image.cloudtype2image(ctype.cloudtype,legend)
        msgwrite_log("INFO","image instance created...",moduleid=MODULE_ID)

        # do_sir function taken from msg_rgb_remap_all_Oper.py
        do_sir(im,"PGE02",year,month,day,hour,minute,areaid)        
        
    # Make standard images:
    if PRODUCT_IMAGES["PGE02"].has_key(areaid):
        #print PRODUCT_IMAGES["PGE02"][areaid].keys()
        for key in PRODUCT_IMAGES["PGE02"][areaid].keys():
            for imformat in PRODUCT_IMAGES["PGE02"][areaid][key]:
                imagefile = outfile.split(".hdf")[0] + "_%s.%s"%(string.lower(key),imformat)
                thumbnail = outfile.split(".hdf")[0] + "_%s.thumbnail.%s"%(string.lower(key),imformat)
                #print "IMAGE FILE: ",imagefile 
                if not os.path.exists(imagefile):
                    if not ctype:
                        ctype = epshdf.read_cloudtype(outfile,1,1,0)
                    if PGE02_LEGENDS.has_key(key):
                        this = pps_array2image.cloudtype2image(ctype.cloudtype,PGE02_LEGENDS[key])
                        size=this.size
                        this.save(imagefile)
                        this.thumbnail((size[0]/3,size[1]/3))
                        this.save(thumbnail)
                    else:
                        msgwrite_log("ERROR","Failed generating image file",moduleid=MODULE_ID)
                        msgwrite_log("INFO","Legend not supported!",moduleid=MODULE_ID)
                    
    # Sync the output with fileserver:
    if FSERVER_SYNC:
        synctmp = "%s"%SYNC
        for item in SYNC_EXCLUDE_TIMESLOTS:
            synctmp = synctmp + " --exclude 'met0*_%s.*hdf'"%item
        #synctmp = "%s --exclude 'met0*_0000.*hdf' --exclude 'met0*_2345.*hdf' --exclude 'met0*2330.*hdf'"%SYNC
        #synctmp = "%s"%SYNC
        cmdstr = "%s %s/%s* %s/."%(synctmp,CTYPEDIR_OUT,os.path.basename(outfile).split(".hdf")[0],FSERVER_CTYPEDIR_OUT)
        msgwrite_log("INFO","Sync-command = %s"%cmdstr,moduleid=MODULE_ID)
        os.system(cmdstr)
        #os.system("%s %s/%s* %s/."%(SYNC,CTYPEDIR_OUT,os.path.basename(outfile).split(".hdf")[0],FSERVER_CTYPEDIR_OUT))

    return

# -----------------------------------------------------------------------
def doCtth(covData,msgctth,areaid,satellite,year,month,day,hour,minute,ctth=None):
    """
    Make CTTH product images from hdf5 and save to file and send to SIR.
    It reads the MSG CTTH product in satellite projection, maps it to
    a cartographic area, converts it to PPS-HDF5-format model, and
    generates images and saves results to files.
    
    @type covData: Coverage Instance
    @param covData: Coverage data used when mapping
    @type msgctth: msgCTTHData instance
    @param msgctth: NWCSAF/MSG CTTH instance
    @type areaid: String
    @param areaid: Area id
    @type satellite: String
    @param satellite: Satellite
    @type year: String
    @param year: Year
    @type month: String
    @param month: Month (number)
    @type day: String
    @param day: Day of month
    @type hour: String
    @param hour: Hour of day
    @type minute: String
    @param minute: Minute of hour
    @type ctth: CloudTop instance (optional)
    @param ctth: PPS CTTH instance - MSG CTTH product already remapped and converted to PPS format 
    @return: None
    """
    import string
    
    msgwrite_log("INFO","Area id: %s"%(areaid),moduleid=MODULE_ID)
    if PRODUCT_IMAGES["PGE03"].has_key(areaid) and  PRODUCT_IMAGES["PGE03"][areaid].has_key("standard"):
        imformat = PRODUCT_IMAGES["PGE03"][areaid]["standard"][0]
    else:
        imformat = "png"
    
    areaObj = area.area(areaid)
    yystr = ("%.4d"%year)[2:4]
    timestamp = "%s%.2d%.2d%.2d%.2d"%(yystr,month,day,hour,minute)
    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")

    outfile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.ctth.hdf"%(CTTHDIR_OUT,satellite,year,month,day,hour,minute,areaid)
    msgwrite_log("INFO","Output file: %s"%(outfile),moduleid=MODULE_ID)
    if not os.path.exists(outfile):
        msgctthRem = msgCtth_remap_fast(covData,msgctth,areaid,areaObj)
        ctth = msg_ctth2ppsformat(msgctthRem)
        epshdf.write_cloudtop(outfile,ctth,6)

    imagelist = glob.glob("%s*.%s"%(string.split(outfile,".hdf")[0],imformat))
    nrgbs = len(imagelist)
    msgwrite_log("INFO","Number of images already there: %d"%nrgbs,moduleid=MODULE_ID)
    if nrgbs >= 2:
        return
    
    # Make images to distribute via SIR for forecasters and others:
    if SIR_PRODUCTS.has_key(areaid) and "PGE03" in SIR_PRODUCTS[areaid].keys() and \
           len(SIR_PRODUCTS[areaid]["PGE03"]) > 0 and os.path.exists(outfile) and SIR_SIGNAL[areaid]["PGE03"]:
        # Make (extra) image(s) of the result:        
        msgwrite_log("INFO","Make (extra) CTTH images for SMHI from the hdf5",moduleid=MODULE_ID)
        legend_name = "standard"
        msgwrite_log("INFO","Pallete type: %s"%(legend_name),moduleid=MODULE_ID)
        if not ctth:
            ctth=epshdf.read_cloudtop(outfile,1,1,1,0,1)

        this,arr = pps_array2image.ctth2image(ctth,PGE03_LEGENDS[legend_name])
        msgwrite_log("INFO","image instance created...",moduleid=MODULE_ID)

        # do_sir function taken from msg_rgb_remap_all_Oper.py
        do_sir(this,"PGE03",year,month,day,hour,minute,areaid)        
        
    # Make standard images:
    if PRODUCT_IMAGES["PGE03"].has_key(areaid):
        msgwrite_log("INFO",PRODUCT_IMAGES["PGE03"][areaid].keys(),moduleid=MODULE_ID)
        for key in PRODUCT_IMAGES["PGE03"][areaid].keys():
            for imformat in PRODUCT_IMAGES["PGE03"][areaid][key]:
                imagefile = outfile.split(".hdf")[0] + "_%s.%s"%(string.lower(key),imformat)
                thumbnail = outfile.split(".hdf")[0] + "_%s.thumbnail.%s"%(string.lower(key),imformat)
                msgwrite_log("INFO","IMAGE FILE: %s"%imagefile,moduleid=MODULE_ID)
                if not os.path.exists(imagefile):
                    if not ctth:
                        ctth = epshdf.read_cloudtop(outfile,1,1,1,0,1)                
                    if PGE03_LEGENDS.has_key(key):
                        this,arr = pps_array2image.ctth2image(ctth,PGE03_LEGENDS[key])
                        size=this.size
                        this.save(imagefile)
                        this.thumbnail((size[0]/3,size[1]/3))
                        this.save(thumbnail)
                    else:
                        msgwrite_log("ERROR","Failed generating image file",moduleid=MODULE_ID)
                        msgwrite_log("INFO: Legend not supported!",moduleid=MODULE_ID)

    # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
    if FSERVER_SYNC:
        synctmp = "%s"%SYNC
        for item in SYNC_EXCLUDE_TIMESLOTS:
            synctmp = synctmp + " --exclude 'met0*_%s.*hdf'"%item
        #synctmp = "%s --exclude 'met0*_0000.*hdf' --exclude 'met0*_2345.*hdf' --exclude 'met0*2330.*hdf'"%SYNC
        #synctmp = "%s"%SYNC
        cmdstr = "%s %s/%s* %s/."%(synctmp,CTTHDIR_OUT,os.path.basename(outfile).split(".hdf")[0],FSERVER_CTTHDIR_OUT)
        msgwrite_log("INFO","Sync-command = %s"%cmdstr,moduleid=MODULE_ID)
        os.system(cmdstr)
        #os.system("%s %s/%s* %s/."%(SYNC,CTTHDIR_OUT,os.path.basename(outfile).split(".hdf")[0],FSERVER_CTTHDIR_OUT))

    return

# -----------------------------------------------------------------------
def doCprod01(cov,areaid,satellite,year,month,day,hour,minute):
    """
    Make CTTH product images from hdf5 and save to file and send to SIR.
    It reads the MSG CTTH product in satellite projection, maps it to
    a cartographic area, converts it to PPS-HDF5-format model, and
    generates images and saves results to files.
    
    @type covData: Coverage Instance
    @param covData: Coverage data used when mapping
    @type msgctth: msgCTTHData instance
    @param msgctth: NWCSAF/MSG CTTH instance
    @type areaid: String
    @param areaid: Area id
    @type satellite: String
    @param satellite: Satellite
    @type year: String
    @param year: Year
    @type month: String
    @param month: Month (number)
    @type day: String
    @param day: Day of month
    @type hour: String
    @param hour: Hour of day
    @type minute: String
    @param minute: Minute of hour
    @type ctth: CloudTop instance (optional)
    @param ctth: PPS CTTH instance - MSG CTTH product already remapped and converted to PPS format 
    @return: None
    """
    import string
    import msg_ctype_products
    import tempfile,os

    yystr = ("%.4d"%year)[2:4]
    timestamp = "%s%.2d%.2d%.2d%.2d"%(yystr,month,day,hour,minute)

    #fileprfx="%s/%.4d/%.2d/%.2d"%(RGBDIR_IN,year,month,day)
    fileprfx="%s"%(RGBDIR_IN)
    fname = "%.4d%.2d%.2d%.2d%.2d_C%.4d_%.4d_S%.4d_%.4d"%(year,month,day,hour,minute,MSG_AREA_CENTER[0],MSG_AREA_CENTER[1],ROWS,COLS)

    fl = glob.glob("%s/*_%s*"%(fileprfx,fname))
    if len(fl) == 0:
        msgwrite_log("INFO","No files for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,minute),moduleid=MODULE_ID)
    else:
        msgwrite_log("INFO","Try extract SEVIRI channel(s) for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,minute),moduleid=MODULE_ID)

    ch9file = "%s/9_%s.BT"%(fileprfx,fname)
    ch9,ok9=get_ch_projected(ch9file,cov)

    if not ok9:
        msgwrite_log("INFO","ERROR: Failed extracting SEVIRI channel 9 data",moduleid=MODULE_ID)
        sys.exit(-9)

    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")
    ctypefile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.cloudtype.hdf"%(CTYPEDIR_OUT,satellite,year,month,day,hour,minute,areaid)
    msgwrite_log("INFO","Output file: ",ctypefile,moduleid=MODULE_ID)

    this,img_with_ovl = msg_ctype_products.make_ctype_prod01(ch9,ctypefile,areaid,gamma=1.6,overlay=1)

    # Make images to distribute via SIR for forecasters and others:
    if SIR_PRODUCTS.has_key(areaid) and "PGE02b" in SIR_PRODUCTS[areaid].keys() and \
           len(SIR_PRODUCTS[areaid]["PGE02b"]) > 0:

        for tup in SIR_PRODUCTS[areaid]["PGE02b"]:
            sirname,imformat=tup
            msgwrite_log("INFO","File time stamp = %s"%timestamp,moduleid=MODULE_ID)
            aidstr=string.ljust(areaid,8).replace(" ","_") # Pad with "_" up to 8 characters
            prodid=string.ljust(sirname,8).replace(" ","_") # Pad with "_" up to 8 characters
            local_outname = "%s/%s%s%s.%s"%(LOCAL_SIR_DIR,prodid,aidstr,timestamp,imformat)
            outname = "%s/%s%s%s.%s_original"%(SIR_DIR,prodid,aidstr,timestamp,imformat)
            msgwrite_log("INFO","Image file name to SIR = %s"%outname,moduleid=MODULE_ID)
            if SIR_SIGNAL[areaid]["PGE02b"]:
                sir_stat = 0
                try:
                    if sirname in ["msg_02b",] and areaid in ["scan","euro4"] and imformat == "jpg": # FIXME! Ad, 2006-09-27
                        img_with_ovl.save(local_outname,FORMAT=imformat,quality=100)
                    else:
                        this.save(local_outname,FORMAT=imformat,quality=100)
                    #this.save(outname,FORMAT=imformat,quality=100)
                except:
                    msgwrite_log("ERROR","Couldn't make image of specified format: ",imformat,moduleid=MODULE_ID)
                    sir_stat=-1
                    pass
                # Migration to new SIR:
                # No more invoking the sir-signal script.
                # Adam Dybbroe, 2008-11-20
	    	# We keep the '_original' extentions for consistency - proved
            	# too much work for customers to adapt. Adam Dybbroe, 2008-11-26
                fdhandle_lvl,tmpfilename = tempfile.mkstemp('.%s'%imformat,
                                                            '%s%s%s'%(prodid,aidstr,timestamp),SIR_DIR)
                msgwrite_log("INFO","Temporary file created: Handle level=%d, Name=%s"%(fdhandle_lvl,tmpfilename),moduleid=MODULE_ID)
            	if os.path.exists(local_outname):
                   shutil.copy(local_outname,tmpfilename)
                   msgwrite_log("INFO","Temporary file available in SIR: Name=%s"%(tmpfilename),moduleid=MODULE_ID)
                   os.rename(tmpfilename,outname)
                   msgwrite_log("INFO","Temporary file in SIR renamed: Name=%s"%(outname),moduleid=MODULE_ID)
                else:
                   os.remove(tmpfilename)
            else:
               msgwrite_log("INFO","No product to SIR",moduleid=MODULE_ID)

    # ==========================================================
    # New since Nov-7, 2006, Adam Dybbroe:
    if SIR_PRODUCTS.has_key(areaid) and "PGE02bj" in SIR_PRODUCTS[areaid].keys() and \
           len(SIR_PRODUCTS[areaid]["PGE02bj"]) > 0:

        # do_sir function taken from msg_rgb_remap_all_Oper.py
        do_sir(img_with_ovl,"PGE02bj",year,month,day,hour,minute,areaid)        

    # ==========================================================
    
    # Sync the output with fileserver:
    if PRODUCT_IMAGES["PGE02"].has_key(areaid) and  PRODUCT_IMAGES["PGE02"][areaid].has_key("standard"):
        for key in PRODUCT_IMAGES["PGE02"][areaid].keys():
            imformat = PRODUCT_IMAGES["PGE02"][areaid][key]
            if FSERVER_SYNC:
                os.system("%s %s/%s_ir.*%s %s/."%(SYNC,CTYPEDIR_OUT,os.path.basename(ctypefile).split(".hdf")[0],imformat,FSERVER_CTYPEDIR_OUT))
    else:
        msgwrite_log("WARNING","No image format specified in configuration... No syncing to fileserver!",moduleid=MODULE_ID)
        
    return

# -----------------------------------------------------------------------
def doCprod02(cov,areaid,satellite,year,month,day,hour,minute):
    import string
    import msg_ctype_products
    import tempfile,os

    yystr = ("%.4d"%year)[2:4]
    timestamp = "%s%.2d%.2d%.2d%.2d"%(yystr,month,day,hour,minute)
    fileprfx="%s"%(RGBDIR_IN)
    fname = "%.4d%.2d%.2d%.2d%.2d_C%.4d_%.4d_S%.4d_%.4d"%(year,month,day,hour,minute,MSG_AREA_CENTER[0],MSG_AREA_CENTER[1],ROWS,COLS)

    fl = glob.glob("%s/*_%s*"%(fileprfx,fname))
    if len(fl) == 0:
        msgwrite_log("INFO","No files for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,minute),moduleid=MODULE_ID)
    else:
        msgwrite_log("INFO","Try extract SEVIRI channel(s) for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,minute),moduleid=MODULE_ID)

    ch9file = "%s/9_%s.BT"%(fileprfx,fname)
    ch9,ok9=get_ch_projected(ch9file,cov)
    if not ok9:
        msgwrite_log("INFO","ERROR: Failed extracting SEVIRI channel 9 data",moduleid=MODULE_ID)
        sys.exit(-9)

    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")
    ctypefile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.cloudtype.hdf"%(CTYPEDIR_OUT,satellite,year,month,day,hour,minute,areaid)
    msgwrite_log("INFO","Output file: ",ctypefile,moduleid=MODULE_ID)

    #this,img_with_ovl = msg_ctype_products.make_ctype_prod02(ch9,ctypefile,areaid,gamma=1.6,overlay=1)
    this,img_with_ovl = msg_ctype_products.make_ctype_prod02(ch9,ctypefile,areaid,overlay=1) # Use stretch = crude-linear
    #this,img_with_ovl = msg_ctype_products.make_ctype_prod02(ch9,ctypefile,areaid,stretch="linear",overlay=1)
    #this = msg_ctype_products.make_ctype_prod02(ch9,ctypefile,areaid,gamma=1.6,overlay=0)

    # Make images to distribute via SIR for forecasters and others:
    if SIR_PRODUCTS.has_key(areaid) and "PGE02c" in SIR_PRODUCTS[areaid].keys() and \
           len(SIR_PRODUCTS[areaid]["PGE02c"]) > 0:

        for tup in SIR_PRODUCTS[areaid]["PGE02c"]:
            sirname,imformat=tup
            msgwrite_log("INFO","File time stamp = %s"%timestamp,moduleid=MODULE_ID)
            aidstr=string.ljust(areaid,8).replace(" ","_") # Pad with "_" up to 8 characters
            prodid=string.ljust(sirname,8).replace(" ","_") # Pad with "_" up to 8 characters
            local_outname = "%s/%s%s%s.%s"%(LOCAL_SIR_DIR,prodid,aidstr,timestamp,imformat)
            outname = "%s/%s%s%s.%s_original"%(SIR_DIR,prodid,aidstr,timestamp,imformat)
            msgwrite_log("INFO","Image file name to SIR = %s"%outname,moduleid=MODULE_ID)
            if SIR_SIGNAL[areaid]["PGE02c"]:
                sir_stat = 0
                try:
                    if sirname in ["metirccj"]:
                        img_with_ovl.save(local_outname,FORMAT=imformat,quality=100)
                    else:
                        this.save(local_outname,FORMAT=imformat,quality=100)
                except:
                    msgwrite_log("ERROR","Couldn't make image of specified format: ",imformat,moduleid=MODULE_ID)
                    sir_stat=-1
                    pass
                # Migration to new SIR:
                # No more invoking the sir-signal script.
                # Adam Dybbroe, 2008-11-20
	    	# We keep the '_original' extentions for consistency - proved
            	# too much work for customers to adapt. Adam Dybbroe, 2008-11-26
                fdhandle_lvl,tmpfilename = tempfile.mkstemp('.%s'%imformat,
                                                            '%s%s%s'%(prodid,aidstr,timestamp),SIR_DIR)
            	if os.path.exists(local_outname):
                   shutil.copy(local_outname,tmpfilename)
                   os.rename(tmpfilename,outname)
                else:
                   os.remove(tmpfilename)
            else:
                msgwrite_log("INFO","No product to SIR",moduleid=MODULE_ID)
    
    # Sync the output with fileserver:
    if PRODUCT_IMAGES["PGE02"].has_key(areaid) and  PRODUCT_IMAGES["PGE02"][areaid].has_key("standard"):
        for key in PRODUCT_IMAGES["PGE02"][areaid].keys():
            imformat = PRODUCT_IMAGES["PGE02"][areaid][key]
            if FSERVER_SYNC:
                os.system("%s %s/%s_irtv.*%s %s/."%(SYNC,CTYPEDIR_OUT,os.path.basename(ctypefile).split(".hdf")[0],imformat,FSERVER_CTYPEDIR_OUT))
    else:
        msgwrite_log("WARNING","No image format specified in configuration... No syncing to fileserver!",moduleid=MODULE_ID)

    return

# -----------------------------------------------------------------------
def doNordradCtype(covData,msgctype,areaid,satellite,year,month,day,hour,minute):
    import string
    import area
    import msg_ctype2radar

    areaObj = area.area(areaid)
    datestr = "%.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,minute)

    outfile = "%s/%s_nordrad_%.4d%.2d%.2d_%.2d%.2d.%s.cloudtype.hdf"%(CTYPEDIR_OUT,satellite,year,month,day,hour,minute,areaid)
    msgwrite_log("INFO","Output file: ",outfile,moduleid=MODULE_ID)
    if not os.path.exists(outfile):
        msgctype = msgCtype_remap_fast(covData,msgctype,areaid,areaObj)            
        status = msg_ctype2radar.msg_writectype2nordradformat(msgctype,outfile,datestr)
        if status:
            # Send the product to the nordrad servers:
            for tup in N2SERVERS_AND_PORTS:
                cmdstr = "%s %s:%d %s"%(N2INJECT,tup[0],tup[1],outfile)
                msgwrite_log("INFO","Command: %s"%(cmdstr),moduleid=MODULE_ID)
                os.system(cmdstr)
        else:
            msgwrite_log("ERROR","Failed writing cloudtype product for Nordrad!",moduleid=MODULE_ID)
            msgwrite_log("INFO","Filename = %s"%(outfile),moduleid=MODULE_ID)

    return


# -----------------------------------------------------------------------
def doOneArea(in_aid,areaid,lon,lat,MetSat,year,month,day,hour,minute):
    import area
    areaObj=area.area(areaid)

    # Check for existing coverage file for the area:
    covfilename = "%s/cst/msg_coverage_%s.%s.hdf"%(APPLDIR,in_aid,areaid)
    CoverageData = None
    
    if not CoverageData and not os.path.exists(covfilename):
        msgwrite_log("INFO","Generate MSG coverage and store in file...",moduleid=MODULE_ID)
        CoverageData = _satproj.create_coverage(areaObj,lon,lat,1)
        writeCoverage(CoverageData,covfilename,in_aid,areaid)
    elif not CoverageData:
        msgwrite_log("INFO","Read the MSG coverage from file...",moduleid=MODULE_ID)
        CoverageData,info = readCoverage(covfilename)

    if msgctype:
        doCloudType(CoverageData,msgctype,areaid,MetSat,year,month,day,hour,minute)
        if areaid in NORDRAD_AREAS:
            doNordradCtype(CoverageData,msgctype,areaid,MetSat,year,month,day,hour,minute)
        if areaid in NWCSAF_PRODUCTS["PGE02b"] or areaid in NWCSAF_PRODUCTS["PGE02bj"]:
            doCprod01(CoverageData,areaid,MetSat,year,month,day,hour,minute)
        if areaid in NWCSAF_PRODUCTS["PGE02c"]:
            doCprod02(CoverageData,areaid,MetSat,year,month,day,hour,minute)

    if msgctth:
        if areaid not in ["euro","eurotv","scan"]:
            doCtth(CoverageData,msgctth,areaid,MetSat,year,month,day,hour,minute)

    return

# -----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Usage: %s <n-slots back in time>"%(sys.argv[0])
        sys.exit(-9)
    else:
        import string
        nSlots = string.atoi(sys.argv[1])

    import msg_rgb_remap_all_Oper
    
    start_date,end_date = msg_rgb_remap_all_Oper.get_times(nSlots)
    msgwrite_log("INFO","Start and End times: ",start_date,end_date,moduleid=MODULE_ID)

    import string,time
    in_aid=MSG_AREA
    MetSat=MSG_SATELLITE
    
    lon = read_msg_lonlat(LONFILE)
    lat = read_msg_lonlat(LATFILE)

    year=string.atoi(start_date[0:4])
    month=string.atoi(start_date[4:6])
    day=string.atoi(start_date[6:8])
    hour=string.atoi(start_date[8:10])
    minute=string.atoi(start_date[10:12])    
    time_start = time.mktime((year,month,day,hour,minute,0,0,0,0)) - time.timezone

    year=string.atoi(end_date[0:4])
    month=string.atoi(end_date[4:6])
    day=string.atoi(end_date[6:8])
    hour=string.atoi(end_date[8:10])
    minute=string.atoi(end_date[10:12])    
    time_end = time.mktime((year,month,day,hour,minute,0,0,0,0)) - time.timezone

    if time_start > time_end:
        msgwrite_log("INFO","Start time is later than end time!",moduleid=MODULE_ID)
        
    sec = time_start    
    while (sec < time_end + 1):
        ttup = time.gmtime(sec)
        year,month,day,hour,minute,dummy,dummy,jday,dummy = ttup
        slotn = hour*4+int((minute+7.5)/15)

        #prefix="SAFNWC_MSG%.1d_CT___%.2d%.3d_%.3d_%s"%(MSG_NUMBER,year-2000,jday,slotn,in_aid)
        # Changed name-convention with version 2008!:
        prefix="SAFNWC_MSG%.1d_CT___%.4d%.2d%.2d%.2d%.2d_%s"%(MSG_NUMBER,year,month,day,hour,minute,in_aid)
        #match_str = "%s/%s*h5"%(CTYPEDIR_IN,prefix)
        match_str = "%s/%s*PLAX.CTTH.0.h5"%(CTYPEDIR_IN,prefix)
        msgwrite_log("INFO","file-match: ",match_str,moduleid=MODULE_ID)
        flist = glob.glob(match_str)
	msgctype=None
        if len(flist) > 1:
            msgwrite_log("ERROR","More than one matching input file: N = ",len(flist),moduleid=MODULE_ID)
        elif len(flist) == 0:
            msgwrite_log("ERROR","No matching input file",moduleid=MODULE_ID)
        else:
            # First read the original MSG file if not already done...
            msgwrite_log("INFO","Read MSG CT file: ",flist[0],moduleid=MODULE_ID)
            msgctype = read_msgCtype(flist[0])
            
        #prefix="SAFNWC_MSG%.1d_CTTH_%.2d%.3d_%.3d_%s"%(MSG_NUMBER,year-2000,jday,slotn,in_aid)
        prefix="SAFNWC_MSG%.1d_CTTH_%.4d%.2d%.2d%.2d%.2d_%s"%(MSG_NUMBER,year,month,day,hour,minute,in_aid)
        #match_str = "%s/%s*h5"%(CTTHDIR_IN,prefix)
        match_str = "%s/%s*PLAX.CTTH.0.h5"%(CTTHDIR_IN,prefix)
        msgwrite_log("INFO","file-match: ",match_str,moduleid=MODULE_ID)
        flist = glob.glob(match_str)
	msgctth=None
        if len(flist) > 1:
            msgwrite_log("ERROR","More than one matching input file: N = ",len(flist),moduleid=MODULE_ID)
        elif len(flist) == 0:
            msgwrite_log("ERROR","No matching input file",moduleid=MODULE_ID)
        else:
            # First read the original MSG file if not already done...
            msgwrite_log("INFO","Read MSG CTTH file: ",flist[0],moduleid=MODULE_ID)
            msgctth = read_msgCtth(flist[0])

	if not msgctype and not msgctth:
            sec = sec + DSEC_SLOTS
            continue

        runlist = []
        # Loop over areas:
        for areaid in NWCSAF_MSG_AREAS:
            this = threadit(in_aid,areaid,lon,lat,MetSat,year,month,day,hour,minute)
            runlist.append(this)
            this.start()

        for item in runlist:
            item.join()

        # Loop over areas:
        #for areaid in NWCSAF_MSG_AREAS:
        #    doOneArea(in_aid,areaid,lon,lat,MetSat,year,month,day,hour,minute)

        sec = sec + DSEC_SLOTS

    # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
    #os.system("/usr/bin/rsync -crzulv --delete /local_disk/data/Meteosat8/MesanX/ /data/proj/saftest/nwcsafmsg/PGEs")
