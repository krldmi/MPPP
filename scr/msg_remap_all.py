#
from msgpp_config import *

import _satproj
import epshdf
import area
import glob,os
import pps_array2image

from msg_ctype_remap import *
from msg_ctth_remap import *

# -----------------------------------------------------------------------
def doCloudType(cov,filename,areaid,in_aid):
    a = area.area(areaid)
    
    legend = pps_array2image.get_cms_modified()
    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")
    outfile = "%s/%s%s.h5"%(CTYPEDIR_OUT,os.path.basename(filename).split(in_aid)[0],ext)
    print outfile
    ctype=None
    if not os.path.exists(outfile):
        msgctype = read_msgCtype(filename)
        msgctype = msgCtype_remap_fast(cov,msgctype,areaid,a)
        ctype = msg_ctype2ppsformat(msgctype)
        epshdf.write_cloudtype(outfile,ctype,6)

    imagefile = outfile.split(".h5")[0] + ".png"
    thumbnail = outfile.split(".h5")[0] + ".thumbnail.png"
    if not os.path.exists(imagefile):
        if not ctype:
            ctype = epshdf.read_cloudtype(outfile,1,1,0,1)
        this = pps_array2image.cloudtype2image(ctype.cloudtype,legend)
        size=this.size
        this.save(imagefile)
        this.thumbnail((size[0]/3,size[1]/3))
        this.save(thumbnail)

    return

# -----------------------------------------------------------------------
def doCtth(cov,filename,areaid,in_aid):
    a = area.area(areaid)
    
    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")
    outfile = "%s/%s%s.h5"%(CTTHDIR_OUT,os.path.basename(filename).split(in_aid)[0],ext)
    print outfile
    if not os.path.exists(outfile):
        msgctth = read_msgCtth(filename)
        msgctth = msgCtth_remap_fast(cov,msgctth,areaid,a)
        ctth = msg_ctth2ppsformat(msgctth)
        epshdf.write_cloudtop(outfile,ctth,6)

    imagefile = outfile.split(".h5")[0] + ".png"
    thumbnail = outfile.split(".h5")[0] + ".thumbnail.png"
    if not os.path.exists(imagefile):
        this,arr = pps_array2image.ctth2image(ctth,"height")
        size=this.size
        this.save(imagefile)
        this.thumbnail((size[0]/3,size[1]/3))
        this.save(thumbnail)

    return

# -----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print "Usage: %s <area id> <start-date: yyyymmddhhmm> <end-date: yyyymmddhhmm>"%(sys.argv[0])
        sys.exit(-9)
    else:
        areaid = sys.argv[1]
        start_date = sys.argv[2]
        end_date = sys.argv[3]

    import string,time
    in_aid="CEuro"
    
    lon = read_msg_lonlat(LONFILE)
    lat = read_msg_lonlat(LATFILE)

    a=area.area(areaid)

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

    # Check for existing coverage file for the area:
    covfilename = "%s/cst/msg_coverage_%s.%s.hdf"%(APPLDIR,in_aid,areaid)
    cov = None

    if time_start > time_end:
        print "Start time is later than end time!"
        
    sec = time_start    
    while (sec < time_end + 1):
        ttup = time.gmtime(sec)
        year,month,day,hour,min,dummy,dummy,jday,dummy = ttup
        slotn = hour*4+int((min+7.5)/15)

        if not cov and not os.path.exists(covfilename):
            print "Generate MSG coverage and store in file..."
            cov = _satproj.create_coverage(a,lon,lat,1)
            writeCoverage(cov,covfilename,in_aid,areaid)
        elif not cov:
            print "Read the MSG coverage from file..."
            cov,info = readCoverage(covfilename)
            

        prefix="SAFNWC_MSG1_CT___%.2d%.3d_%.3d_%s"%(year-2000,jday,slotn,in_aid)
        match_str = "%s/%s*h5"%(CTYPEDIR_IN,prefix)
        print "file-match: ",match_str
        flist = glob.glob(match_str)
        if len(flist) > 1:
            print "ERROR: More than one matching input file: N = ",len(flist)
            continue
        elif len(flist) == 0:
            print "ERROR: No matching input file"
            continue            
        doCloudType(cov,flist[0],areaid,in_aid)

        prefix="SAFNWC_MSG1_CTTH_%.2d%.3d_%.3d_%s"%(year-2000,jday,slotn,in_aid)
        match_str = "%s/%s*h5"%(CTTHDIR_IN,prefix)
        print "file-match: ",match_str
        flist = glob.glob(match_str)
        if len(flist) > 1:
            print "ERROR: More than one matching input file: N = ",len(flist)
            continue
        elif len(flist) == 0:
            print "ERROR: No matching input file"
            continue            
        doCtth(cov,flist[0],areaid,in_aid)

        sec = sec + 3600
