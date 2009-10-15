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

import glob
import datetime

# Local modules

from msg_communications import *
from msgpp_config import *
from misc_utils import *
import msg_coverage
import msg_data
import time_utils
import geo_image
from products import *

seviri_data = None

MODULE_ID="MSG_RGB_REMAP"

def usage():
    print "Usage: %s [-h,--help] [-a area] [-p product] <n-slots back in time>"%(sys.argv[0])
    sys.exit(-9)
    

if __name__ == "__main__":
    import sys
    import time
    import string
    import py_msg
    import numpy
    import getopt

    try:
        opts, args = getopt.getopt(sys.argv[1:],"ha:p:",["help"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    areas = PRODUCTS.keys()
    prods = None

    for opt, arg in opts:
        if opt in ("-h","--help"):
            usage()
            sys.exit()
        elif opt == "-a":
            areas = [arg]
        elif opt == "-p":
            prods = [arg]


    if len(args) > 1:
        usage()
        sys.exit(-9)
    elif len(args) == 0:
        import string
        msgwrite_log("INFO",
                     "No slots number specified, extrapolating... ",
                     moduleid=MODULE_ID)
        prefix="H-000-MSG?__-MSG?________-_________-EPI______-"
        match_str = "%s/import/SEVIRI_data/%s*"%(MSG_DIR,prefix)
        flist = glob.glob(match_str)
        flist.sort(reverse = True)
        tstr = flist[0][-15:-3]
        time_slots = [datetime.datetime(string.atoi(tstr[:4]),
                                        string.atoi(tstr[4:6]),
                                        string.atoi(tstr[6:8]),
                                        string.atoi(tstr[8:10]),
                                        string.atoi(tstr[10:12]))]
    else:
        n_slots = string.atoi(args[0])
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

        if("globe" in areas and
           (prods is None or
            "overview" in prods)):

            msgwrite_log("INFO",
                         "Loading global Seviri channels...",
                         moduleid=MODULE_ID)
        

        
            seviri_data = msg_data.MSGSeviriChannels(time_slot, 
                                                     "globe", 
                                                     rad = False)
            seviri_data.load([1,2,9])


            # This should be done differently. The globe area should not be
            # treated differently, but this will wait for smart remapping
            # features. -- Martin, 2009-10-07
  
            msgwrite_log("INFO",
                         "Loading done",
                         moduleid=MODULE_ID)
            
            msgwrite_log("INFO",
                         "Generating %s for area %s."%("overview","globe"),
                         moduleid=MODULE_ID)
            
            
            rgb = seviri_data.overview()
            
            if rgb is not None:
                for filename in PRODUCTS["globe"]["overview"]:
                    if(isinstance(filename,tuple) and
                       len(filename) == 2):
                        rgb.double_save(time_slot.strftime(filename[0]),
                                        time_slot.strftime(filename[1]))
                    else:
                        rgb.secure_save(time_slot.strftime(filename))
                        
        msgwrite_log("INFO",
                     "Loading Seviri channels...",
                     moduleid=MODULE_ID)
        
        seviri_data = msg_data.MSGSeviriChannels(time_slot, 
                                                 input_area_id, 
                                                 rad = False)
        seviri_data.load()

        msgwrite_log("INFO",
                     "Loading done",
                     moduleid=MODULE_ID)

            
        for akey in areas:
            if akey == "globe":
                continue
            msgwrite_log("INFO",
                         "Processing area %s."%akey,
                         moduleid=MODULE_ID)
            channels = seviri_data.project(akey)

            if prods is None:
                products = PRODUCTS[akey]
            else:
                products = list(set(PRODUCTS[akey]) &
                                set(prods))

            for pkey in products:
                if pkey in ["convection", "airmass", "overview","ir9",
                            "wv_low", "wv_high", "greensnow", "redsnow",
                            "fog", "nightfog", "cloudtop", "hr_overview"]:
                    msgwrite_log("INFO",
                                 "Generating %s for area %s."%(pkey,akey),
                                 moduleid=MODULE_ID)
                rgb = None
                if(pkey == "convection"):
                    rgb = channels.convection()
                elif(pkey == "airmass"):
                    rgb = channels.airmass()
                elif(pkey == "overview"):
                    rgb = channels.overview()
                elif(pkey == "ir9"):
                    rgb = channels.ir9()
                elif(pkey == "wv_low"):
                    rgb = channels.wv_low()
                elif(pkey == "wv_high"):
                    rgb = channels.wv_high()
                elif(pkey == "greensnow"):
                    rgb = channels.green_snow()
                elif(pkey == "redsnow"):
                    rgb = channels.red_snow()
                elif(pkey == "fog"):
                    rgb = channels.fog()
                elif(pkey == "nightfog"):
                    rgb = channels.night_fog()
                elif(pkey == "cloudtop"):
                    rgb = channels.cloudtop()
                if(pkey == "hr_overview"):
                    rgb = channels.hr_overview()

                if rgb is not None:
                    for filename in PRODUCTS[akey][pkey]:
                        if(isinstance(filename,tuple) and
                           len(filename) == 2):
                            filename0 = time_slot.strftime(filename[0])
                            filename1 = time_slot.strftime(filename[1])
                            msgwrite_log("INFO",
                                         "Saving to %s."%(filename0),
                                         moduleid=MODULE_ID)
                            msgwrite_log("INFO",
                                         "Saving to %s."%(filename1),
                                         moduleid=MODULE_ID)

                            rgb.double_save(filename0, filename1)
                        else:
                            filename0 = time_slot.strftime(filename)
                            msgwrite_log("INFO",
                                         "Saving to %s."%(filename0),
                                         moduleid=MODULE_ID)

                            rgb.secure_save(filename0)
