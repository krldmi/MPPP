"""This module handles coverage objects. Such objects are used to
transform area projected data by changing either the area or the
projection or both. A typical usage is to transform one large area in
satellite projection to an area of interest in polar projection for
example.
"""

import os
import numpy

import _pyhl
import _satproj
import area
import py_msg

from msgpp_config import *
from msg_communications import msgwrite_log





MODULE_ID = "MSG_COVERAGE"




# !!! This class is already defined in satproj somehow, would be nice to
# extend it (inherit) instead of creating it from scratch...

class SatProjCov:
    """This is the class that defines coverage objects. They contain the
    mapping information necessary for projection purposes. For efficiency
    reasons, generate coverages are saved to disk for later reuse.
    """
    coverage = None
    """Coverage data"""

    colidx = None
    rowidx = None
    in_area_id = None
    """Input area"""
    out_area_id = None
    """Output area"""

    is_hr = False

    def __init__(self,in_area_id = None, out_area_id = None, hr = False):
        self.coverage = None
        self.colidx = None
        self.rowidx = None
        self.in_area_id = in_area_id
        self.out_area_id = out_area_id
        self.is_hr = hr

        if(hr):
            self._filename = "%s/cst/msg_coverage_%s_hr.%s.hdf"\
                %(APPLDIR,in_area_id,out_area_id)
        else:
            self._filename = "%s/cst/msg_coverage_%s.%s.hdf"\
                %(APPLDIR,self.in_area_id,self.out_area_id)


        if((in_area_id is None) or (out_area_id is None)):
            return
        
        msgwrite_log("INFO",
                     "Getting coverage for %s onto %s."
                     %(in_area_id, out_area_id),
                     moduleid=MODULE_ID)

        if(hr):
            channel = "12"
        else:
            channel = "1"

        if not os.path.exists(self._filename):
            msgwrite_log("INFO",
                         "Generate MSG coverage and store in file %s..."
                         %(self._filename),
                         moduleid=MODULE_ID)

            lat,lon = py_msg.lat_lon_from_region("safnwc_"+in_area_id+".cfg", 
                                                 channel)
            areaObj=area.area(out_area_id)
            coverage_data = _satproj.create_coverage(areaObj,lon,lat,1)

            self.colidx = coverage_data.colidx
            self.rowidx = coverage_data.rowidx
            self.coverage = coverage_data.coverage
            self._write()

        else:
            msgwrite_log("INFO",
                         "Read the MSG coverage from file %s..."
                         %(self._filename),
                         moduleid=MODULE_ID)
            self._read()
        



    def _write(self):

        a=_pyhl.nodelist()
        
        b=_pyhl.node(_pyhl.GROUP_ID,"/info")
        a.addNode(b)
        b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/description")
        b.setScalarValue(-1,
                         "MSG coverage from area %s on to area %s"
                          %(self.in_area_id,
                            self.out_area_id),
                          "string",-1)
        a.addNode(b)
        
        shape=[self.coverage.shape[0],self.coverage.shape[1]]
        b=_pyhl.node(_pyhl.DATASET_ID,"/coverage")
        b.setArrayValue(1,shape,self.coverage,"uchar",-1)
        a.addNode(b)
        b=_pyhl.node(_pyhl.DATASET_ID,"/rowidx")
        b.setArrayValue(1,shape,self.rowidx,"ushort",-1)
        a.addNode(b)
        b=_pyhl.node(_pyhl.DATASET_ID,"/colidx")
        b.setArrayValue(1,shape,self.colidx,"ushort",-1)
        a.addNode(b)
        
        a.write(self._filename,COMPRESS_LVL)
        
    

    def _read(self):

        a=_pyhl.read_nodelist(self._filename)
        b=a.getNodeNames()
        
        a.selectNode("/info/description")
        a.selectNode("/coverage")
        a.selectNode("/rowidx")
        a.selectNode("/colidx")
        a.fetch()
        
        info={}
        c=a.getNode("/info/description");
        d=c.data()
        info["description"]=d
        
        c=a.getNode("/coverage")
        coverage=c.data()
        c=a.getNode("/rowidx")
        rowidx=c.data()
        c=a.getNode("/colidx")
        colidx=c.data()
        
        self.coverage = coverage.astype('b')
        self.rowidx = rowidx.astype('h')
        self.colidx = colidx.astype('h')
            
    def project_array(self, a):
        """Project the masked array *a* along the defined *coverage*.
        """
        if (a is None):
            return None
        
        # This is kinda dirty, but necessary until _satproj supports masked
        # arrays.

        filling = -99999.0
        
        amask = numpy.ones(a.shape)
        amask[a.mask] = 0

        res = _satproj.project(self.coverage,
                               self.rowidx,
                               self.colidx,
                               a.filled(filling),
                               int(filling))
        pmask = _satproj.project(self.coverage,
                                 self.rowidx,
                                 self.colidx,
                                 amask,
                                 int(filling))
        
        #return numpy.ma.array(res,mask = (res == filling))
        return numpy.ma.array(res, mask = (pmask == 0))


# deprecated, to be removed
# def get_msg_lonlat(area_id,hr = False):
#     import py_msg
    
#     if(hr):
#         return py_msg.lat_lon_from_region("safnwc_" + area_id + ".cfg", "12")
#     else:
#         return py_msg.lat_lon_from_region("safnwc_" + area_id + ".cfg", "1")



# def get_coverage(in_area_id, out_area_id, lon, lat,hr = False):
#     areaObj=area.area(out_area_id)
    
#     if(hr):
#         covfilename = "%s/cst/msg_coverage_%s_hr.%s.hdf"\
#                       %(APPLDIR,in_area_id,out_area_id)
#     else:
#         covfilename = "%s/cst/msg_coverage_%s.%s.hdf"\
#                       %(APPLDIR,in_area_id,out_area_id)
    
#     if not os.path.exists(covfilename):
#         msgwrite_log("INFO","Generate MSG coverage and store in file...",moduleid=MODULE_ID)
#         coverage_data = _satproj.create_coverage(areaObj,lon,lat,1)
#         #coverage_data.in_area_id = in_area_id
#         #coverage_data.out_area_id = out_area_id
#         write_coverage(coverage_data,covfilename,in_area_id,out_area_id)
#     else:
#         msgwrite_log("INFO","Read the MSG coverage from file...",moduleid=MODULE_ID)
#         coverage_data,info = read_coverage(covfilename)
#         #coverage_data.in_area_id = in_area_id
#         #coverage_data.out_area_id = out_area_id
        
#     return coverage_data

# def write_coverage(covIn,filename,in_area_id, out_area_id):
        
#     a=_pyhl.nodelist()

#     b=_pyhl.node(_pyhl.GROUP_ID,"/info")
#     a.addNode(b)
#     b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/description")
#     b.setScalarValue(-1,
#                       "MSG coverage from area %s on to area %s"
#                       %(in_area_id,out_area_id),
#                       "string",-1)
#     a.addNode(b)
    
#     shape=[covIn.coverage.shape[0],covIn.coverage.shape[1]]
#     b=_pyhl.node(_pyhl.DATASET_ID,"/coverage")
#     b.setArrayValue(1,shape,covIn.coverage,"uchar",-1)
#     a.addNode(b)
#     b=_pyhl.node(_pyhl.DATASET_ID,"/rowidx")
#     b.setArrayValue(1,shape,covIn.rowidx,"ushort",-1)
#     a.addNode(b)
#     b=_pyhl.node(_pyhl.DATASET_ID,"/colidx")
#     b.setArrayValue(1,shape,covIn.colidx,"ushort",-1)
#     a.addNode(b)

#     a.write(filename,COMPRESS_LVL)
    
#     return

# def read_coverage(filename):

#     a=_pyhl.read_nodelist(filename)
#     b=a.getNodeNames()
    
#     a.selectNode("/info/description")
#     a.selectNode("/coverage")
#     a.selectNode("/rowidx")
#     a.selectNode("/colidx")
#     a.fetch()

#     info={}
#     c=a.getNode("/info/description");
#     d=c.data()
#     info["description"]=d

#     c=a.getNode("/coverage")
#     coverage=c.data()
#     c=a.getNode("/rowidx")
#     rowidx=c.data()
#     c=a.getNode("/colidx")
#     colidx=c.data()
    
#     retv = SatProjCov()
#     retv.coverage = coverage.astype('b')
#     retv.rowidx = rowidx.astype('h')
#     retv.colidx = colidx.astype('h')

#     return retv,info
