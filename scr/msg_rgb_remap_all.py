
from msgpp_config import *
from msg_remap_util import *
from msg_rgb_remap import *
#

# ------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print "Usage: %s <start-date: yyyymmddhhmm> <end-date: yyyymmddhhmm>"%(sys.argv[0])
        sys.exit(-9)
    else:
        start_date = sys.argv[1]
        end_date = sys.argv[2]

    import string,time
    import _satproj
    import area
    import glob,os
    import msg_ctype_products

    MetSat=MSG_SATELLITE
    in_aid=MSG_AREA
    
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

    CoverageData = {}

    for areaid in NWCSAF_MSG_AREAS:
        a=area.area(areaid)

        # Check for existing coverage file for the area:
        covfilename = "%s/cst/msg_coverage_%s.%s.hdf"%(APPLDIR,in_aid,areaid)
        cov = None

        if not cov and not os.path.exists(covfilename):
            print "Generate MSG coverage and store in file..."
            cov = _satproj.create_coverage(a,lon,lat,1)
            writeCoverage(cov,covfilename,in_aid,areaid)
        elif not cov:
            print "Read the MSG coverage from file..."
            cov,info = readCoverage(covfilename)

        if time_start > time_end:
            print "Start time is later than end time!"
        
        sec = time_start
        while (sec < time_end + 1):
            ttup = time.gmtime(sec)
            year,month,day,hour,min,dummy,dummy,jday,dummy = ttup
            slotn = hour*4+int((min+7.5)/15)
            
            fileprfx="%s/%.4d/%.2d/%.2d"%(RGBDIR_IN,year,month,day)
            #fileprfx="%s"%(RGBDIR_IN)
            fname = "%.4d%.2d%.2d%.2d%.2d_C%.4d_%.4d_S%.4d_%.4d"%(year,month,day,hour,min,MSG_AREA_CENTER[0],MSG_AREA_CENTER[1],ROWS,COLS)

            fl = glob.glob("%s/*_%s*"%(fileprfx,fname))
            if len(fl) == 0:
                print "No files for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,min)
            else:
                print "Try make RGBs for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,min)

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

                ch1,ok1=get_ch_projected(ch1file,cov)
                ch2,ok2=get_ch_projected(ch2file,cov)
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

                if ok9:
                    s=string.ljust(areaid,12)
                    ext=string.replace(s," ","_")
                    ctypefile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.cloudtype.hdf"%(CTYPEDIR_OUT,MetSat,year,month,day,hour,min,areaid)
                    print "Output file: ",ctypefile
                    # Two products to vägverket and tv:
                    msg_ctype_products.make_ctype_prod01(ch9,ctypefile,areaid,gamma=1.6,overlay=1)
                    msg_ctype_products.make_ctype_prod02(ch9,ctypefile,areaid,gamma=1.6,overlay=1)
    
                
                """
                # IR - channel 9:
                if ok9:
                    outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_bw_ch9"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                    make_bw(ch9,outname,inverse=1,gamma=1.6)

                # Water vapour - channel 5:
                if ok5:
                    outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_bw_ch5"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                    make_bw(ch5,outname,inverse=1,gamma=1.6)

                # Daytime overview:
                if ok1 and ok2 and ok9:
                    outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_overview"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                    makergb_visvisir(ch1,ch2,ch9,outname,gamma=(1.6,1.6,1.6))

                # Daytime "grön snö":
                if ok3 and ok2 and ok9:
                    outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_greensnow"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                    makergb_visvisir(ch3,ch2,ch9,outname,gamma=(1.6,1.6,1.6))
                    #makergb_visvisir(ch3,ch2,ch9,outname,gamma=(1.0,1.0,1.0))

                # Daytime convection:
                if ok1 and ok3 and ok4 and ok5 and ok6 and ok9:
                    outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_severe_convection"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                    makergb_severe_convection(ch1,ch3,ch4,ch5,ch6,ch9,outname,gamma=(1.0,0.5,1.0),rgbrange=[(-30,0),(0,50.0),(-70.0,20.0)])

                # Fog and low clouds
                if ok4r and ok9 and ok10:
                    outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_nightfog"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                    makergb_nightfog(ch4r,ch9,ch10,outname,gamma=(1.0,2.0,1.0),rgbrange=[(-4,2),(0,6),(243,293)])
                if ok7 and ok9 and ok10:
                    outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_fog"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                    makergb_fog(ch7,ch9,ch10,outname,gamma=(1.0,2.0,1.0),rgbrange=[(-4,2),(0,6),(243,283)])

                """
                # "red snow": Low clouds and snow daytime
                #if ok1 and ok3 and ok9:
                #    outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_redsnow_016"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                #    makergb_redsnow(ch1,ch3,ch9,outname)

                # "cloudtop": Low clouds, thin cirrus, nighttime
                #if ok4 and ok9 and ok10:
                #    outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                #    makergb_cloudtop(ch4,ch9,ch10,outname)
                if ok4r and ok9 and ok10:
                    outname = "%s/met8_%.4d%.2d%.2d%.2d%.2d_%s_rgb_cloudtop_co2corr"%(RGBDIR_OUT,year,month,day,hour,min,areaid)
                    #makergb_cloudtop(ch4r,ch9,ch10,outname,gamma=(1.6,1.6,1.4))
                    makergb_cloudtop(ch4r,ch9,ch10,outname,gamma=(1.8,1.8,1.8),
                                     rgbrange=[(-290,-223),(-290,-223),(-290,-223)])
        
            sec = sec + DSEC_SLOTS

