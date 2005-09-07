
from msgpp_config import *
from msg_remap_util import *
from msg_rgb_remap import *
#
import _satproj
import area
import glob,os


# ------------------------------------------------------------------
def get_times(nSlots):
    # Get the start and end times for the slots, where the time of the last slot
    # is close to now, and the start slot is nSlots earlier:
    
    import time
    now = time.time()
    gmt_time = time.gmtime(now)
    day_hh = gmt_time[3]
    hour_mm = gmt_time[4]
    time_tup = gmt_time[0],gmt_time[1],gmt_time[2],0,0,0,0,0,0
    end_slot_sec1970 = time.mktime(time_tup) - time.timezone + ((hour_mm+8)/15) * 15 * 60 + day_hh * 3600
    end_time = time.gmtime(end_slot_sec1970)
    start_time = time.gmtime(end_slot_sec1970 - 3600*15*nSlots)

    end_date = "%.4d%.2d%.2d%.2d%.2d"%(end_time[0],end_time[1],end_time[2],end_time[3],end_time[4])
    start_date = "%.4d%.2d%.2d%.2d%.2d"%(start_time[0],start_time[1],start_time[2],start_time[3],start_time[4])

    return start_date,end_date

# ------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print "Usage: %s <area id> <n-slots back in time>"%(sys.argv[0])
        sys.exit(-9)
    else:
        areaid = sys.argv[1]
        import string
        nSlots = string.atoi(sys.argv[2])

    start_date,end_date = get_times(nSlots)

    import os,time
    in_aid="CEuro"
    MetSat="met08"
    
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
    if not os.path.exists(covfilename):
        cov = _satproj.create_coverage(a,lon,lat,1)
        writeCoverage(cov,covfilename,in_aid,areaid)
    else:
        cov,info = readCoverage(covfilename)
        print info.items()

    sec = time_start
    while (sec < time_end + 1):
        ttup = time.gmtime(sec)
        year,month,day,hour,min,dummy,dummy,dummy,dummy = ttup

        #fileprfx="%s/%.4d/%.2d/%.2d"%(RGBDIR_IN,year,month,day)
        fileprfx=RGBDIR_IN
        fname = "%.4d%.2d%.2d%.2d%.2d_C0429_1999_S0700_0900"%(year,month,day,hour,min)
        print "%s/*_%s*"%(fileprfx,fname)
        
        fl = glob.glob("%s/*_%s*"%(fileprfx,fname))
        if len(fl) == 0:
            print "No files for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,min)
        else:
            outname_nf = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_nightfog"%(MetSat,RGBDIR_OUT,
                                                                       year,month,day,hour,min,areaid)
            outname_f = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_fog"%(MetSat,RGBDIR_OUT,
                                                                 year,month,day,hour,min,areaid)
            outname_ctop = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop_co2corr"%(MetSat,RGBDIR_OUT,
                                                                                 year,month,day,hour,min,areaid)
            #print outname_nf
            #print outname_f
            #print outname_ctop
            
            if os.path.exists(outname_nf+".png") and os.path.exists(outname_f+".png") and os.path.exists(outname_ctop+".png"):
                print "All rgb's have been done previously"
                sec = sec + DSEC_SLOTS
                continue
            
            print "Try make RGBs for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,min)

            ch1file = "%s/1_%s.REF"%(fileprfx,fname)
            ch3file = "%s/3_%s.REF"%(fileprfx,fname)
            ch4file = "%s/4_%s.BT"%(fileprfx,fname)    
            ch5file = "%s/5_%s.BT"%(fileprfx,fname)
            ch6file = "%s/6_%s.BT"%(fileprfx,fname)
            ch7file = "%s/7_%s.BT"%(fileprfx,fname)
            ch9file = "%s/9_%s.BT"%(fileprfx,fname)
            ch10file = "%s/10_%s.BT"%(fileprfx,fname)
            ch11file = "%s/11_%s.BT"%(fileprfx,fname)

            ch1,ok1=get_ch_projected(ch1file,cov)
            ch3,ok3=get_ch_projected(ch3file,cov)
            ch4,ok4=get_ch_projected(ch4file,cov)    
            ch5,ok5=get_ch_projected(ch5file,cov)
            ch6,ok6=get_ch_projected(ch6file,cov)
            ch7,ok7=get_ch_projected(ch7file,cov)
            ch9,ok9=get_ch_projected(ch9file,cov)
            ch10,ok10=get_ch_projected(ch10file,cov)
            ch11,ok11=get_ch_projected(ch11file,cov)

            ok4r=0
            if ok4 and ok9 and ok11:
                ch4r = co2corr_bt39(ch4,ch9,ch11)
                ok4r = 1

            """
            # Daytime convection:
            if ok1 and ok3 and ok4 and ok5 and ok6 and ok9:
                outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_severe_convection"%(MetSat,RGBDIR_OUT,year,month,day,hour,min,areaid)
                makergb_severe_convection(ch1,ch3,ch4,ch5,ch6,ch9,outname)
            """
            
            # Fog and low clouds
            if ok4r and ok9 and ok10:
                outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_nightfog"%(MetSat,RGBDIR_OUT,year,month,day,hour,min,areaid)
                if not os.path.exists(outname+".png"):
                    makergb_nightfog(ch4r,ch9,ch10,outname)
                else:
                    print "File %s already there"%outname
            if ok7 and ok9 and ok10:
                outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_fog"%(MetSat,RGBDIR_OUT,year,month,day,hour,min,areaid)
                if not os.path.exists(outname+".png"):
                    makergb_fog(ch7,ch9,ch10,outname)
                else:
                    print "File %s already there"%outname

            """
            # "red snow": Low clouds and snow daytime
            if ok1 and ok3 and ok9:
                outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_redsnow_016"%(MetSat,RGBDIR_OUT,year,month,day,hour,min,areaid)
                makergb_redsnow(ch1,ch3,ch9,outname)

            # "cloudtop": Low clouds, thin cirrus, nighttime
            if ok4 and ok9 and ok10:
                outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop"%(MetSat,RGBDIR_OUT,year,month,day,hour,min,areaid)
                makergb_cloudtop(ch4,ch9,ch10,outname)
            """
            if ok4r and ok9 and ok10:
                outname = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop_co2corr"%(MetSat,RGBDIR_OUT,year,month,day,hour,min,areaid)
                if not os.path.exists(outname+".png"):
                    makergb_cloudtop(ch4r,ch9,ch10,outname)
                else:
                    print "File %s already there"%outname
            
        #sec = sec + 3600
        sec = sec + DSEC_SLOTS

    # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
    os.system("/usr/bin/rsync -crtzulv --delete /local_disk/data/Meteosat8/RGBs/ /data/proj/saftest/nwcsafmsg/RGBs")
