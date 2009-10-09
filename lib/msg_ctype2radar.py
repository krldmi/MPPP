
from msg_communications import *

from msgpp_config import *
from msg_ctype import *

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
    b.setScalarValue(1,'MSGCT',"string",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/prodpar")
    b.setScalarValue(1,0.0,"float",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/image1/what/quantity")
    b.setScalarValue(1,"ct","string",-1)
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

