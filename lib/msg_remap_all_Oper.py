# -*- coding: utf-8 -*-
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
# $Id: msg_remap_all_Oper.py,v 1.31 2009/05/30 21:47:39 Adam.Dybbroe Exp $
#
# $Log: msg_remap_all_Oper.py,v $
# Revision 1.31  2009/05/30 21:47:39  Adam.Dybbroe
# Using parameter list from config-file to search for suitable PGE
# output product: E.g. searching for parallax corrected first, and
# then ultimately if no parallax corrected files are available the
# original uncorrected fpge-output will be used.
#
# Revision 1.30  2009/05/29 23:28:23  Adam.Dybbroe
# import shutil
#
# Revision 1.29  2009/05/29 23:06:28  Adam.Dybbroe
# No more use of swedish letters.
# Added threading to the code. Added doOneArea function.
# Adapted to new SIR, using /local_disk/data/sir saving as a local
# repository (to be able to debug).
# Documented the code.
#
# Revision 1.28  2008/07/08 12:22:43  adybbroe
# Excluding certain slots, known to have bad quality under certain
# conditions - equinox problems.
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


import glob
import datetime

from msgpp_config import *

import epshdf
import sys

from msg_communications import *

import time_utils
import msg_data
from products import *
import msg_ctype2radar

MODULE_ID = "MSG_PROD_REMAP"

# -----------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 2:
        print "Usage: %s <n-slots back in time>"%(sys.argv[0])
        sys.exit(-9)
    elif len(sys.argv) == 2:
        import string
        n_slots = string.atoi(sys.argv[1])
        time_slots = time_utils.time_slots(n_slots)
    else:
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



    start_date = time_slots[0]
    end_date = time_slots[-1]

    msgwrite_log("INFO","Start and End times: ",start_date,end_date,moduleid=MODULE_ID)

    input_area_id=MSG_AREA
    MetSat=MSG_SATELLITE
    

    for time_slot in time_slots:

       time_string = time_utils.time_string(time_slot)
       
       msgwrite_log("INFO",
                     "Loading Seviri channels, ctype and ctth...",
                     moduleid=MODULE_ID)

       seviri_data = msg_data.MSGSeviriChannels(time_slot, 
                                                input_area_id, 
                                                rad = False)
       
       seviri_data.load([1,2,9])
       msgwrite_log("INFO",
                    "Seviri channels loaded.",
                    moduleid=MODULE_ID)
       seviri_data.load_cloudtype()
       msgwrite_log("INFO",
                     "Seviri ctype loaded.",
                     moduleid=MODULE_ID)
       seviri_data.load_ctth()
       msgwrite_log("INFO",
                    "Seviri ctth loaded.",
                    moduleid=MODULE_ID)
       
       if(seviri_data.cloudtype is None and
          seviri_data.ctth is None):
          msgwrite_log("INFO",
                       "Unable to load cloudtype and ctth, aborting.",
                       moduleid=MODULE_ID)
          continue
       msgwrite_log("INFO",
                    "Loading done",
                    moduleid=MODULE_ID)


       for akey in PRODUCTS:
          if akey == "globe":
             continue
          msgwrite_log("INFO",
                       "Processing area %s."%akey,
                       moduleid=MODULE_ID)
          channels = seviri_data.project(akey)
          
          for pkey in PRODUCTS[akey]:
             if pkey in ["PGE02", "PGE02b", "PGE02bj", "PGE02c", 
                         "PGE02cj", "PGE02d", "PGE02e", "PGE03"]:
                msgwrite_log("INFO",
                             "Generating %s for area %s."%(pkey,akey),
                             moduleid=MODULE_ID)
             rgb = None
             ctype = None
             ctth = None
             nordrad = None

             if(pkey == "PGE02"):
                rgb = channels.pge02()
             elif(pkey == "PGE02b"):
                rgb = channels.pge02b()
             elif(pkey == "PGE02bj"):
                rgb = channels.pge02b_with_overlay()
             elif(pkey == "PGE02c"):
                rgb = channels.pge02c()
             elif(pkey == "PGE02cj"):
                rgb = channels.pge02c_with_overlay()
             elif(pkey == "PGE02d"):
                rgb = channels.pge02d()
             elif(pkey == "PGE02e"):
                rgb = channels.pge02e()
             elif(pkey == "PGE03"):
                rgb = channels.pge03()
             elif(pkey == "CtypeHDF"):
                 if(isinstance(filename,tuple) and
                    len(filename) == 2):
                     channels.save_cloudtype(time_slot.strftime(filename[0]))
                     channels.save_cloudtype(time_slot.strftime(filename[1]))
                 else:
                     channels.save_cloudtype(time_slot.strftime(filename))
             elif(pkey == "CtthHDF"):
                 if(isinstance(filename,tuple) and
                    len(filename) == 2):
                     channels.save_ctth(time_slot.strftime(filename[0]))
                     channels.save_ctth(time_slot.strftime(filename[1]))
                 else:
                     channels.save_ctth(time_slot.strftime(filename))
             elif(pkey == "NordRad"):
                nordrad = channels.get_cloudtype()

             if rgb is not None:
                for filename in PRODUCTS[akey][pkey]:
                   if(isinstance(filename,tuple) and
                      len(filename) == 2):
                      rgb.double_save(time_slot.strftime(filename[0]),
                                      time_slot.strftime(filename[1]))
                   else:
                      rgb.secure_save(time_slot.strftime(filename))

             if nordrad is not None:
                for filename in PRODUCTS[akey][pkey]:
                   filename = time_slot.strftime(filename)
                   status = msg_ctype2radar.msg_writectype2nordradformat(nordrad,
                                                                         filename,
                                                                         time_string)
                   if status:
                      for tup in N2SERVERS_AND_PORTS:
                         cmdstr = "%s %s:%d %s"%(N2INJECT,tup[0],tup[1],filename)
                         msgwrite_log("INFO","Command: %s"%(cmdstr),moduleid=MODULE_ID)
                         os.system(cmdstr)
                   else:
                      msgwrite_log("ERROR","Failed writing cloudtype product for Nordrad!",moduleid=MODULE_ID)
                      msgwrite_log("INFO","Filename = %s"%(filename),moduleid=MODULE_ID)

                   
