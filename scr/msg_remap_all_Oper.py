#
from msgpp_config import *

import _satproj
import epshdf
import area
import glob,os
import pps_array2image

from msg_ctype_remap import *
from msg_ctth_remap import *

from pps_array2image import get_cms_modified
from smhi_safnwc_legends import *

# -----------------------------------------------------------------------
def inform_sir(saf_name,pge_name,areaid):
    import time,string

    informsir_params = (string.upper("%s_%s"%(saf_name[0:3],pge_name)),
                        string.upper(areaid))
    now = time.time()
    ttup = time.localtime(now)
    year_in_century = ttup[0]-(ttup[0]/100)*100
    datestr = "%.2d%.2d%.2d%.2d%.2d"%(year_in_century,ttup[1],ttup[2],ttup[3],ttup[4])
    cmdstr = "%s %s %s %s 0"%(INFORMSIR_SCRIPT,informsir_params[0],informsir_params[1],datestr)
    print "INFO","Inform SIR command: %s"%(cmdstr)
    #os.system(cmdstr)

    return
    
# -----------------------------------------------------------------------
def doCloudType(covData,msgctype,areaid,in_aid,satellite,year,month,day,hour,min):
    import string

    print "Area = ",areaid
    ctype=None
    areaObj = area.area(areaid)
        
    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")
    outfile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.cloudtype.hdf"%(CTYPEDIR_OUT,satellite,year,month,day,hour,min,areaid)
    print "Output file: ",outfile
    if not os.path.exists(outfile):
        msgctypeRem = msgCtype_remap_fast(covData,msgctype,areaid,areaObj)
        ctype = msg_ctype2ppsformat(msgctypeRem)
        epshdf.write_cloudtype(outfile,ctype,6)

    if PRODUCT_IMAGES["PGE02"].has_key(areaid):
        print PRODUCT_IMAGES["PGE02"][areaid].keys()
        for key in PRODUCT_IMAGES["PGE02"][areaid].keys():
            for imformat in PRODUCT_IMAGES["PGE02"][areaid][key]:
                imagefile = outfile.split(".hdf")[0] + "_%s.%s"%(string.lower(key),imformat)
                thumbnail = outfile.split(".hdf")[0] + "_%s.thumbnail.%s"%(string.lower(key),imformat)
                print "IMAGE FILE: ",imagefile 
                if not os.path.exists(imagefile):
                    if not ctype:
                        ctype = epshdf.read_cloudtype(outfile,1,1,0)
                    if key == "FULL":
                        legend = get_cms_modified()
                    elif key == "VV1":
                        legend = get_ctype_vv1()
                    elif key == "VV2":
                        legend = get_ctype_vv2()
                    else:
                        print "ERROR: Legend not supported!"
                        return
                
                    this = pps_array2image.cloudtype2image(ctype.cloudtype,legend)
                    size=this.size
                    this.save(imagefile)
                    this.thumbnail((size[0]/3,size[1]/3))
                    this.save(thumbnail)
                
    inform_sir("MSG","PGE02",areaid)
                    
    return

# -----------------------------------------------------------------------
def doCtth(covData,msgctth,areaid,in_aid,satellite,year,month,day,hour,min):
    import string

    print "Area = ",areaid
    ctth=None
    areaObj = area.area(areaid)

    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")

    outfile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.ctth.hdf"%(CTTHDIR_OUT,satellite,year,month,day,hour,min,areaid)
    print "Output file: ",outfile
    if not os.path.exists(outfile):
        msgctthRem = msgCtth_remap_fast(covData,msgctth,areaid,areaObj)
        ctth = msg_ctth2ppsformat(msgctthRem)
        epshdf.write_cloudtop(outfile,ctth,6)

    if PRODUCT_IMAGES["PGE03"].has_key(areaid):
        print PRODUCT_IMAGES["PGE03"][areaid].keys()
        for key in PRODUCT_IMAGES["PGE03"][areaid].keys():
            for imformat in PRODUCT_IMAGES["PGE03"][areaid][key]:
                imagefile = outfile.split(".hdf")[0] + "_%s.%s"%(string.lower(key),imformat)
                thumbnail = outfile.split(".hdf")[0] + "_%s.thumbnail.%s"%(string.lower(key),imformat)
                print "IMAGE FILE: ",imagefile 
                if not os.path.exists(imagefile):
                    if not ctth:
                        ctth = epshdf.read_cloudtop(outfile,1,1,1,0,1)                
                    if key == "HEIGHT_FULL":
                        this,arr = pps_array2image.ctth2image(ctth,"height")
                    else:
                        print "ERROR: Legend not supported!"
                        return

                    size=this.size
                    this.save(imagefile)
                    this.thumbnail((size[0]/3,size[1]/3))
                    this.save(thumbnail)
                
    inform_sir("MSG","PGE03",areaid)

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
    print "Start and End times: ",start_date,end_date

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

        prefix="SAFNWC_MSG1_CT___%.2d%.3d_%.3d_%s"%(year-2000,jday,slotn,in_aid)
        match_str = "%s/%s*h5"%(CTYPEDIR_IN,prefix)
        print "file-match: ",match_str
        flist = glob.glob(match_str)
	msgctype=None
        if len(flist) > 1:
            print "ERROR: More than one matching input file: N = ",len(flist)
        elif len(flist) == 0:
            print "ERROR: No matching input file"
        else:
            # First read the original MSG file if not already done...
            print "Read MSG CT file: ",flist[0]
            msgctype = read_msgCtype(flist[0])

        prefix="SAFNWC_MSG1_CTTH_%.2d%.3d_%.3d_%s"%(year-2000,jday,slotn,in_aid)
        match_str = "%s/%s*h5"%(CTTHDIR_IN,prefix)
        print "file-match: ",match_str
        flist = glob.glob(match_str)
	msgctth=None
        if len(flist) > 1:
            print "ERROR: More than one matching input file: N = ",len(flist)
        elif len(flist) == 0:
            print "ERROR: No matching input file"
        else:
            # First read the original MSG file if not already done...
            print "Read MSG CTTH file: ",flist[0]
            msgctth = read_msgCtth(flist[0])

	if not msgctype and not msgctth:
            sec = sec + DSEC_SLOTS
            continue

        # Loop over areas:
        for areaid in NWCSAF_MSG_AREAS:
            areaObj=area.area(areaid)

            # Check for existing coverage file for the area:
            covfilename = "%s/cst/msg_coverage_%s.%s.hdf"%(APPLDIR,in_aid,areaid)
            CoverageData = None
            
            if not CoverageData and not os.path.exists(covfilename):
                print "Generate MSG coverage and store in file..."
                CoverageData = _satproj.create_coverage(areaObj,lon,lat,1)
                writeCoverage(CoverageData,covfilename,in_aid,areaid)
            elif not CoverageData:
                print "Read the MSG coverage from file..."
                CoverageData,info = readCoverage(covfilename)

            if msgctype:
                doCloudType(CoverageData,msgctype,areaid,in_aid,MetSat,year,month,day,hour,min)
            
            if msgctth:
                doCtth(CoverageData,msgctth,areaid,in_aid,MetSat,year,month,day,hour,min)

        sec = sec + DSEC_SLOTS

    # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
    os.system("/usr/bin/rsync -crtzulv --delete /local_disk/data/Meteosat8/MesanX/*mesanX* /data/proj/saftest/nwcsafmsg/PGEs")
    
