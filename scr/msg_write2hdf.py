# -*- coding: UTF-8 -*-
# **************************************************************************
#
#  COPYRIGHT   : SMHI
#  PRODUCED BY : Swedish Meteorological and Hydrological Institute (SMHI)
#                Folkborgsvaegen 1
#                Norrkoping, Sweden
#
#  PROJECT      : 
#  FILE         : msg_write2hdf.py
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
# $Id: msg_write2hdf.py,v 1.3 2009/05/29 22:14:46 Adam.Dybbroe Exp $
#
# $Log: msg_write2hdf.py,v $
# Revision 1.3  2009/05/29 22:14:46  Adam.Dybbroe
# Removed swedish characters.
#
# Revision 1.2  2007/10/31 22:22:37  adybbroe
# Using SEVIRI_CHANNELS_IN_HDF5 instead of hardcoded path.
#
# Revision 1.1  2007/10/30 14:39:39  adybbroe
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
#
from msg_communications import *

from msgpp_config import *
from msg_remap_util import *
#
import _satproj
import area
import glob,os

MODULE_ID = "WRITE2HDF"

from msg_rgb_remap import *

# ------------------------------------------------------------------
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

    import os,time
    in_aid=MSG_AREA
    MetSat=MSG_SATELLITE

    year=string.atoi(start_date[0:4])
    month=string.atoi(start_date[4:6])
    day=string.atoi(start_date[6:8])
    hour=string.atoi(start_date[8:10])
    min=string.atoi(start_date[10:12])    
    time_start = time.mktime((year,month,day,hour,min,0,0,0,0)) - time.timezone

    year=string.atoi(end_date[0:4])
    month=string.atoi(end_date[4:6])
    day=string.atoi(end_date[6:8])
    hour=string.atoi(end_date[8:10])
    min=string.atoi(end_date[10:12])    
    time_end = time.mktime((year,month,day,hour,min,0,0,0,0)) - time.timezone

    if time_start > time_end:
        msgwrite_log("INFO","Start time is later than end time!",moduleid=MODULE_ID)
        
    fileprfx_out=SEVIRI_CHANNELS_IN_HDF5

    sec = time_start
    while (sec < time_end + 1):
        ttup = time.gmtime(sec)
        year,month,day,hour,min,dummy,dummy,dummy,dummy = ttup
        fileprfx=RGBDIR_IN
        fname = "%.4d%.2d%.2d%.2d%.2d_C%.4d_%.4d_S%.4d_%.4d"%(year,month,day,hour,min,MSG_AREA_CENTER[0],MSG_AREA_CENTER[1],ROWS,COLS)
        msgwrite_log("INFO","%s/*_%s*"%(fileprfx,fname),moduleid=MODULE_ID)
        
        fl = glob.glob("%s/*_%s*"%(fileprfx,fname))
        if len(fl) == 0:
            msgwrite_log("INFO","No files for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,min),moduleid=MODULE_ID)
            sec = sec + DSEC_SLOTS
            continue
        
        # Sun angles:
        sunzenfile = "%s/%s.SUN_ZEN"%(fileprfx,fname)
        sunazimuthfile = "%s/%s.SUN_AZI"%(fileprfx,fname)

        # Sat angles:
        fname_satangles = "C%.4d_%.4d_S%.4d_%.4d"%(MSG_AREA_CENTER[0],MSG_AREA_CENTER[1],ROWS,COLS)
        satzenfile = "%s/%s.SAT_ZEN"%(fileprfx,fname_satangles)
        satazimuthfile = "%s/%s.SAT_AZI"%(fileprfx,fname_satangles)

        # Geolocation:
        lonfile = "%s/%s.LON"%(fileprfx,fname_satangles)
        latfile = "%s/%s.LAT"%(fileprfx,fname_satangles)

        ch1file = "%s/1_%s.REF"%(fileprfx,fname)
        ch2file = "%s/2_%s.REF"%(fileprfx,fname)
        ch3file = "%s/3_%s.REF"%(fileprfx,fname)
        ch4file = "%s/4_%s.BT"%(fileprfx,fname)    
        ch5file = "%s/5_%s.BT"%(fileprfx,fname)
        ch6file = "%s/6_%s.BT"%(fileprfx,fname)
        ch7file = "%s/7_%s.BT"%(fileprfx,fname)
        ch9file = "%s/9_%s.BT"%(fileprfx,fname)
        ch10file = "%s/10_%s.BT"%(fileprfx,fname)
        ch11file = "%s/11_%s.BT"%(fileprfx,fname)
    
        sunangles_outname = "%s/%s_sunangles.h5"%(fileprfx_out,fname)
        if not os.path.exists(sunangles_outname):
            sunzen = read_msg_lonlat(sunzenfile)
            sunazi = read_msg_lonlat(sunazimuthfile)
            status = sunsat_angles2hdf(sunangles_outname,sunzen,sunazi,"sun")

        satangles_outname = "%s/%s_satangles.h5"%(fileprfx_out,fname_satangles)
        if not os.path.exists(satangles_outname):
            satzen = read_msg_lonlat(satzenfile)
            satazi = read_msg_lonlat(satazimuthfile)
            status = sunsat_angles2hdf(satangles_outname,satzen,satazi,"sat")

        lonlat_outname = "%s/%s_lonlat.h5"%(fileprfx_out,fname_satangles)
        if not os.path.exists(lonlat_outname):
            lon = read_msg_lonlat(lonfile)
            lat = read_msg_lonlat(latfile)
            status = lonlat2hdf(lonlat_outname,lon,lat)

        ch1outname = "%s/1_%s.h5"%(fileprfx_out,fname)
        if not os.path.exists(ch1outname):
            ch_raw = read_msg_lonlat(ch1file)
            status = raw_channel2hdf(ch1outname,(ch_raw,),1,"REF")

        ch2outname = "%s/2_%s.h5"%(fileprfx_out,fname)
        if not os.path.exists(ch2outname):
            ch_raw = read_msg_lonlat(ch2file)
            status = raw_channel2hdf(ch2outname,(ch_raw,),2,"REF")

        ch3outname = "%s/3_%s.h5"%(fileprfx_out,fname)
        if not os.path.exists(ch3outname):
            ch_raw = read_msg_lonlat(ch3file)
            status = raw_channel2hdf(ch3outname,(ch_raw,),3,"REF")

        ch4outname = "%s/4_%s.h5"%(fileprfx_out,fname)
        if not os.path.exists(ch4outname):
            ch_raw = read_msg_lonlat(ch4file)
            ch_raw_rad = read_msg_lonlat("%s.RAD"%(string.split(ch4file,".BT")[0]))
            status = raw_channel2hdf(ch4outname,(ch_raw,ch_raw_rad),4,"BT")

        ch5outname = "%s/5_%s.h5"%(fileprfx_out,fname)
        if not os.path.exists(ch5outname):
            ch_raw = read_msg_lonlat(ch5file)
            ch_raw_rad = read_msg_lonlat("%s.RAD"%(string.split(ch5file,".BT")[0]))
            status = raw_channel2hdf(ch5outname,(ch_raw,ch_raw_rad),5,"BT")

        ch6outname = "%s/6_%s.h5"%(fileprfx_out,fname)
        if not os.path.exists(ch6outname):
            ch_raw = read_msg_lonlat(ch6file)
            ch_raw_rad = read_msg_lonlat("%s.RAD"%(string.split(ch6file,".BT")[0]))
            status = raw_channel2hdf(ch6outname,(ch_raw,ch_raw_rad),6,"BT")

        ch7outname = "%s/7_%s.h5"%(fileprfx_out,fname)
        if not os.path.exists(ch7outname):
            ch_raw = read_msg_lonlat(ch7file)
            ch_raw_rad = read_msg_lonlat("%s.RAD"%(string.split(ch7file,".BT")[0]))
            status = raw_channel2hdf(ch7outname,(ch_raw,ch_raw_rad),7,"BT")

        ch9outname = "%s/9_%s.h5"%(fileprfx_out,fname)
        if not os.path.exists(ch9outname):
            ch_raw = read_msg_lonlat(ch9file)
            ch_raw_rad = read_msg_lonlat("%s.RAD"%(string.split(ch9file,".BT")[0]))
            status = raw_channel2hdf(ch9outname,(ch_raw,ch_raw_rad),9,"BT")

        ch10outname = "%s/10_%s.h5"%(fileprfx_out,fname)
        if not os.path.exists(ch10outname):
            ch_raw = read_msg_lonlat(ch10file)
            ch_raw_rad = read_msg_lonlat("%s.RAD"%(string.split(ch10file,".BT")[0]))
            status = raw_channel2hdf(ch10outname,(ch_raw,ch_raw_rad),10,"BT")

        ch11outname = "%s/11_%s.h5"%(fileprfx_out,fname)
        if not os.path.exists(ch11outname):
            ch_raw = read_msg_lonlat(ch11file)
            ch_raw_rad = read_msg_lonlat("%s.RAD"%(string.split(ch11file,".BT")[0]))
            status = raw_channel2hdf(ch11outname,(ch_raw,ch_raw_rad),11,"BT")

        sec = sec + DSEC_SLOTS
