#
#
from msg_communications import *

from msgpp_config import *
from msg_remap_util import *

import _satproj
import epshdf
import area
import glob,os
import pps_array2image
import Numeric

MODULE_ID = "MSG_CTTH_REMAP"

# ----------------------------------------
class msgCTTHData:
    def __init__(self):
        self.data = None
        self.scaling_factor=1
        self.offset=0
        self.num_of_lines=0
        self.num_of_columns=0
        self.product=""
        self.id=""
        
class msgCTTH:
    def __init__(self):
        self.package=""
        self.saf=""
        self.product_name=""
        self.num_of_columns=0
        self.num_of_lines=0
        self.projection_name=""
        self.region_name=""
        self.cfac=0
        self.lfac=0
        self.coff=0
        self.loff=0
        self.nb_param=0
        self.gp_sc_id=0
        self.image_acquisition_time=0
        self.spectral_channel_id=0
        self.nominal_product_time=0
        self.sgs_product_quality=0
        self.sgs_product_completeness=0
        self.product_algorithm_version=""
        self.cloudiness=None # Effective cloudiness
        self.processing_flags=None
        self.height=None
        self.temperature=None
        self.pressure=None
        
# ------------------------------------------------------------------
def read_msgCtth(filename):
    import _pyhl
    aNodeList=_pyhl.read_nodelist(filename)
    aNodeList.selectAll()
    aNodeList.fetch()

    retv = msgCTTH()
    retv.cloudiness=msgCTTHData() # Effective cloudiness
    retv.temperature=msgCTTHData()
    retv.height=msgCTTHData()
    retv.pressure=msgCTTHData()
    retv.processing_flags=msgCTTHData()

    # The header
    aNode=aNodeList.getNode("/PACKAGE")
    retv.package=aNode.data()
    aNode=aNodeList.getNode("/SAF")
    retv.saf=aNode.data()
    aNode=aNodeList.getNode("/PRODUCT_NAME")
    retv.product_name=aNode.data()
    aNode=aNodeList.getNode("/NC")
    retv.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/NL")
    retv.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/PROJECTION_NAME")
    retv.projection_name=aNode.data()
    aNode=aNodeList.getNode("/REGION_NAME")
    retv.region_name=aNode.data()
    aNode=aNodeList.getNode("/CFAC")
    retv.cfac=aNode.data()
    aNode=aNodeList.getNode("/LFAC")
    retv.lfac=aNode.data()
    aNode=aNodeList.getNode("/COFF")
    retv.coff=aNode.data()
    aNode=aNodeList.getNode("/LOFF")
    retv.loff=aNode.data()
    aNode=aNodeList.getNode("/NB_PARAMETERS")
    retv.nb_param=aNode.data()
    aNode=aNodeList.getNode("/GP_SC_ID")
    retv.gp_sc_id=aNode.data()
    aNode=aNodeList.getNode("/IMAGE_ACQUISITION_TIME")
    retv.image_acquisition_time=aNode.data()
    aNode=aNodeList.getNode("/SPECTRAL_CHANNEL_ID")
    retv.spectral_channel_id=aNode.data()
    aNode=aNodeList.getNode("/NOMINAL_PRODUCT_TIME")
    retv.nominal_product_time=aNode.data()
    aNode=aNodeList.getNode("/SGS_PRODUCT_QUALITY")
    retv.sgs_product_quality=aNode.data()
    aNode=aNodeList.getNode("/SGS_PRODUCT_COMPLETENESS")
    retv.sgs_product_completeness=aNode.data()
    aNode=aNodeList.getNode("/PRODUCT_ALGORITHM_VERSION")
    retv.product_algorithm_version=aNode.data()    
    # ------------------------
    
    # The CTTH cloudiness data
    aNode=aNodeList.getNode("/CTTH_EFFECT")
    retv.cloudiness.data=aNode.data()
    aNode=aNodeList.getNode("/CTTH_EFFECT/SCALING_FACTOR")
    retv.cloudiness.scaling_factor=aNode.data()
    aNode=aNodeList.getNode("/CTTH_EFFECT/OFFSET")
    retv.cloudiness.offset=aNode.data()
    aNode=aNodeList.getNode("/CTTH_EFFECT/N_LINES")
    retv.cloudiness.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/CTTH_EFFECT/N_COLS")
    retv.cloudiness.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/CTTH_EFFECT/PRODUCT")
    retv.cloudiness.product=aNode.data()
    aNode=aNodeList.getNode("/CTTH_EFFECT/ID")
    retv.cloudiness.id=aNode.data()
    # ------------------------
    
    # The CTTH temperature data
    aNode=aNodeList.getNode("/CTTH_TEMPER")
    retv.temperature.data=aNode.data()
    aNode=aNodeList.getNode("/CTTH_TEMPER/SCALING_FACTOR")
    retv.temperature.scaling_factor=aNode.data()
    aNode=aNodeList.getNode("/CTTH_TEMPER/OFFSET") 
    retv.temperature.offset=aNode.data()
    aNode=aNodeList.getNode("/CTTH_TEMPER/N_LINES")
    retv.temperature.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/CTTH_TEMPER/N_COLS")
    retv.temperature.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/CTTH_TEMPER/PRODUCT")
    retv.temperature.product=aNode.data()
    aNode=aNodeList.getNode("/CTTH_TEMPER/ID")
    retv.temperature.id=aNode.data()
    # ------------------------
    
    # The CTTH pressure data
    aNode=aNodeList.getNode("/CTTH_PRESS")
    retv.pressure.data=aNode.data()
    aNode=aNodeList.getNode("/CTTH_PRESS/SCALING_FACTOR")
    retv.pressure.scaling_factor=aNode.data()
    aNode=aNodeList.getNode("/CTTH_PRESS/OFFSET")
    retv.pressure.offset=aNode.data()
    aNode=aNodeList.getNode("/CTTH_PRESS/N_LINES")
    retv.pressure.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/CTTH_PRESS/N_COLS")
    retv.pressure.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/CTTH_PRESS/PRODUCT")
    retv.pressure.product=aNode.data()
    aNode=aNodeList.getNode("/CTTH_PRESS/ID")
    retv.pressure.id=aNode.data()
    # ------------------------
    
    # The CTTH height data
    aNode=aNodeList.getNode("/CTTH_HEIGHT")
    retv.height.data=aNode.data()
    aNode=aNodeList.getNode("/CTTH_HEIGHT/SCALING_FACTOR")
    retv.height.scaling_factor=aNode.data()
    aNode=aNodeList.getNode("/CTTH_HEIGHT/OFFSET")
    retv.height.offset=aNode.data()
    aNode=aNodeList.getNode("/CTTH_HEIGHT/N_LINES")
    retv.height.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/CTTH_HEIGHT/N_COLS")
    retv.height.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/CTTH_HEIGHT/PRODUCT")
    retv.height.product=aNode.data()
    aNode=aNodeList.getNode("/CTTH_HEIGHT/ID")
    retv.height.id=aNode.data()
    # ------------------------
    
    # The CTTH processing/quality flags
    aNode=aNodeList.getNode("/CTTH_QUALITY")
    retv.processing_flags.data=aNode.data()
    aNode=aNodeList.getNode("/CTTH_QUALITY/SCALING_FACTOR")
    retv.processing_flags.scaling_factor=aNode.data()
    aNode=aNodeList.getNode("/CTTH_QUALITY/OFFSET")
    retv.processing_flags.offset=aNode.data()
    aNode=aNodeList.getNode("/CTTH_QUALITY/N_LINES")
    retv.processing_flags.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/CTTH_QUALITY/N_COLS")
    retv.processing_flags.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/CTTH_QUALITY/PRODUCT")
    retv.processing_flags.product=aNode.data()
    aNode=aNodeList.getNode("/CTTH_QUALITY/ID")
    retv.processing_flags.id=aNode.data()
    # ------------------------
    
    return retv

# ------------------------------------------------------------------
def msg_ctth2ppsformat(msgctth,satid="Meteosat 8"):
    import area,string

    retv = epshdf.CloudTop()
    retv.region=epshdf.SafRegion()
    retv.region.xsize=msgctth.num_of_columns
    retv.region.ysize=msgctth.num_of_lines
    retv.region.id=msgctth.region_name
    retv.region.pcs_id=msgctth.projection_name
    pcsdef=string.join(area.area(msgctth.region_name).pcs.definition)
    retv.region.pcs_def=pcsdef
    retv.region.area_extent=area.area(msgctth.region_name).extent
    retv.satellite_id=satid

    retv.processingflag_lut = []
    retv.des="MSG SEVIRI Cloud Top Temperature & Height"
    retv.ctt_des="MSG SEVIRI cloud top temperature (K)"
    retv.ctp_des="MSG SEVIRI cloud top pressure (hPa)"
    retv.ctp_des="MSG SEVIRI cloud top height (m)"
    retv.cloudiness_des="MSG SEVIRI effective cloudiness (%)"
    retv.processingflag_des = 'MSG SEVIRI bitwise quality/processing flags'

    retv.t_gain=1.0
    retv.t_intercept=100.0
    retv.t_nodata=255
    #print "Temp offset & scaling factor: ",msgctth.temperature.scaling_factor,msgctth.temperature.offset
    arr = (((msgctth.temperature.data * msgctth.temperature.scaling_factor + msgctth.temperature.offset)\
            - retv.t_intercept)/retv.t_gain).astype('b')
    retv.temperature = Numeric.where(Numeric.equal(msgctth.temperature.data,0),retv.t_nodata,arr).astype('b')
    #retv.temperature=msgctth.temperature.data
    #retv.t_gain=msgctth.temperature.scaling_factor
    #retv.t_intercept=msgctth.temperature.offset
    
    retv.h_gain=200.0
    retv.h_intercept=0.0
    retv.h_nodata=255
    #print "Height offset & scaling factor: ",msgctth.height.scaling_factor,msgctth.height.offset
    arr = (((msgctth.height.data * msgctth.height.scaling_factor + msgctth.height.offset)\
            - retv.h_intercept)/retv.h_gain).astype('b')
    retv.height = Numeric.where(Numeric.equal(msgctth.height.data,0),retv.h_nodata,arr).astype('b')
    #retv.height=msgctth.height.data
    #retv.h_gain=msgctth.height.scaling_factor
    #retv.h_intercept=msgctth.height.offset
    
    retv.p_gain=25.0
    retv.p_intercept=0.0
    retv.p_nodata=255
    #print "Pressure offset & scaling factor: ",msgctth.pressure.scaling_factor,msgctth.pressure.offset
    arr = (((msgctth.pressure.data * msgctth.pressure.scaling_factor + msgctth.pressure.offset)\
            - retv.p_intercept)/retv.p_gain).astype('b')
    retv.pressure = Numeric.where(Numeric.equal(msgctth.pressure.data,0),retv.p_nodata,arr).astype('b')
    #retv.pressure=msgctth.pressure.data
    #retv.p_gain=msgctth.pressure.scaling_factor
    #retv.p_intercept=msgctth.pressure.offset
    
    retv.cloudiness=msgctth.cloudiness.data
    retv.c_nodata=255 # Is this correct? FIXME
    
    retv.processingflag=convert_procflags2pps(msgctth.processing_flags.data)
    
    return retv

# ------------------------------------------------------------------
def convert_procflags2pps(data):
    import Numeric
    
    ones = Numeric.ones(data.shape,"s")

    # 2 bits to define processing status
    # (maps to pps bits 0 and 1:)
    is_bit0_set = get_bit_from_flags(data,0)    
    is_bit1_set = get_bit_from_flags(data,1)
    proc = is_bit0_set * Numeric.left_shift(ones,0) + \
           is_bit1_set * Numeric.left_shift(ones,1)
    #print Numeric.minimum.reduce(is_bit0_set.flat),Numeric.maximum.reduce(is_bit0_set.flat)
    #print Numeric.minimum.reduce(is_bit1_set.flat),Numeric.maximum.reduce(is_bit1_set.flat)
    del is_bit0_set
    del is_bit1_set
    #print "Processing status flags: min,max=",Numeric.minimum.reduce(proc.flat),Numeric.maximum.reduce(proc.flat)
    # Non-processed?
    # If non-processed in msg (0) then set pps bit 0 and nothing else.
    # If non-processed in msg due to FOV is cloud free (1) then do not set any pps bits.
    # If processed (because cloudy) with/without result in msg (2&3) then set pps bit 1.
    #
    arr = Numeric.where(Numeric.equal(proc,0),Numeric.left_shift(ones,0),0)
    #arr = Numeric.where(Numeric.equal(proc,1),Numeric.left_shift(ones,0),0)
    arr = Numeric.where(Numeric.equal(proc,2),Numeric.left_shift(ones,1),0)
    arr = Numeric.where(Numeric.equal(proc,3),Numeric.left_shift(ones,1),0)
    retv = Numeric.array(arr)
    del proc
    #print Numeric.minimum.reduce(retv.flat),Numeric.maximum.reduce(retv.flat)

    # 1 bit to define if RTTOV-simulations are available?
    # (maps to pps bit 3:)
    is_bit2_set = get_bit_from_flags(data,2)    
    proc = is_bit2_set
    #print Numeric.minimum.reduce(is_bit2_set.flat),Numeric.maximum.reduce(is_bit2_set.flat)
    #print "Processing flags - rttov: min,max=",Numeric.minimum.reduce(proc.flat),Numeric.maximum.reduce(proc.flat)
    # RTTOV-simulations available?
    #
    arr = Numeric.where(Numeric.equal(proc,1),Numeric.left_shift(ones,3),0)
    retv = Numeric.add(retv,arr)
    del is_bit2_set
    
    # 3 bits to describe NWP input data
    # (maps to pps bits 4&5:)
    is_bit3_set = get_bit_from_flags(data,3)
    is_bit4_set = get_bit_from_flags(data,4)
    is_bit5_set = get_bit_from_flags(data,5)    
    # Put together the three bits into a nwp-flag:
    nwp_bits = is_bit3_set * Numeric.left_shift(ones,0) + \
               is_bit4_set * Numeric.left_shift(ones,1) + \
               is_bit5_set * Numeric.left_shift(ones,2)
    arr = Numeric.where(Numeric.logical_and(Numeric.greater_equal(nwp_bits,3),Numeric.less_equal(nwp_bits,5)),
                        Numeric.left_shift(ones,4),0)
    arr = Numeric.add(arr,Numeric.where(Numeric.logical_or(Numeric.equal(nwp_bits,2),Numeric.equal(nwp_bits,4)),
                                        Numeric.left_shift(ones,5),0))
    #print "Processing flags - nwp: min,max=",Numeric.minimum.reduce(nwp_bits.flat),Numeric.maximum.reduce(nwp_bits.flat)
    retv = Numeric.add(retv,arr)
    del is_bit3_set
    del is_bit4_set
    del is_bit5_set

    # 2 bits to describe SEVIRI input data
    # (maps to pps bits 6:)
    is_bit6_set = get_bit_from_flags(data,6)
    is_bit7_set = get_bit_from_flags(data,7)
    # Put together the two bits into a seviri-flag:
    seviri_bits = is_bit6_set * Numeric.left_shift(ones,0) + \
                  is_bit7_set * Numeric.left_shift(ones,1)
    arr = Numeric.where(Numeric.greater_equal(seviri_bits,2),Numeric.left_shift(ones,6),0)
    #print "Processing flags - seviri: min,max=",Numeric.minimum.reduce(seviri_bits.flat),\
    #      Numeric.maximum.reduce(seviri_bits.flat)
    retv = Numeric.add(retv,arr)
    del is_bit6_set
    del is_bit7_set
    
    # 4 bits to describe which method has been used
    # (maps to pps bits 7&8 and bit 2:)
    is_bit8_set = get_bit_from_flags(data,8)
    is_bit9_set = get_bit_from_flags(data,9)
    is_bit10_set = get_bit_from_flags(data,10)
    is_bit11_set = get_bit_from_flags(data,11)
    # Put together the four bits into a method-flag:
    method_bits = is_bit8_set * Numeric.left_shift(ones,0) + \
                  is_bit9_set * Numeric.left_shift(ones,1) + \
                  is_bit10_set * Numeric.left_shift(ones,2) + \
                  is_bit11_set * Numeric.left_shift(ones,3)
    arr = Numeric.where(Numeric.logical_and(Numeric.greater_equal(method_bits,1),Numeric.less_equal(method_bits,2)),
                        Numeric.left_shift(ones,2),0)
    arr = Numeric.add(arr,
                      Numeric.where(Numeric.equal(method_bits,1),Numeric.left_shift(ones,7),0))
    arr = Numeric.add(arr,
                      Numeric.where(Numeric.logical_and(Numeric.greater_equal(method_bits,3),
                                                        Numeric.less_equal(method_bits,12)),
                                    Numeric.left_shift(ones,8),0))
    #print "Processing flags - method: min,max=",Numeric.minimum.reduce(method_bits.flat),\
    #      Numeric.maximum.reduce(method_bits.flat)
    # (Maps directly - as well - to the spare bits 9-12) 
    arr = Numeric.add(arr,Numeric.where(is_bit8_set,Numeric.left_shift(ones,9),0))
    arr = Numeric.add(arr,Numeric.where(is_bit9_set,Numeric.left_shift(ones,10),0))
    arr = Numeric.add(arr,Numeric.where(is_bit10_set,Numeric.left_shift(ones,11),0))
    arr = Numeric.add(arr,Numeric.where(is_bit11_set,Numeric.left_shift(ones,12),0))   
    retv = Numeric.add(retv,arr)
    del is_bit8_set
    del is_bit9_set
    del is_bit10_set
    del is_bit11_set

    # 2 bits to describe the quality of the processing itself
    # (maps to pps bits 14&15:)
    is_bit12_set = get_bit_from_flags(data,12)
    is_bit13_set = get_bit_from_flags(data,13)
    # Put together the two bits into a quality-flag:
    qual_bits = is_bit12_set * Numeric.left_shift(ones,0) + \
                is_bit13_set * Numeric.left_shift(ones,1)
    arr = Numeric.where(Numeric.logical_and(Numeric.greater_equal(qual_bits,1),
                                            Numeric.less_equal(qual_bits,2)),
                        Numeric.left_shift(ones,14),0)
    arr = Numeric.add(arr,
                      Numeric.where(Numeric.equal(qual_bits,2),Numeric.left_shift(ones,15),0))
    #print "Processing flags - quality: min,max=",Numeric.minimum.reduce(qual_bits.flat),\
    #      Numeric.maximum.reduce(qual_bits.flat)
    retv = Numeric.add(retv,arr)
    del is_bit12_set
    del is_bit13_set    
    
    return retv.astype('s')

# ------------------------------------------------------------------
def OLDmsgCtth_remap_fast(cov,msgctth,areaid,a):
    msgctth.temperature.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctth.temperature.data)
    msgctth.height.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctth.height.data)
    msgctth.pressure.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctth.pressure.data)
    msgctth.cloudiness.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctth.cloudiness.data)
    msgctth.processing_flags.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctth.processing_flags.data)    

    msgctth.region_name = areaid
    msgctth.projection_name = a.pcs.id
    msgctth.num_of_columns = a.xsize
    msgctth.num_of_lines = a.ysize
    msgctth.temperature.num_of_columns = a.xsize
    msgctth.temperature.num_of_lines = a.ysize
    msgctth.height.num_of_columns = a.xsize
    msgctth.height.num_of_lines = a.ysize
    msgctth.pressure.num_of_columns = a.xsize
    msgctth.pressure.num_of_lines = a.ysize
    msgctth.cloudiness.num_of_columns = a.xsize
    msgctth.cloudiness.num_of_lines = a.ysize
    msgctth.processing_flags.num_of_columns = a.xsize
    msgctth.processing_flags.num_of_lines = a.ysize    

    return msgctth

# ------------------------------------------------------------------
def msgCtth_remap_fast(cov,msgctth,areaid,a):
    retv = msgCTTH()
    retv.cloudiness=msgCTTHData() # Effective cloudiness
    retv.temperature=msgCTTHData()
    retv.height=msgCTTHData()
    retv.pressure=msgCTTHData()
    retv.processing_flags=msgCTTHData()

    retv.temperature.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctth.temperature.data)
    retv.height.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctth.height.data)
    retv.pressure.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctth.pressure.data)
    retv.cloudiness.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctth.cloudiness.data)
    retv.processing_flags.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctth.processing_flags.data)    

    retv.region_name = areaid
    retv.projection_name = a.pcs.id
    retv.num_of_columns = a.xsize
    retv.num_of_lines = a.ysize

    retv.temperature.offset=msgctth.temperature.offset
    retv.temperature.scaling_factor=msgctth.temperature.scaling_factor
    retv.temperature.num_of_columns = a.xsize
    retv.temperature.num_of_lines = a.ysize

    retv.height.offset=msgctth.height.offset
    retv.height.scaling_factor=msgctth.height.scaling_factor
    retv.height.num_of_columns = a.xsize
    retv.height.num_of_lines = a.ysize

    retv.pressure.offset=msgctth.pressure.offset
    retv.pressure.scaling_factor=msgctth.pressure.scaling_factor
    retv.pressure.num_of_columns = a.xsize
    retv.pressure.num_of_lines = a.ysize

    retv.cloudiness.offset=msgctth.cloudiness.offset
    retv.cloudiness.scaling_factor=msgctth.cloudiness.scaling_factor
    retv.cloudiness.num_of_columns = a.xsize
    retv.cloudiness.num_of_lines = a.ysize

    retv.processing_flags.offset=msgctth.processing_flags.offset
    retv.processing_flags.scaling_factor=msgctth.processing_flags.scaling_factor
    retv.processing_flags.num_of_columns = a.xsize
    retv.processing_flags.num_of_lines = a.ysize    

    return retv

# ------------------------------------------------------------------
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

    import time
    timetup = time.localtime(time.mktime((year,month,day,0,0,0,0,0,0)))    
    jday=timetup[7]
    msgwrite_log("INFO","year,month,day: %d %d %d Julian day = %d"%(year,month,day,jday),moduleid=MODULE_ID)
    
    lon = read_msg_lonlat(LONFILE)
    lat = read_msg_lonlat(LATFILE)
    
    #in_aid="CEuro"
    in_aid=MSG_AREA
    prefix="SAFNWC_MSG1_CTTH_%.2d%.3d_%.3d_%s"%(year-2000,jday,slotn,in_aid)    
    a=area.area(areaid)

    # Check for existing coverage file for the area:
    covfilename = "%s/cst/msg_coverage_%s.%s.hdf"%(APPLDIR,in_aid,areaid)
    if not os.path.exists(covfilename):
        cov = _satproj.create_coverage(a,lon,lat,1)
        writeCoverage(cov,covfilename,in_aid,areaid)
    else:
        cov,info = readCoverage(covfilename)
        #print info.items()
    
    for infile in glob.glob("%s/%s*h5"%(CTTHDIR_IN,prefix)):
        outfile = "%s/%s%s%s"%(CTTHDIR_OUT,os.path.basename(infile).split(in_aid)[0],
                               areaid,os.path.basename(infile).split(in_aid)[1])
        msgwrite_log("INFO","Output file: ",outfile,moduleid=MODULE_ID)
        if not os.path.exists(outfile):
            msgctth = read_msgCtth(infile)
            msgctth = msgCtth_remap_fast(cov,msgctth,areaid,a)
            ctth = msg_ctth2ppsformat(msgctth)
            epshdf.write_cloudtop(outfile,ctth,6)

        # Test reading it and generating a png image....
        that = epshdf.read_cloudtop(outfile,1,1,1,0,1)
        fileprefix = string.split(outfile,".h5")[0]
        #this = pps_array2image.ctthimage(that,fileprefix,(3,),"height",coastlines=1)
        this = pps_array2image.ctthimage(that,fileprefix+".temp",
                                         (3,),"temperature",coastlines=1)

        """
        import Numeric
        print " -------- Temperature ---------"
        print ctth.temperature[1000:1005,1000:1005]
        maxt = Numeric.where(Numeric.not_equal(ctth.temperature.flat,ctth.t_nodata),ctth.temperature.flat,0)
        print "Max & Min: ",Numeric.maximum.reduce(maxt),\
              Numeric.minimum.reduce(ctth.temperature.flat)
        print that.temperature[1000:1005,1000:1005]
        maxt = Numeric.where(Numeric.not_equal(that.temperature.flat,ctth.t_nodata),that.temperature.flat,0)
        print "Max & Min: ",Numeric.maximum.reduce(maxt),\
              Numeric.minimum.reduce(that.temperature.flat)
        print msgctth.temperature.data[1000:1005,1000:1005]
        print "Max & Min: ",Numeric.maximum.reduce(msgctth.temperature.data.flat),\
              Numeric.minimum.reduce(msgctth.temperature.data.flat)
        #print " ------ Processing flags ------"
        #print msgctth.processing_flags.data[1000:1005,1000:1005]
        #print ctth.processingflag[1000:1005,1000:1005]
        #print " ------ Processing flags ------"
        #print msgctth.processing_flags.data[0:5,0:5]
        #print ctth.processingflag[0:5,0:5]
        """
