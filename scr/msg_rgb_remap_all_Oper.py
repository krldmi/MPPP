from msg_communications import *

from msgpp_config import *
from msg_remap_util import *
from msg_rgb_remap import *
#
import _satproj
import area
import glob,os

MODULE_ID="MSG_RGB_REMAP"

# ------------------------------------------------------------------
def do_sir(imIn,prodid,year,month,day,hour,min,areaid):
    if SIR_SIGNAL[areaid].has_key(prodid) and not SIR_SIGNAL[areaid][prodid] or \
       not SIR_SIGNAL[areaid].has_key(prodid):
        msgwrite_log("INFO","No product requested for SIR",moduleid=MODULE_ID)
        return
    
    msgwrite_log("INFO","Product requested for SIR: %s"%SIR_DIR,moduleid=MODULE_ID)

    import msg_remap_all_Oper
    yystr = ("%.4d"%year)[2:4]
    timestamp = "%s%.2d%.2d%.2d%.2d"%(yystr,month,day,hour,min)
                    
    for name_format in SIR_PRODUCTS[areaid][prodid]:
        prodname=name_format[0]
        imformat=name_format[1]
        msgwrite_log("INFO","File time stamp = %s"%timestamp,moduleid=MODULE_ID)
        aidstr=string.ljust(areaid,8).replace(" ","_") # Pad with "_" up to 8 characters
        prodid=string.ljust(prodname,8).replace(" ","_") # Pad with "_" up to 8 characters
        outname = "%s/%s%s%s.%s"%(SIR_DIR,prodid,aidstr,timestamp,imformat)
        msgwrite_log("INFO","Image file name to SIR = %s"%outname,moduleid=MODULE_ID)

        sir_stat=0
        try:
            imIn.save(outname,FORMAT=imformat,quality=100)
        except:
            msgwrite_log("ERROR","Couldn't make image of specified format: ",imformat,moduleid=MODULE_ID)
            sir_stat=-1
            pass
        if os.path.exists(outname):
            os.rename(outname,outname.split(imformat)[0]+imformat+"_original")
            msg_remap_all_Oper.inform_sir2(prodid,areaid,sir_stat,timestamp)
        else:
            msgwrite_log("INFO","No product to SIR",moduleid=MODULE_ID)

    return

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
    start_time = time.gmtime(end_slot_sec1970 - 60*15*nSlots)

    end_date = "%.4d%.2d%.2d%.2d%.2d"%(end_time[0],end_time[1],end_time[2],end_time[3],end_time[4])
    start_date = "%.4d%.2d%.2d%.2d%.2d"%(start_time[0],start_time[1],start_time[2],start_time[3],start_time[4])

    return start_date,end_date

# ------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Usage: %s <n-slots back in time>"%(sys.argv[0])
        sys.exit(-9)
    else:
        import string
        nSlots = string.atoi(sys.argv[1])

    start_date,end_date = get_times(nSlots)
    msgwrite_log("INFO","Start and End times: ",start_date,end_date,moduleid=MODULE_ID)

    import os,time
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
        msgwrite_log("INFO","Start time is later than end time!",moduleid=MODULE_ID)
        
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
        
        # Loop over areas:
        for areaid in NWCSAF_MSG_AREAS:
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
                                                                       year,month,day,hour,min,areaid)
            outname_f = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_fog"%(RGBDIR_OUT,MetSat,
                                                                 year,month,day,hour,min,areaid)
            outname_ctop = "%s/%s_%.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop_co2corr"%(RGBDIR_OUT,MetSat,
                                                                                 year,month,day,hour,min,areaid)

            if os.path.exists(outname_nf+".png") and os.path.exists(outname_f+".png") and os.path.exists(outname_ctop+".png"):
                msgwrite_log("INFO","All rgb's have been done previously",moduleid=MODULE_ID)
                continue
            
            msgwrite_log("INFO","Try make RGBs for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,min),moduleid=MODULE_ID)

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

            ch1,ok1=get_ch_projected(ch1file,CoverageData)
            ch2,ok2=get_ch_projected(ch2file,CoverageData)
            ch3,ok3=get_ch_projected(ch3file,CoverageData)
            ch4,ok4=get_ch_projected(ch4file,CoverageData)    
            ch5,ok5=get_ch_projected(ch5file,CoverageData)
            ch6,ok6=get_ch_projected(ch6file,CoverageData)
            ch7,ok7=get_ch_projected(ch7file,CoverageData)
            ch9,ok9=get_ch_projected(ch9file,CoverageData)
            ch10,ok10=get_ch_projected(ch10file,CoverageData)
            ch11,ok11=get_ch_projected(ch11file,CoverageData)
            
            ok4r=0
            if ok4 and ok9 and ok11:
                ch4r = co2corr_bt39(ch4,ch9,ch11)
                ok4r = 1
                    
            # IR - channel 9:
            if ok9:
                outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_bw_ch9"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                msgwrite_log("INFO","met-8 product: %.4d%.2d%.2d%.2d%.2d_%s_bw_ch9"%(year,month,day,hour,min,areaid),moduleid=MODULE_ID)                
                this = make_bw(ch9,outname,inverse=1,gamma=1.6)
                # Sync the output with fileserver:
                if FSERVER_SYNC:
                    os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

                do_sir(this,"ir9",year,month,day,hour,min,areaid)
                    
            # Water vapour - channel 5:
            if ok5:
                outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_bw_ch5"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                msgwrite_log("INFO","met-8 product: %.4d%.2d%.2d%.2d%.2d_%s_bw_ch5"%(year,month,day,hour,min,areaid),moduleid=MODULE_ID)                
                this = make_bw(ch5,outname,inverse=1,gamma=1.6)
                # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
                if FSERVER_SYNC:
                    os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))
                    
                do_sir(this,"watervapour_high",year,month,day,hour,min,areaid)

            # Water vapour - channel 6:
            if ok6:
                outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_bw_ch6"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                msgwrite_log("INFO","met-8 product: %.4d%.2d%.2d%.2d%.2d_%s_bw_ch6"%(year,month,day,hour,min,areaid),moduleid=MODULE_ID)                
                this = make_bw(ch6,outname,inverse=1,gamma=1.6)
                # Sync the output with fileserver: /data/proj/saftest/nwcsafmsg
                if FSERVER_SYNC:
                    os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

                do_sir(this,"watervapour_low",year,month,day,hour,min,areaid)

            # Daytime overview:
            if ok1 and ok2 and ok9:
                outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_overview"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                msgwrite_log("INFO","met-8 product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_overview"%(year,month,day,hour,min,areaid),moduleid=MODULE_ID)
                this = makergb_visvisir(ch1,ch2,ch9,outname,gamma=(1.6,1.6,1.6))
                if FSERVER_SYNC:
                    os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

                do_sir(this,"overview",year,month,day,hour,min,areaid)

            # Daytime "green snow":
            if ok3 and ok2 and ok9:
                outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_greensnow"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                msgwrite_log("INFO","met-8 product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_greensnow"%(year,month,day,hour,min,areaid),moduleid=MODULE_ID)
                this = makergb_visvisir(ch3,ch2,ch9,outname,gamma=(1.6,1.6,1.6))
                if FSERVER_SYNC:
                    os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

                do_sir(this,"greensnow",year,month,day,hour,min,areaid)

            # Daytime convection:
            if ok1 and ok3 and ok4 and ok5 and ok6 and ok9:
                outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_severe_convection"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                msgwrite_log("INFO","met-8 product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_severe_convection"%(year,month,day,hour,min,areaid),moduleid=MODULE_ID)
                this = makergb_severe_convection(ch1,ch3,ch4,ch5,ch6,ch9,outname,gamma=(1.0,1.0,1.0),rgbrange=[(-30,0),(0,55.0),(-70.0,20.0)])
                if FSERVER_SYNC:
                    os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

                do_sir(this,"convection",year,month,day,hour,min,areaid)

            # Fog and low clouds
            if ok4r and ok9 and ok10:
                outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_nightfog"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                msgwrite_log("INFO","met-8 product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_nightfog"%(year,month,day,hour,min,areaid),moduleid=MODULE_ID)
                this=makergb_nightfog(ch4r,ch9,ch10,outname,gamma=(1.0,2.0,1.0),rgbrange=[(-4,2),(0,6),(243,293)])
                if FSERVER_SYNC:
                    os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))
                
                do_sir(this,"nightfog",year,month,day,hour,min,areaid)

            if ok7 and ok9 and ok10:
                outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_fog"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                msgwrite_log("INFO","met-8 product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_fog"%(year,month,day,hour,min,areaid),moduleid=MODULE_ID)
                this = makergb_fog(ch7,ch9,ch10,outname,gamma=(1.0,2.0,1.0),rgbrange=[(-4,2),(0,6),(243,283)])
                if FSERVER_SYNC:
                    os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))
                
                do_sir(this,"fog",year,month,day,hour,min,areaid)

            # "cloudtop": Low clouds, thin cirrus, nighttime
            if ok4r and ok9 and ok10:
                outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop_co2corr"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                msgwrite_log("INFO","met-8 product: %.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop_co2corr"%(year,month,day,hour,min,areaid),moduleid=MODULE_ID)
                this = makergb_cloudtop(ch4r,ch9,ch10,outname,gamma=(1.2,1.2,1.2))
                if FSERVER_SYNC:
                    os.system("%s %s/%s* %s/."%(SYNC,RGBDIR_OUT,os.path.basename(outname),FSERVER_RGBDIR_OUT))

                do_sir(this,"cloudtop",year,month,day,hour,min,areaid)

        sec = sec + DSEC_SLOTS
