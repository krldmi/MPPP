#
from msgpp_config import *

import _satproj
import epshdf
import area
import glob,os
import pps_array2image

from msg_ctype_remap import *
from msg_ctth_remap import *
from msg_rgb_remap import *

from pps_array2image import get_cms_modified
from smhi_safnwc_legends import *

# -----------------------------------------------------------------------
def inform_sir(saf_name,pge_name,aidstr,status,datestr):
    import string

    print "INFO","inside inform_sir..."
    print "INFO","aidstr=%s"%aidstr
    informsir_params = (string.upper("%s_%s"%(saf_name[0:3],pge_name)),string.upper(aidstr))
    print "INFO","informsir_params: ",informsir_params
    cmdstr = "%s %s %s %s %d"%(INFORMSIR_SCRIPT,informsir_params[0],informsir_params[1],datestr,status)
    print "INFO","Inform SIR command: %s"%(cmdstr)
    os.system(cmdstr)

    return
    
# -----------------------------------------------------------------------
def doCloudType(covData,msgctype,areaid,in_aid,satellite,year,month,day,hour,min):
    import string

    print "Area = ",areaid
    ctype=None
    areaObj = area.area(areaid)

    yystr = ("%.4d"%year)[2:4]
    timestamp = "%s%.2d%.2d%.2d%.2d"%(yystr,month,day,hour,min)
    
    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")
    outfile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.cloudtype.hdf"%(CTYPEDIR_OUT,satellite,year,month,day,hour,min,areaid)
    print "Output file: ",outfile
    if not os.path.exists(outfile):
        msgctypeRem = msgCtype_remap_fast(covData,msgctype,areaid,areaObj)
        ctype = msg_ctype2ppsformat(msgctypeRem)
        epshdf.write_cloudtype(outfile,ctype,6)

    imagelist = glob.glob("%s*.png"%string.split(outfile,".hdf")[0])
    nrgbs = len(imagelist)
    print "INFO","Number of images already there: ",nrgbs
    if nrgbs >= 2:
        return

    # Make images to distribute via SIR for forecasters and others:
    if EXTRA_IMAGE_FORMATS.has_key(areaid) and "PGE02" in EXTRA_IMAGE_FORMATS[areaid].keys() and \
           len(EXTRA_IMAGE_FORMATS[areaid]["PGE02"]) > 0 and os.path.exists(outfile):
        # Make (extra) image(s) of the result:        
        print "INFO","Make (extra) Cloud Type images for SMHI from the hdf5"
        for legend_name in PGE02_LEGEND_NAMES[areaid]:
            print "INFO","Call cloudtype2image"
            print "INFO","Pallete type: %s"%(legend_name)
            legend = PGE02_LEGENDS[legend_name]
            if not ctype:
                ctype = epshdf.read_cloudtype(outfile,1,0,0)
                
            im = pps_array2image.cloudtype2image(ctype.cloudtype,legend)
            print "INFO","image instance created..."
            
            for imformat in EXTRA_IMAGE_FORMATS[areaid]["PGE02"]:
                print "INFO","File time stamp = %s"%timestamp
                aidstr=string.ljust(areaid,8).replace(" ","_") # Pad with "_" up to 8 characters
                prodid=string.ljust(PGE02_SIR_NAMES[legend_name],4).replace(" ","_") # Pad with "_" up to 4 characters
                outname = "%s/msg_%s%s%s.%s"%(SIR_DIR,prodid,aidstr,timestamp,imformat)
                print "INFO","Image file name to SIR = %s"%outname
                if PGE02_SIR_NAMES.has_key(legend_name):
                    sir_stat=0
                    try:
                        im.save(outname,FORMAT=imformat,quality=100)
                    except:
                        print "INFO","Couldn't make image of specified format: ",imformat                        
                        sir_stat=-1
                        pass
                    if os.path.exists(outname):
                        os.rename(outname,outname.split(imformat)[0]+imformat+"_original")
                    inform_sir("MSG",PGE02_SIR_NAMES[legend_name],areaid,sir_stat,timestamp)
                else:
                    print "INFO","No product to SIR for this legend: %s"%(legend_name)
    
    # Make standard images:
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
                    if PGE02_LEGENDS.has_key(key):
                        this = pps_array2image.cloudtype2image(ctype.cloudtype,PGE02_LEGENDS[key])
                        size=this.size
                        this.save(imagefile)
                        this.thumbnail((size[0]/3,size[1]/3))
                        this.save(thumbnail)
                    else:
                        print "ERROR","Failed generating image file"
                        print "INFO: Legend not supported!"
                    
    # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
    os.system("/usr/bin/rsync -crzulv /local_disk/data/Meteosat8/MesanX/%s* /data/proj/saftest/nwcsafmsg/PGEs/."%(os.path.basename(outfile).split(".hdf")[0]))

    return

# -----------------------------------------------------------------------
def doCtth(covData,msgctth,areaid,in_aid,satellite,year,month,day,hour,min):
    import string

    print "Area = ",areaid
    ctth=None
    areaObj = area.area(areaid)
    yystr = ("%.4d"%year)[2:4]
    timestamp = "%s%.2d%.2d%.2d%.2d"%(yystr,month,day,hour,min)
    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")

    outfile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.ctth.hdf"%(CTTHDIR_OUT,satellite,year,month,day,hour,min,areaid)
    print "Output file: ",outfile
    if not os.path.exists(outfile):
        msgctthRem = msgCtth_remap_fast(covData,msgctth,areaid,areaObj)
        ctth = msg_ctth2ppsformat(msgctthRem)
        epshdf.write_cloudtop(outfile,ctth,6)

    imagelist = glob.glob("%s*.png"%string.split(outfile,".hdf")[0])
    nrgbs = len(imagelist)
    print "INFO","Number of images already there: ",nrgbs
    if nrgbs >= 2:
        return
    
    # Make images to distribute via SIR for forecasters and others:
    if EXTRA_IMAGE_FORMATS.has_key(areaid) and "PGE03" in EXTRA_IMAGE_FORMATS[areaid].keys() and \
           len(EXTRA_IMAGE_FORMATS[areaid]["PGE03"]) > 0 and os.path.exists(outfile):
        # Make (extra) image(s) of the result:        
        print "INFO","Make (extra) CTTH images for SMHI from the hdf5"
        for legend_name in PGE03_LEGEND_NAMES[areaid]:
            print "INFO","Pallete type: %s"%(legend_name)
            if not ctth:
                ctth=epshdf.read_cloudtop(outfile,1,1,1,0,1)

            this,arr = pps_array2image.ctth2image(ctth,PGE03_LEGENDS[legend_name])
            print "INFO","image instance created..."
            
            for imformat in EXTRA_IMAGE_FORMATS[areaid]["PGE03"]:
                print "INFO","File time stamp = %s"%timestamp
                aidstr=string.ljust(areaid,8).replace(" ","_") # Pad with "_" up to 8 characters
                prodid=string.ljust(PGE03_SIR_NAMES[legend_name],4).replace(" ","_") # Pad with "_" up to 4 characters
                outname = "%s/msg_%s%s%s.%s"%(SIR_DIR,prodid,aidstr,timestamp,imformat)
                print "INFO","Image file name to SIR = %s"%outname
                if PGE03_SIR_NAMES.has_key(legend_name):
                    sir_stat=0
                    try:
                        this.save(outname,FORMAT=imformat,quality=100)
                    except:
                        print "INFO","Couldn't make image of specified format: ",imformat                        
                        sir_stat=-1
                        pass
                    if os.path.exists(outname):
                        os.rename(outname,outname.split(imformat)[0]+imformat+"_original")
                    inform_sir("MSG",PGE03_SIR_NAMES[legend_name],areaid,sir_stat,timestamp)
                else:
                    print "INFO","No product to SIR for this legend: %s"%(legend_name)
    
    # Make standard images:
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
                    if PGE03_LEGENDS.has_key(key):
                        this,arr = pps_array2image.ctth2image(ctth,PGE03_LEGENDS[key])
                        size=this.size
                        this.save(imagefile)
                        this.thumbnail((size[0]/3,size[1]/3))
                        this.save(thumbnail)
                    else:
                        print "ERROR","Failed generating image file"
                        print "INFO: Legend not supported!"

    # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
    os.system("/usr/bin/rsync -crzulv /local_disk/data/Meteosat8/MesanX/%s* /data/proj/saftest/nwcsafmsg/PGEs/."%(os.path.basename(outfile).split(".hdf")[0]))

    return

# -----------------------------------------------------------------------
def doCprod01(cov,areaid,in_aid,satellite,year,month,day,hour,min):
    import string
    import make_ctype_products

    fileprfx="%s/%.4d/%.2d/%.2d"%(RGBDIR_IN,year,month,day)
    fname = "%.4d%.2d%.2d%.2d%.2d_C%.4d_%.4d_S%.4d_%.4d"%(year,month,day,hour,min,MSG_AREA_CENTER[0],MSG_AREA_CENTER[1],ROWS,COL)

    fl = glob.glob("%s/*_%s*"%(fileprfx,fname))
    if len(fl) == 0:
        print "No files for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,min)
    else:
        print "Try extract SEVIRI channel(s) for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,min)

    ch9file = "%s/9_%s.BT"%(fileprfx,fname)
    ch9,ok9=get_ch_projected(ch9file,cov)

    if not ok9:
        print "ERROR: Failed extracting SEVIRI channel 9 data"
        sys.exit(-9)

    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")
    ctypefile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.cloudtype.hdf"%(CTYPEDIR_OUT,satellite,year,month,day,hour,min,areaid)
    print "Output file: ",ctypefile

    make_ctype_prod01(ch9,ctypefile,areaid,gamma=1.6,overlay=1)
    
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
    in_aid=MSG_AREA
    MetSat=MSG_SATELLITE
    
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
                doCprod01(CoverageData,areaid,in_aid,MetSat,year,month,day,hour,min)
                
            if msgctth:
                doCtth(CoverageData,msgctth,areaid,in_aid,MetSat,year,month,day,hour,min)

        sec = sec + DSEC_SLOTS

    # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
    #os.system("/usr/bin/rsync -crzulv --delete /local_disk/data/Meteosat8/MesanX/ /data/proj/saftest/nwcsafmsg/PGEs")
    
