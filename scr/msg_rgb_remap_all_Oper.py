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

# Global modules

import math
import glob
import os
import shutil
import time_utils

# PPS modules

import area

# Local modules

from msg_communications import *
from msgpp_config import *
from msg_remap_util import *
from msg_rgb_remap import *
from misc_utils import *
import msg_coverage
import msg_data

seviri_data = None

MODULE_ID="MSG_RGB_REMAP"

# ------------------------------------------------------------------

def do_sir(imIn,prodid,time_slot,areaid):
    import string
    import tempfile,os
    
    if (SIR_SIGNAL[areaid].has_key(prodid) and not SIR_SIGNAL[areaid][prodid]) or \
            not SIR_SIGNAL[areaid].has_key(prodid):
        msgwrite_log("INFO","No product requested for SIR",moduleid=MODULE_ID)
        return
    
    msgwrite_log("INFO","Product requested for SIR: %s"%SIR_DIR,moduleid=MODULE_ID)

    import msg_remap_all_Oper
    timestamp = time_utils.short_time_string(time_slot)
                    
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
    import math

    dmin_slots = DSEC_SLOTS / 60.0

    now = time.time()
    gmt_time = time.gmtime(now)
    day_hh = gmt_time[3]
    hour_mm = gmt_time[4]
    time_tup = gmt_time[0],gmt_time[1],gmt_time[2],0,0,0,0,0,0

    print int(math.ceil(dmin_slots/2.0))
    print "Hez"

    end_slot_sec1970 = time.mktime(time_tup) - time.timezone + \
                       ((hour_mm+math.ceil(dmin_slots/2.0))//dmin_slots) * \
                       dmin_slots * 60 + day_hh * 3600
    end_time = time.gmtime(end_slot_sec1970)
    start_time = time.gmtime(end_slot_sec1970 - 60 * dmin_slots * nSlots)

    end_date = "%.4d%.2d%.2d%.2d%.2d"%(end_time[0],end_time[1],end_time[2],end_time[3],end_time[4])
    start_date = "%.4d%.2d%.2d%.2d%.2d"%(start_time[0],start_time[1],start_time[2],start_time[3],start_time[4])

    return start_date,end_date


# ------------------------------------------------------------------
def doOneAreaRgbs(seviri_data,areaid,MetSat,time_slot,fileprfx):

## This looks wrong

#     outname_nf = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_nightfog"%(RGBDIR_OUT,MetSat,
#                                                                year,month,day,hour,minute,areaid)
#     outname_f = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_fog"%(RGBDIR_OUT,MetSat,
#                                                          year,month,day,hour,minute,areaid)
#     outname_ctop = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop_co2corr"%(RGBDIR_OUT,MetSat,
#                                                                          year,month,day,hour,minute,areaid)

#     if os.path.exists(outname_nf+".png") and os.path.exists(outname_f+".png") and os.path.exists(outname_ctop+".png"):
#         msgwrite_log("INFO","All rgb's have been done previously",moduleid=MODULE_ID)
#         return



    #coverage = msg_coverage.SatProjCov(in_aid, areaid, False)
    #hr_coverage = msg_coverage.SatProjCov(in_aid, areaid, True)

    msgwrite_log("INFO","Try make RGBs for this time: %s"%(time_slot),moduleid=MODULE_ID)

    channels = seviri_data.project(areaid)
    time_string = time_utils.time_string(time_slot)

    ch = channels.strip("CAL")

    ch4r = None
    if (ch[4] is not None and 
        ch[9] is not None and 
        ch[11] is not None):
        ch4r = co2corr_bt39(ch[4],ch[9],ch[11])
        ok4r = 1

    # IR - channel 9:
    if ch[9] is not None and RGB_IMAGE[areaid]["ir9"]:
        outname = "%s/%s_%s_%s_bw_ch9"%(RGBDIR_OUT,MetSat,time_string,areaid)
        msgwrite_log("INFO","%s product: %s_%s_bw_ch9"%(MetSat,time_slot,areaid),moduleid=MODULE_ID)                
        this = make_bw(ch[9],outname,inverse=1,stretch="no",bwrange=[-70+273.15,57.5+273.15])
        # Sync the output with fileserver:
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))
            
        do_sir(this,"ir9",time_slot,areaid)
                    
    # Water vapour - channel 5:
    if ch[5] is not None and RGB_IMAGE[areaid]["watervapour_high"]:
        outname = "%s/%s_%s_%s_bw_ch5"%(RGBDIR_OUT,MetSat,time_string,areaid)
        msgwrite_log("INFO","%s product: %s_%s_bw_ch5"%(MetSat,time_slot,areaid),moduleid=MODULE_ID)                
        #this = make_bw(ch5,outname,inverse=1,gamma=1.6,stretch="gamma")
        this = make_bw(ch[5],outname,inverse=1,stretch="linear")
        # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))
                    
        do_sir(this,"watervapour_high",time_slot,areaid)

    # Water vapour - channel 6:
    if ch[6] is not None and RGB_IMAGE[areaid]["watervapour_low"]:
        outname = "%s/%s_%s_%s_bw_ch6"%(RGBDIR_OUT,MetSat,time_string,areaid)
        msgwrite_log("INFO","%s product: %s_%s_bw_ch6"%(MetSat,time_slot,areaid),moduleid=MODULE_ID)                
        #this = make_bw(ch6,outname,inverse=1,gamma=1.6,stretch="gamma")
        this = make_bw(ch[6],outname,inverse=1,stretch="linear")
        # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

        do_sir(this,"watervapour_low",time_slot,areaid)

    # Daytime overview:
    if ch[1] is not None and ch[2] is not None and ch[9] is not None and RGB_IMAGE[areaid]["overview"]:
        outname = "%s/%s_%s_%s_rgb_overview"%(RGBDIR_OUT,MetSat,time_string,areaid)
        msgwrite_log("INFO","%s product: %s_%s_rgb_overview"%(MetSat,time_slot,areaid),moduleid=MODULE_ID)
        this = makergb_visvisir(ch[1],ch[2],ch[9],outname,gamma=(1.6,1.6,1.6))
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

        do_sir(this,"overview",time_slot,areaid)

    # Daytime "green snow":
    if ch[3] is not None and ch[2] is not None and ch[9] is not None and RGB_IMAGE[areaid]["greensnow"]:
        outname = "%s/%s_%s_%s_rgb_greensnow"%(RGBDIR_OUT,MetSat,time_string,areaid)
        msgwrite_log("INFO","%s product: %s_%s_rgb_greensnow"%(MetSat,time_slot,areaid),moduleid=MODULE_ID)
        this = makergb_visvisir(ch[3],ch[2],ch[9],outname,gamma=(1.6,1.6,1.6))
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

        do_sir(this,"greensnow",time_slot,areaid)

    # Daytime convection:
    if ch[1] is not None and ch[3] is not None and ch[4] is not None and ch[5] is not None and ch[6] is not None and ch[9] is not None and RGB_IMAGE[areaid]["convection"]:
        outname = "%s/%s_%s_%s_rgb_severe_convection"%(RGBDIR_OUT,MetSat,time_string,areaid)
        msgwrite_log("INFO","%s product: %s_%s_rgb_severe_convection"%(MetSat,time_slot,areaid),moduleid=MODULE_ID)
        this = makergb_severe_convection(ch[1],ch[3],ch[4],ch[5],ch[6],ch[9],outname,gamma=(1.0,1.0,1.0),rgbrange=[(-30,0),(0,55.0),(-70.0,20.0)])
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

        do_sir(this,"convection",time_slot,areaid)

    # New since October 31, 2007. Adam Dybbroe
    # Airmass - IR/WV:
    if ch[5] is not None and ch[6] is not None and ch[8] is not None and ch[9] is not None and RGB_IMAGE[areaid]["convection"]:
        outname = "%s/%s_%s_%s_rgb_airmass"%(RGBDIR_OUT,MetSat,time_string,areaid)
        msgwrite_log("INFO","%s product: %s_%s_rgb_airmass"%(MetSat,time_slot,areaid),moduleid=MODULE_ID)
        # WV6.2 - WV7.3	                -25 till   0 K	gamma 1
        # IR9.7 - IR10.8		-40 till  +5 K	gamma 1
        # WV6.2		               +243 till 208 K	gamma 1
        this = makergb_airmass(ch[5],ch[6],ch[8],ch[9],outname,gamma=(1.0,1.0,1.0),rgbrange=[(-25,0),(-40,5.0),(243-70.0,208+20.0)])
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

    # Fog and low clouds
    if ch4r is not None and ch[9] is not None and ch[10] is not None and RGB_IMAGE[areaid]["nightfog"]:
        outname = "%s/%s_%s_%s_rgb_nightfog"%(RGBDIR_OUT,MetSat,time_string,areaid)
        msgwrite_log("INFO","%s product: %s_%s_rgb_nightfog"%(MetSat,time_slot,areaid),moduleid=MODULE_ID)
        this=makergb_nightfog(ch4r,ch[9],ch[10],outname,gamma=(1.0,2.0,1.0),rgbrange=[(-4,2),(0,6),(243,293)])
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))
            
        do_sir(this,"nightfog",time_slot,areaid)
                
    if ch[7] is not None and ch[9] is not None and ch[10] is not None and RGB_IMAGE[areaid]["fog"]:
        outname = "%s/%s_%s_%s_rgb_fog"%(RGBDIR_OUT,MetSat,time_string,areaid)
        msgwrite_log("INFO","%s product: %s_%s_rgb_fog"%(MetSat,time_slot,areaid),moduleid=MODULE_ID)
        this = makergb_fog(ch[7],ch[9],ch[10],outname,gamma=(1.0,2.0,1.0),rgbrange=[(-4,2),(0,6),(243,283)])
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))
                
        do_sir(this,"fog",time_slot,areaid)

    # "cloudtop": Low clouds, thin cirrus, nighttime
    if ch4r is not None and ch[9] is not None and ch[10] is not None and RGB_IMAGE[areaid]["cloudtop"]:
        outname = "%s/%s_%s_%s_rgb_cloudtop_co2corr"%(RGBDIR_OUT,MetSat,time_string,areaid)
        msgwrite_log("INFO","%s product: %s_%s_rgb_cloudtop_co2corr"%(MetSat,time_slot,areaid),moduleid=MODULE_ID)
        this = makergb_cloudtop(ch4r,ch[9],ch[10],outname,stretch="linear")
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

        do_sir(this,"cloudtop",time_slot,areaid)

    # High resolution daytime overview
    if ch[1] is not None and ch[2] is not None and ch[9] is not None and ch[12] is not None and RGB_IMAGE[areaid]["hr_overview"]:
        outname = "%s/%s_%s_%s_rgb_hr_overview"%(RGBDIR_OUT,MetSat,time_string,areaid)
        msgwrite_log("INFO","%s product: %s_%s_rgb_hr_overview"%(MetSat,time_slot,areaid),moduleid=MODULE_ID)
        
        this = makergb_hrovw(ch[1], ch[2], ch[9], ch[12], outname, gamma=(1.6,1.6,1.6))
        if FSERVER_SYNC:
            os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

        do_sir(this,"hr_overview",time_slot,areaid)


    return


def doGlobe(time_slot):
    import Image

    time_string = time_utils.time_string(time_slot)

    print time_string

    outname = "%s/%s_%s_%s_rgb_overview.png"%(RGBDIR_OUT,MSG_SATELLITE,time_string,"globe")
    msgwrite_log("INFO","%s product: %s_%s_rgb_overview"%(MSG_SATELLITE,time_string,"globe"),moduleid=MODULE_ID)
    
    ch1 = msg_data.MSGChannel(time_slot, "globe","1",rad = False)
    ch2 = msg_data.MSGChannel(time_slot, "globe","2",rad = False)
    ch9 = msg_data.MSGChannel(time_slot, "globe","9",rad = False)

    if((ch1 is None) or (ch2 is None) or (ch9 is None)):
        return

    ch1 = msg_data.normalizeArray(ch1.component("CAL"),255)
    im1 = Image.fromarray(ch1.astype(numpy.uint8),"L")

    ch2 = msg_data.normalizeArray(ch2.component("CAL"),255)
    im2 = Image.fromarray(ch2.astype(numpy.uint8),"L")

    ch9i = msg_data.normalizeArray(ch9.component("CAL",inverted = True),255)
    im9i = Image.fromarray(ch9i.astype(numpy.uint8),"L")

    im = Image.merge("RGB",(im1,im2,im9i))
    im.save(outname)



# ------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import time
    import string
    import py_msg
    import numpy

    if len(sys.argv) < 2:
        print "Usage: %s <n-slots back in time>"%(sys.argv[0])
        sys.exit(-9)
    else:
        n_slots = string.atoi(sys.argv[1])

    time_slots = time_utils.time_slots(n_slots,DSEC_SLOTS/60)

    start_date = time_slots[0]
    end_date = time_slots[-1]

    msgwrite_log("INFO","Start and End times: ",
                 start_date,end_date,
                 moduleid=MODULE_ID)

    input_area_id=MSG_AREA
    MetSat=MSG_SATELLITE
    file_prefix=RGBDIR_IN
        
    for time_slot in time_slots:

        doGlobe(time_slot)
        
        seviri_data = msg_data.MSGSeviriChannels(time_slot, 
                                                 input_area_id, 
                                                 rad = False)


        # Loop over areas:
        for output_area_id in NWCSAF_MSG_AREAS:
            doOneAreaRgbs(seviri_data,
                          output_area_id,
                          MetSat,
                          time_slot,
                          file_prefix)

