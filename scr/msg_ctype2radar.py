
from msg_communications import *

from msgpp_config import *
from msg_ctype_remap import *

# ------------------------------------------------------------------
def msg_writectype2nordradformat(msgctype,filename,datestr,satid="Meteosat 8"):
    import string
    import _pyhl
    status = 1
    
    a=_pyhl.nodelist()

    # What
    b=_pyhl.node(_pyhl.GROUP_ID,"/what")
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/what/object")
    b.setScalarValue(-1,"IMAGE","string",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/what/sets")
    b.setScalarValue(-1,1,"int",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/what/version")
    b.setScalarValue(-1,"H5rad 1.2","string",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/what/date")
    #yyyymmdd = msgctype.nominal_product_time[0:8]
    yyyymmdd = datestr[0:8]
    hourminsec = datestr[8:12]+'00'
    b.setScalarValue(-1,yyyymmdd,"string",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/what/time")
    b.setScalarValue(-1,hourminsec,"string",-1)
    a.addNode(b)    

    # Where
    b=_pyhl.node(_pyhl.GROUP_ID,"/where")
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/where/projdef")
    b.setScalarValue(-1,msgctype.pcs_def,"string",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/where/xsize")
    b.setScalarValue(-1,msgctype.num_of_columns,"int",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/where/ysize")
    b.setScalarValue(-1,msgctype.num_of_lines,"int",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/where/xscale")
    b.setScalarValue(-1,msgctype.xscale,"float",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/where/yscale")
    b.setScalarValue(-1,msgctype.yscale,"float",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/where/LL_lon")
    b.setScalarValue(-1,msgctype.LL_lon,"float",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/where/LL_lat")
    b.setScalarValue(-1,msgctype.LL_lat,"float",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/where/UR_lon")
    b.setScalarValue(-1,msgctype.UR_lon,"float",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/where/UR_lat")
    b.setScalarValue(-1,msgctype.UR_lat,"float",-1)
    a.addNode(b)

    # How
    b=_pyhl.node(_pyhl.GROUP_ID,"/how")
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/how/area")
    b.setScalarValue(-1,msgctype.region_name,"string",-1)
    a.addNode(b)

    # image1
    b=_pyhl.node(_pyhl.GROUP_ID,"/image1")
    a.addNode(b)
    b=_pyhl.node(_pyhl.DATASET_ID,"/image1/data")
    b.setArrayValue(1,[msgctype.num_of_columns,msgctype.num_of_lines],msgctype.cloudtype.data,"uchar",-1)
    a.addNode(b)

    b=_pyhl.node(_pyhl.GROUP_ID,"/image1/what")
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/product")
    # We should eventually try to use the msg-parameters "package", "product_algorithm_version", and "product_name":
    b.setScalarValue(1,'NWCSAF_MSG_CT',"string",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/prodpar")
    b.setScalarValue(1,0.0,"float",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/quantity")
    b.setScalarValue(1,"cloudtype","string",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/startdate")
    b.setScalarValue(-1,yyyymmdd,"string",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/starttime")
    b.setScalarValue(-1,hourminsec,"string",-1)
    a.addNode(b)    
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/enddate")
    b.setScalarValue(-1,yyyymmdd,"string",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/endtime")
    b.setScalarValue(-1,hourminsec,"string",-1)
    a.addNode(b)    
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/gain")
    b.setScalarValue(-1,1.0,"float",-1)
    a.addNode(b)    
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/offset")
    b.setScalarValue(-1,0.0,"float",-1)
    a.addNode(b)    
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/nodata")
    b.setScalarValue(-1,0.0,"float",-1)
    a.addNode(b)
    # What we call missingdata in PPS:
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/undetect")
    b.setScalarValue(-1,20.0,"float",-1)
    a.addNode(b)    
        
    a.write(filename,COMPRESS_LVL)    
    return status

# ------------------------------------------------------------------
# test:
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 6:
        print "Usage: %s <year> <month> <day> <slot number> <area id>"%(sys.argv[0])
        sys.exit(-9)
    else:
        import string
        year = string.atoi(sys.argv[1])
        month = string.atoi(sys.argv[2])
        day = string.atoi(sys.argv[3])
        slotn = string.atoi(sys.argv[4])
        areaid = sys.argv[5]

    MetSat=MSG_SATELLITE

    import time
    timetup = time.localtime(time.mktime((year,month,day,0,0,0,0,0,0)))    
    jday=timetup[7]
    msgwrite_log("INFO","year,month,day: %d %d %d Julian day = %d"%(year,month,day,jday),moduleid=MODULE_ID)
    hour = slotn/4
    min = (slotn%4)*15
    
    lon = read_msg_lonlat(LONFILE)
    lat = read_msg_lonlat(LATFILE)
    
    in_aid=MSG_AREA
    prefix="SAFNWC_MSG1_CT___%.2d%.3d_%.3d_%s"%(year-2000,jday,slotn,in_aid)    
    a=area.area(areaid)

    # Check for existing coverage file for the area:
    covfilename = "%s/cst/msg_coverage_%s.%s.hdf"%(APPLDIR,in_aid,areaid)
    if not os.path.exists(covfilename):
        cov = _satproj.create_coverage(a,lon,lat,1)
        writeCoverage(cov,covfilename,in_aid,areaid)
    else:
        cov,info = readCoverage(covfilename)
        #print info.items()

    datestr = "%.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,min)
    print "Date string: %s"%datestr
    
    for infile in glob.glob("%s/%s*h5"%(CTYPEDIR_IN,prefix)):
        s=string.ljust(areaid,12)
        ext=string.replace(s," ","_")
        outfile = "%s/%s_nordrad_%.4d%.2d%.2d_%.2d%.2d.%s.cloudtype.hdf"%(CTYPEDIR_OUT,MetSat,year,month,day,hour,min,areaid)
        msgwrite_log("INFO","Output file: ",outfile,moduleid=MODULE_ID)
        if not os.path.exists(outfile):
            msgctype = read_msgCtype(infile)
            msgctype = msgCtype_remap_fast(cov,msgctype,areaid,a)            
            status = msg_writectype2nordradformat(msgctype,outfile,datestr)
