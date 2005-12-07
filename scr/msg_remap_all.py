#
from msgpp_config import *

import _satproj
import epshdf
import area
import glob,os
import pps_array2image

from msg_ctype_remap import *
from msg_ctth_remap import *

from msg_remap_all_Oper import *

# -----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print "Usage: %s <start-date: yyyymmddhhmm> <end-date: yyyymmddhhmm>"%(sys.argv[0])
        sys.exit(-9)
    else:
        start_date = sys.argv[1]
        end_date = sys.argv[2]

    import string,time
    in_aid="CEuro"
    MetSat="met08"
    
    lon = read_msg_lonlat(LONFILE)
    lat = read_msg_lonlat(LATFILE)

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
        print "Start time is later than end time!"
        
    sec = time_start    
    while (sec < time_end + 1):
        ttup = time.gmtime(sec)
        year,month,day,hour,min,dummy,dummy,jday,dummy = ttup
        slotn = hour*4+int((min+7.5)/15)

        msgctype = None
        prefix="SAFNWC_MSG1_CT___%.2d%.3d_%.3d_%s"%(year-2000,jday,slotn,in_aid)
        match_str = "%s/%s*h5"%(CTYPEDIR_IN,prefix)
        print "file-match: ",match_str
        flist = glob.glob(match_str)
        if len(flist) > 1:
            print "ERROR: More than one matching input file: N = ",len(flist)
        elif len(flist) == 0:
            print "ERROR: No matching CT input file"
        else:
            # First read the original MSG file:
            print "Read MSG CT file: ",flist[0]
            msgctype = read_msgCtype(flist[0])

        msgctth = None
        prefix="SAFNWC_MSG1_CTTH_%.2d%.3d_%.3d_%s"%(year-2000,jday,slotn,in_aid)
        match_str = "%s/%s*h5"%(CTTHDIR_IN,prefix)
        print "file-match: ",match_str
        flist = glob.glob(match_str)
        if len(flist) > 1:
            print "ERROR: More than one matching input file: N = ",len(flist)
        elif len(flist) == 0:
            print "ERROR: No matching CTTH input file"
        else:
            # First read the original MSG file:
            print "Read MSG CTTH file: ",flist[0]
            msgctth = read_msgCtth(flist[0])

        if msgctype or msgctth:
            print NWCSAF_MSG_AREAS
            for areaid in NWCSAF_MSG_AREAS:
                print "Area: ",areaid
                aObj=area.area(areaid)

                # Check for existing coverage file for the area:
                covfilename = "%s/cst/msg_coverage_%s.%s.hdf"%(APPLDIR,in_aid,areaid)
                print "Coverage filename: ",covfilename
                CoverageData = None

                if not CoverageData and not os.path.exists(covfilename):
                    print "Generate MSG coverage and store in file..."
                    CoverageData = _satproj.create_coverage(aObj,lon,lat,1)
                    writeCoverage(CoverageData,covfilename,in_aid,areaid)
                elif not CoverageData:
                    print "Read the MSG coverage from file..."
                    CoverageData,info = readCoverage(covfilename)

                if msgctype:
                    doCloudType(CoverageData,msgctype,areaid,in_aid,MetSat,year,month,day,hour,min)
                if msgctth:
                    doCtth(CoverageData,msgctth,areaid,in_aid,MetSat,year,month,day,hour,min)

        sec = sec + DSEC_SLOTS


