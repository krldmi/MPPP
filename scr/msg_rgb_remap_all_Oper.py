# -*- coding: utf-8 -*-
# **************************************************************************
#
#  COPYRIGHT   : SMHI
#  PRODUCED BY : Swedish Meteorological and Hydrological Institute (SMHI)
#                Folkborgsvaegen 1
#                Norrkoping, Sweden
#
#  PROJECT      : 
#  FILE         : msg_rgb_remap_all_Oper.py
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
# $Id: msg_rgb_remap_all_Oper.py,v 1.19 2009/05/29 22:33:28 Adam.Dybbroe Exp $
#
# $Log: msg_rgb_remap_all_Oper.py,v $
# Revision 1.19  2009/05/29 22:33:28  Adam.Dybbroe
# Change of do_sir function: Adaptations to new SIR: Using
# /local_disk/data/sir as a temporary storage.  Moving much of the
# main part in under the new function doOneAreaRgbs.
#
# Revision 1.18  2007/10/31 20:01:35  adybbroe
# Added for airmass RGB generation, if channel 8 is available.
#
# Revision 1.17  2007/10/30 14:39:39  adybbroe
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

# Local modules

from msg_communications import *
from msgpp_config import *
from msg_remap_util import *
from msg_rgb_remap import *
from misc_utils import *

# PPS modules

import _satproj
import area

# Global modules

import math
import glob
import os
import shutil

MODULE_ID="MSG_RGB_REMAP"

# ------------------------------------------------------------------

def do_sir(imIn,prodid,year,month,day,hour,minute,areaid):
    import string
    import tempfile,os
    
    if SIR_SIGNAL[areaid].has_key(prodid) and not SIR_SIGNAL[areaid][prodid] or \
       not SIR_SIGNAL[areaid].has_key(prodid):
        msgwrite_log("INFO","No product requested for SIR",moduleid=MODULE_ID)
        return
    
    msgwrite_log("INFO","Product requested for SIR: %s"%SIR_DIR,moduleid=MODULE_ID)

    import msg_remap_all_Oper
    yystr = ("%.4d"%year)[2:4]
    timestamp = "%s%.2d%.2d%.2d%.2d"%(yystr,month,day,hour,minute)
                    
    for name_format in SIR_PRODUCTS[areaid][prodid]:
        prodname=name_format[0]
        imformat=name_format[1]
        msgwrite_log("INFO","File time stamp = %s"%timestamp,moduleid=MODULE_ID)
        aidstr=string.ljust(areaid,8).replace(" ","_") # Pad with "_" up to 8 characters
        prodid=string.ljust(prodname,8).replace(" ","_") # Pad with "_" up to 8 characters

        # No more invoking the sir-signal script.
        # Adam Dybbroe, 2008-11-20
	# We keep the '_original' extentions for consistency - proved
	# too much work for customers to adapt. Adam Dybbroe, 2008-11-26

        local_outname = "%s/%s%s%s.%s"%(LOCAL_SIR_DIR,prodid,aidstr,timestamp,imformat)
        msgwrite_log("INFO","Local version for SIR verification = %s"%local_outname,moduleid=MODULE_ID)
        outname = "%s/%s%s%s.%s_original"%(SIR_DIR,prodid,aidstr,timestamp,imformat)
        msgwrite_log("INFO","Image file name to SIR = %s"%outname,moduleid=MODULE_ID)

        try:
            imIn.save(local_outname,FORMAT=imformat,quality=100)
        except:
            msgwrite_log("ERROR","Couldn't make image of specified format: ",imformat,moduleid=MODULE_ID)
            pass

        fdhandle_lvl,tmpfilename = tempfile.mkstemp('.%s'%imformat,
                                                    '%s%s%s'%(prodid,aidstr,timestamp),SIR_DIR)
        msgwrite_log("INFO","Temporary file created: Handle level=%d, Name=%s"%(fdhandle_lvl,
                                                                                tmpfilename),moduleid=MODULE_ID)
        if os.path.exists(local_outname):
            shutil.copy(local_outname,tmpfilename)
            msgwrite_log("INFO","Temporary file available in SIR: Name=%s"%(tmpfilename),moduleid=MODULE_ID)
            os.rename(tmpfilename,outname)
            msgwrite_log("INFO","Temporary file in SIR renamed: Name=%s"%(outname),moduleid=MODULE_ID)
        else:
            os.remove(tmpfilename)
            msgwrite_log("ERROR","No file to copy - No product to SIR: %s"%outname,moduleid=MODULE_ID)
    
    return

# ------------------------------------------------------------------
def get_times(nSlots):
    """Get the start and end times for the slots, where the time of
     the last slot is close to now, and the start slot is nSlots
     earlier:
     """
    import time

    dmin_slots = DSEC_SLOTS * 60

    now = time.time()
    gmt_time = time.gmtime(now)
    day_hh = gmt_time[3]
    hour_mm = gmt_time[4]
    time_tup = gmt_time[0],gmt_time[1],gmt_time[2],0,0,0,0,0,0
    end_slot_sec1970 = time.mktime(time_tup) - time.timezone + \
                       ((hour_mm+math.ceil(dmin_slots/2))/dmin_slots) * \
                       dmin_slots * 60 + day_hh * 3600
    end_time = time.gmtime(end_slot_sec1970)
    start_time = time.gmtime(end_slot_sec1970 - 60 * dmin_slots * nSlots)

    end_date = "%.4d%.2d%.2d%.2d%.2d"%(end_time[0],end_time[1],end_time[2],end_time[3],end_time[4])
    start_date = "%.4d%.2d%.2d%.2d%.2d"%(start_time[0],start_time[1],start_time[2],start_time[3],start_time[4])

    return start_date,end_date



# ------------------------------------------------------------------
def doOneAreaRgbs(in_aid,areaid,lon,lat,MetSat,year,month,day,hour,minute,fileprfx,fname):
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

    outname_nf = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_nightfog"%(RGBDIR_OUT,MetSat,
                                                               year,month,day,hour,minute,areaid)
    outname_f = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_fog"%(RGBDIR_OUT,MetSat,
                                                         year,month,day,hour,minute,areaid)
    outname_ctop = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop_co2corr"%(RGBDIR_OUT,MetSat,
                                                                         year,month,day,hour,minute,areaid)

    if os.path.exists(outname_nf+".png") and os.path.exists(outname_f+".png") and os.path.exists(outname_ctop+".png"):
        msgwrite_log("INFO","All rgb's have been done previously",moduleid=MODULE_ID)
        return
            
    msgwrite_log("INFO","Try make RGBs for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,minute),moduleid=MODULE_ID)

    ch1file = "%s/1_%s.REF"%(fileprfx,fname)
    ch2file = "%s/2_%s.REF"%(fileprfx,fname)
    ch3file = "%s/3_%s.REF"%(fileprfx,fname)
    ch4file = "%s/4_%s.BT"%(fileprfx,fname)    
    ch5file = "%s/5_%s.BT"%(fileprfx,fname)
    ch6file = "%s/6_%s.BT"%(fileprfx,fname)
    ch7file = "%s/7_%s.BT"%(fileprfx,fname)
    ch8file = "%s/8_%s.BT"%(fileprfx,fname)
    ch9file = "%s/9_%s.BT"%(fileprfx,fname)
    ch10file = "%s/10_%s.BT"%(fileprfx,fname)
    ch11file = "%s/11_%s.BT"%(fileprfx,fname)

    ch1,ok1=get_ch_projected(ch1file,CoverageData)
    ch2,ok2=get_ch_projected(ch2file,CoverageData)
    ch3,ok3=get_ch_projected(ch3file,CoverageData)
    ch4,ok4=get_ch_projected(ch4file,CoverageData)    
    ch5,ok5=get_ch_projected(ch5file,CoverageData)
    ch6,ok6=get_ch_projected(ch6file,CoverageData)
    ch7,ok7=get_ch_projected(ch7file,CoverageData)
    ch8,ok8=get_ch_projected(ch8file,CoverageData)
    ch9,ok9=get_ch_projected(ch9file,CoverageData)
    ch10,ok10=get_ch_projected(ch10file,CoverageData)
    ch11,ok11=get_ch_projected(ch11file,CoverageData)
            
    ok4r=0
    if ok4 and ok9 and ok11:
        ch4r = co2corr_bt39(ch4,ch9,ch11)
        ok4r = 1
                    
    # IR - channel 9:
    if ok9 and RGB_IMAGE[areaid]["ir9"]:
        outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_bw_ch9"%(RGBDIR_OUT,MSG_SATELLITE,year,month,day,hour,minute,areaid)
        msgwrite_log("INFO","%s product: %.4d%.2d%.2d%.2d%.2d_%s_bw_ch9"%(MSG_SATELLITE,year,month,day,hour,minute,areaid),moduleid=MODULE_ID)                
        #this = make_bw(ch9,outname,inverse=1,gamma=1.6,stretch="gamma")
        #this = make_bw(ch9,outname,inverse=1,stretch="linear")
        this = make_bw(ch9,outname,inverse=1,stretch="no",bwrange=[-70+273.15,57.5+273.15])
        # Sync the output with fileserver:
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))
            
        do_sir(this,"ir9",year,month,day,hour,minute,areaid)
                    
    # Water vapour - channel 5:
    if ok5 and RGB_IMAGE[areaid]["watervapour_high"]:
        outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_bw_ch5"%(RGBDIR_OUT,MSG_SATELLITE,year,month,day,hour,minute,areaid)
        msgwrite_log("INFO","%s product: %.4d%.2d%.2d%.2d%.2d_%s_bw_ch5"%(MSG_SATELLITE,year,month,day,hour,minute,areaid),moduleid=MODULE_ID)                
        #this = make_bw(ch5,outname,inverse=1,gamma=1.6,stretch="gamma")
        this = make_bw(ch5,outname,inverse=1,stretch="linear")
        # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))
                    
        do_sir(this,"watervapour_high",year,month,day,hour,minute,areaid)

    # Water vapour - channel 6:
    if ok6 and RGB_IMAGE[areaid]["watervapour_low"]:
        outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_bw_ch6"%(RGBDIR_OUT,MSG_SATELLITE,year,month,day,hour,minute,areaid)
        msgwrite_log("INFO","%s product: %.4d%.2d%.2d%.2d%.2d_%s_bw_ch6"%(MSG_SATELLITE,year,month,day,hour,minute,areaid),moduleid=MODULE_ID)                
        #this = make_bw(ch6,outname,inverse=1,gamma=1.6,stretch="gamma")
        this = make_bw(ch6,outname,inverse=1,stretch="linear")
        # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

        do_sir(this,"watervapour_low",year,month,day,hour,minute,areaid)

    # Daytime overview:
    if ok1 and ok2 and ok9 and RGB_IMAGE[areaid]["overview"]:
        outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_overview"%(RGBDIR_OUT,MSG_SATELLITE,year,month,day,hour,minute,areaid)
        msgwrite_log("INFO","%s product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_overview"%(MSG_SATELLITE,year,month,day,hour,minute,areaid),moduleid=MODULE_ID)
        this = makergb_visvisir(ch1,ch2,ch9,outname,gamma=(1.6,1.6,1.6))
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

        do_sir(this,"overview",year,month,day,hour,minute,areaid)

    # Daytime "green snow":
    if ok3 and ok2 and ok9 and RGB_IMAGE[areaid]["greensnow"]:
        outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_greensnow"%(RGBDIR_OUT,MSG_SATELLITE,year,month,day,hour,minute,areaid)
        msgwrite_log("INFO","%s product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_greensnow"%(MSG_SATELLITE,year,month,day,hour,minute,areaid),moduleid=MODULE_ID)
        this = makergb_visvisir(ch3,ch2,ch9,outname,gamma=(1.6,1.6,1.6))
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

        do_sir(this,"greensnow",year,month,day,hour,minute,areaid)

    # Daytime convection:
    if ok1 and ok3 and ok4 and ok5 and ok6 and ok9 and RGB_IMAGE[areaid]["convection"]:
        outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_severe_convection"%(RGBDIR_OUT,MSG_SATELLITE,year,month,day,hour,minute,areaid)
        msgwrite_log("INFO","%s product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_severe_convection"%(MSG_SATELLITE,year,month,day,hour,minute,areaid),moduleid=MODULE_ID)
        this = makergb_severe_convection(ch1,ch3,ch4,ch5,ch6,ch9,outname,gamma=(1.0,1.0,1.0),rgbrange=[(-30,0),(0,55.0),(-70.0,20.0)])
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

        do_sir(this,"convection",year,month,day,hour,minute,areaid)

    # New since October 31, 2007. Adam Dybbroe
    # Airmass - IR/WV:
    if ok5 and ok6 and ok8 and ok9 and RGB_IMAGE[areaid]["convection"]:
        outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_airmass"%(RGBDIR_OUT,MSG_SATELLITE,year,month,day,hour,minute,areaid)
        msgwrite_log("INFO","%s product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_airmass"%(MSG_SATELLITE,year,month,day,hour,minute,areaid),moduleid=MODULE_ID)
        # WV6.2 - WV7.3	                -25 till   0 K	gamma 1
        # IR9.7 - IR10.8		-40 till  +5 K	gamma 1
        # WV6.2		               +243 till 208 K	gamma 1
        this = makergb_arimass(ch5,ch6,ch8,ch9,outname,gamma=(1.0,1.0,1.0),rgbrange=[(-25,0),(-40,5.0),(243-70.0,208+20.0)])
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

    # Fog and low clouds
    if ok4r and ok9 and ok10 and RGB_IMAGE[areaid]["nightfog"]:
        outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_nightfog"%(RGBDIR_OUT,MSG_SATELLITE,year,month,day,hour,minute,areaid)
        msgwrite_log("INFO","%s product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_nightfog"%(MSG_SATELLITE,year,month,day,hour,minute,areaid),moduleid=MODULE_ID)
        this=makergb_nightfog(ch4r,ch9,ch10,outname,gamma=(1.0,2.0,1.0),rgbrange=[(-4,2),(0,6),(243,293)])
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))
            
        do_sir(this,"nightfog",year,month,day,hour,minute,areaid)
                
    if ok7 and ok9 and ok10 and RGB_IMAGE[areaid]["fog"]:
        outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_fog"%(RGBDIR_OUT,MSG_SATELLITE,year,month,day,hour,minute,areaid)
        msgwrite_log("INFO","%s product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_fog"%(MSG_SATELLITE,year,month,day,hour,minute,areaid),moduleid=MODULE_ID)
        this = makergb_fog(ch7,ch9,ch10,outname,gamma=(1.0,2.0,1.0),rgbrange=[(-4,2),(0,6),(243,283)])
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))
                
        do_sir(this,"fog",year,month,day,hour,minute,areaid)

    # "cloudtop": Low clouds, thin cirrus, nighttime
    if ok4r and ok9 and ok10 and RGB_IMAGE[areaid]["cloudtop"]:
        outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop_co2corr"%(RGBDIR_OUT,MSG_SATELLITE,year,month,day,hour,minute,areaid)
        msgwrite_log("INFO","%s product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop_co2corr"%(MSG_SATELLITE,year,month,day,hour,minute,areaid),moduleid=MODULE_ID)
        #this = makergb_cloudtop(ch4r,ch9,ch10,outname,gamma=(1.2,1.2,1.2))
        this = makergb_cloudtop(ch4r,ch9,ch10,outname,stretch="linear")
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

        do_sir(this,"cloudtop",year,month,day,hour,minute,areaid)

    return


# ------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import time
    import string

    if len(sys.argv) < 2:
        print "Usage: %s <n-slots back in time>"%(sys.argv[0])
        sys.exit(-9)
    else:
        nSlots = string.atoi(sys.argv[1])

    start_date,end_date = get_times(nSlots)
    
    # Just for testing -- Martin, 20090918
    #start_date = "200812121030"
    #end_date = "200812121045"


    msgwrite_log("INFO","Start and End times: ",
                 start_date,end_date,
                 moduleid=MODULE_ID)

    input_area_id=MSG_AREA
    MetSat=MSG_SATELLITE
    file_prefix=RGBDIR_IN
        
    lon = read_msg_lonlat(LONFILE)
    lat = read_msg_lonlat(LATFILE)

    time_start = UTC_time_from_string(start_date)
    time_end = UTC_time_from_string(end_date)

    if time_start > time_end:
        msgwrite_log("INFO","Start time is later than end time!",
                     moduleid=MODULE_ID)


        
    sec = time_start
    while (sec <= time_end):
        current_time = time.gmtime(sec)

        filename = "%.4d%.2d%.2d%.2d%.2d_C%.4d_%.4d_S%.4d_%.4d"\
                   %(current_time.tm_year,
                     current_time.tm_mon,
                     current_time.tm_mday,
                     current_time.tm_hour,
                     current_time.tm_min,
                     MSG_AREA_CENTER[0],
                     MSG_AREA_CENTER[1],
                     ROWS,
                     COLS)

        msgwrite_log("INFO","%s/*_%s*"%(file_prefix,filename),moduleid=MODULE_ID)
        
        file_list = glob.glob("%s/*_%s*"%(file_prefix,filename))
        if len(file_list) == 0:
            msgwrite_log("INFO","No files for this time: %.4d%.2d%.2d%.2d%.2d"
                         %(current_time.tm_year,
                           current_time.tm_mon,
                           current_time.tm_mday,
                           current_time.tm_hour,
                           current_time.tm_min),
                         moduleid=MODULE_ID)
            sec = sec + DSEC_SLOTS
            continue
        
        # Loop over areas:
        for output_area_id in NWCSAF_MSG_AREAS:
            doOneAreaRgbs(input_area_id,output_area_id,
                          lon,lat,
                          MetSat,
                          current_time.tm_year,
                           current_time.tm_mon,
                           current_time.tm_mday,
                           current_time.tm_hour,
                           current_time.tm_min,
                          file_prefix,filename)

        sec = sec + DSEC_SLOTS
