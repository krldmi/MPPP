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
import numpy

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
    def read_msgCtth(self,filename):
        import _pyhl
        aNodeList=_pyhl.read_nodelist(filename)
        aNodeList.selectAll()
        aNodeList.fetch()
        
        self.cloudiness=msgCTTHData() # Effective cloudiness
        self.temperature=msgCTTHData()
        self.height=msgCTTHData()
        self.pressure=msgCTTHData()
        self.processing_flags=msgCTTHData()
        
        # The header
        aNode=aNodeList.getNode("/PACKAGE")
        self.package=aNode.data()
        aNode=aNodeList.getNode("/SAF")
        self.saf=aNode.data()
        aNode=aNodeList.getNode("/PRODUCT_NAME")
        self.product_name=aNode.data()
        aNode=aNodeList.getNode("/NC")
        self.num_of_columns=aNode.data()
        aNode=aNodeList.getNode("/NL")
        self.num_of_lines=aNode.data()
        aNode=aNodeList.getNode("/PROJECTION_NAME")
        self.projection_name=aNode.data()
        aNode=aNodeList.getNode("/REGION_NAME")
        self.region_name=aNode.data()
        aNode=aNodeList.getNode("/CFAC")
        self.cfac=aNode.data()
        aNode=aNodeList.getNode("/LFAC")
        self.lfac=aNode.data()
        aNode=aNodeList.getNode("/COFF")
        self.coff=aNode.data()
        aNode=aNodeList.getNode("/LOFF")
        self.loff=aNode.data()
        aNode=aNodeList.getNode("/NB_PARAMETERS")
        self.nb_param=aNode.data()
        aNode=aNodeList.getNode("/GP_SC_ID")
        self.gp_sc_id=aNode.data()
        aNode=aNodeList.getNode("/IMAGE_ACQUISITION_TIME")
        self.image_acquisition_time=aNode.data()
        aNode=aNodeList.getNode("/SPECTRAL_CHANNEL_ID")
        self.spectral_channel_id=aNode.data()
        aNode=aNodeList.getNode("/NOMINAL_PRODUCT_TIME")
        self.nominal_product_time=aNode.data()
        aNode=aNodeList.getNode("/SGS_PRODUCT_QUALITY")
        self.sgs_product_quality=aNode.data()
        aNode=aNodeList.getNode("/SGS_PRODUCT_COMPLETENESS")
        self.sgs_product_completeness=aNode.data()
        aNode=aNodeList.getNode("/PRODUCT_ALGORITHM_VERSION")
        self.product_algorithm_version=aNode.data()    
        # ------------------------
    
        # The CTTH cloudiness data
        aNode=aNodeList.getNode("/CTTH_EFFECT")
        self.cloudiness.data=aNode.data()
        aNode=aNodeList.getNode("/CTTH_EFFECT/SCALING_FACTOR")
        self.cloudiness.scaling_factor=aNode.data()
        aNode=aNodeList.getNode("/CTTH_EFFECT/OFFSET")
        self.cloudiness.offset=aNode.data()
        aNode=aNodeList.getNode("/CTTH_EFFECT/N_LINES")
        self.cloudiness.num_of_lines=aNode.data()
        aNode=aNodeList.getNode("/CTTH_EFFECT/N_COLS")
        self.cloudiness.num_of_columns=aNode.data()
        aNode=aNodeList.getNode("/CTTH_EFFECT/PRODUCT")
        self.cloudiness.product=aNode.data()
        aNode=aNodeList.getNode("/CTTH_EFFECT/ID")
        self.cloudiness.id=aNode.data()
        # ------------------------
    
        # The CTTH temperature data
        aNode=aNodeList.getNode("/CTTH_TEMPER")
        self.temperature.data=aNode.data()
        aNode=aNodeList.getNode("/CTTH_TEMPER/SCALING_FACTOR")
        self.temperature.scaling_factor=aNode.data()
        aNode=aNodeList.getNode("/CTTH_TEMPER/OFFSET") 
        self.temperature.offset=aNode.data()
        aNode=aNodeList.getNode("/CTTH_TEMPER/N_LINES")
        self.temperature.num_of_lines=aNode.data()
        aNode=aNodeList.getNode("/CTTH_TEMPER/N_COLS")
        self.temperature.num_of_columns=aNode.data()
        aNode=aNodeList.getNode("/CTTH_TEMPER/PRODUCT")
        self.temperature.product=aNode.data()
        aNode=aNodeList.getNode("/CTTH_TEMPER/ID")
        self.temperature.id=aNode.data()
        # ------------------------
    
        # The CTTH pressure data
        aNode=aNodeList.getNode("/CTTH_PRESS")
        self.pressure.data=aNode.data()
        aNode=aNodeList.getNode("/CTTH_PRESS/SCALING_FACTOR")
        self.pressure.scaling_factor=aNode.data()
        aNode=aNodeList.getNode("/CTTH_PRESS/OFFSET")
        self.pressure.offset=aNode.data()
        aNode=aNodeList.getNode("/CTTH_PRESS/N_LINES")
        self.pressure.num_of_lines=aNode.data()
        aNode=aNodeList.getNode("/CTTH_PRESS/N_COLS")
        self.pressure.num_of_columns=aNode.data()
        aNode=aNodeList.getNode("/CTTH_PRESS/PRODUCT")
        self.pressure.product=aNode.data()
        aNode=aNodeList.getNode("/CTTH_PRESS/ID")
        self.pressure.id=aNode.data()
        # ------------------------
    
        # The CTTH height data
        aNode=aNodeList.getNode("/CTTH_HEIGHT")
        self.height.data=aNode.data()
        aNode=aNodeList.getNode("/CTTH_HEIGHT/SCALING_FACTOR")
        self.height.scaling_factor=aNode.data()
        aNode=aNodeList.getNode("/CTTH_HEIGHT/OFFSET")
        self.height.offset=aNode.data()
        aNode=aNodeList.getNode("/CTTH_HEIGHT/N_LINES")
        self.height.num_of_lines=aNode.data()
        aNode=aNodeList.getNode("/CTTH_HEIGHT/N_COLS")
        self.height.num_of_columns=aNode.data()
        aNode=aNodeList.getNode("/CTTH_HEIGHT/PRODUCT")
        self.height.product=aNode.data()
        aNode=aNodeList.getNode("/CTTH_HEIGHT/ID")
        self.height.id=aNode.data()
        # ------------------------
    
        # The CTTH processing/quality flags
        aNode=aNodeList.getNode("/CTTH_QUALITY")
        self.processing_flags.data=aNode.data()
        aNode=aNodeList.getNode("/CTTH_QUALITY/SCALING_FACTOR")
        self.processing_flags.scaling_factor=aNode.data()
        aNode=aNodeList.getNode("/CTTH_QUALITY/OFFSET")
        self.processing_flags.offset=aNode.data()
        aNode=aNodeList.getNode("/CTTH_QUALITY/N_LINES")
        self.processing_flags.num_of_lines=aNode.data()
        aNode=aNodeList.getNode("/CTTH_QUALITY/N_COLS")
        self.processing_flags.num_of_columns=aNode.data()
        aNode=aNodeList.getNode("/CTTH_QUALITY/PRODUCT")
        self.processing_flags.product=aNode.data()
        aNode=aNodeList.getNode("/CTTH_QUALITY/ID")
        self.processing_flags.id=aNode.data()
        # ------------------------

    def save(self,filename):
        ctth = msg_ctth2ppsformat(self)
        msg_communications.msgwrite_log("INFO",
                                        "Saving CTTH hdf file...",
                                        moduleid=MODULE_ID)
        epshdf.write_cloudtop(filename, ctth, 6)
        msg_communications.msgwrite_log("INFO",
                                        "Saving CTTH hdf file done !",
                                        moduleid=MODULE_ID)

    def project(self,coverage,dest_area):
        import area
        a = area.area(dest_area)

        retv = msgCTTH()
        retv.cloudiness=msgCTTHData() # Effective cloudiness
        retv.temperature=msgCTTHData()
        retv.height=msgCTTHData()
        retv.pressure=msgCTTHData()
        retv.processing_flags=msgCTTHData()

        retv.temperature.data = coverage.project_array(self.temperature.data)
        retv.height.data = coverage.project_array(self.height.data)
        retv.pressure.data = coverage.project_array(self.pressure.data)
        retv.cloudiness.data = coverage.project_array(self.cloudiness.data)
        retv.processing_flags.data = \
            coverage.project_array(self.processing_flags.data)

        retv.region_name = dest_area
        retv.projection_name = a.pcs.id
        retv.num_of_columns = a.xsize
        retv.num_of_lines = a.ysize
        
        retv.temperature.offset=self.temperature.offset
        retv.temperature.scaling_factor=self.temperature.scaling_factor
        retv.temperature.num_of_columns = a.xsize
        retv.temperature.num_of_lines = a.ysize
        
        retv.height.offset=self.height.offset
        retv.height.scaling_factor=self.height.scaling_factor
        retv.height.num_of_columns = a.xsize
        retv.height.num_of_lines = a.ysize

        retv.pressure.offset=self.pressure.offset
        retv.pressure.scaling_factor=self.pressure.scaling_factor
        retv.pressure.num_of_columns = a.xsize
        retv.pressure.num_of_lines = a.ysize
        
        retv.cloudiness.offset=self.cloudiness.offset
        retv.cloudiness.scaling_factor=self.cloudiness.scaling_factor
        retv.cloudiness.num_of_columns = a.xsize
        retv.cloudiness.num_of_lines = a.ysize
        
        retv.processing_flags.offset=self.processing_flags.offset
        retv.processing_flags.scaling_factor=self.processing_flags.scaling_factor
        retv.processing_flags.num_of_columns = a.xsize
        retv.processing_flags.num_of_lines = a.ysize    

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
            - retv.t_intercept)/retv.t_gain).astype('B')
    retv.temperature = numpy.where(numpy.equal(msgctth.temperature.data,0),retv.t_nodata,arr).astype('B')
    #retv.temperature=msgctth.temperature.data
    #retv.t_gain=msgctth.temperature.scaling_factor
    #retv.t_intercept=msgctth.temperature.offset
    
    retv.h_gain=200.0
    retv.h_intercept=0.0
    retv.h_nodata=255
    #print "Height offset & scaling factor: ",msgctth.height.scaling_factor,msgctth.height.offset
    arr = (((msgctth.height.data * msgctth.height.scaling_factor + msgctth.height.offset)\
            - retv.h_intercept)/retv.h_gain).astype('B')
    retv.height = numpy.where(numpy.equal(msgctth.height.data,0),retv.h_nodata,arr).astype('B')
    #retv.height=msgctth.height.data
    #retv.h_gain=msgctth.height.scaling_factor
    #retv.h_intercept=msgctth.height.offset
    
    retv.p_gain=25.0
    retv.p_intercept=0.0
    retv.p_nodata=255
    #print "Pressure offset & scaling factor: ",msgctth.pressure.scaling_factor,msgctth.pressure.offset
    arr = (((msgctth.pressure.data * msgctth.pressure.scaling_factor + msgctth.pressure.offset)\
            - retv.p_intercept)/retv.p_gain).astype('B')
    retv.pressure = numpy.where(numpy.equal(msgctth.pressure.data,0),retv.p_nodata,arr).astype('B')
    #retv.pressure=msgctth.pressure.data
    #retv.p_gain=msgctth.pressure.scaling_factor
    #retv.p_intercept=msgctth.pressure.offset
    
    retv.cloudiness=msgctth.cloudiness.data
    retv.c_nodata=255 # Is this correct? FIXME
    
    retv.processingflag=convert_procflags2pps(msgctth.processing_flags.data)
    
    return retv

# ------------------------------------------------------------------
def convert_procflags2pps(data):
    import numpy
    
    ones = numpy.ones(data.shape,"h")

    # 2 bits to define processing status
    # (maps to pps bits 0 and 1:)
    is_bit0_set = get_bit_from_flags(data,0)    
    is_bit1_set = get_bit_from_flags(data,1)
    proc = is_bit0_set * numpy.left_shift(ones,0) + \
           is_bit1_set * numpy.left_shift(ones,1)
    #print numpy.minimum.reduce(is_bit0_set.flat),numpy.maximum.reduce(is_bit0_set.flat)
    #print numpy.minimum.reduce(is_bit1_set.flat),numpy.maximum.reduce(is_bit1_set.flat)
    del is_bit0_set
    del is_bit1_set
    #print "Processing status flags: min,max=",numpy.minimum.reduce(proc.flat),numpy.maximum.reduce(proc.flat)
    # Non-processed?
    # If non-processed in msg (0) then set pps bit 0 and nothing else.
    # If non-processed in msg due to FOV is cloud free (1) then do not set any pps bits.
    # If processed (because cloudy) with/without result in msg (2&3) then set pps bit 1.
    #
    arr = numpy.where(numpy.equal(proc,0),numpy.left_shift(ones,0),0)
    #arr = numpy.where(numpy.equal(proc,1),numpy.left_shift(ones,0),0)
    arr = numpy.where(numpy.equal(proc,2),numpy.left_shift(ones,1),0)
    arr = numpy.where(numpy.equal(proc,3),numpy.left_shift(ones,1),0)
    retv = numpy.array(arr)
    del proc
    #print numpy.minimum.reduce(retv.flat),numpy.maximum.reduce(retv.flat)

    # 1 bit to define if RTTOV-simulations are available?
    # (maps to pps bit 3:)
    is_bit2_set = get_bit_from_flags(data,2)    
    proc = is_bit2_set
    #print numpy.minimum.reduce(is_bit2_set.flat),numpy.maximum.reduce(is_bit2_set.flat)
    #print "Processing flags - rttov: min,max=",numpy.minimum.reduce(proc.flat),numpy.maximum.reduce(proc.flat)
    # RTTOV-simulations available?
    #
    arr = numpy.where(numpy.equal(proc,1),numpy.left_shift(ones,3),0)
    retv = numpy.add(retv,arr)
    del is_bit2_set
    
    # 3 bits to describe NWP input data
    # (maps to pps bits 4&5:)
    is_bit3_set = get_bit_from_flags(data,3)
    is_bit4_set = get_bit_from_flags(data,4)
    is_bit5_set = get_bit_from_flags(data,5)    
    # Put together the three bits into a nwp-flag:
    nwp_bits = is_bit3_set * numpy.left_shift(ones,0) + \
               is_bit4_set * numpy.left_shift(ones,1) + \
               is_bit5_set * numpy.left_shift(ones,2)
    arr = numpy.where(numpy.logical_and(numpy.greater_equal(nwp_bits,3),numpy.less_equal(nwp_bits,5)),
                        numpy.left_shift(ones,4),0)
    arr = numpy.add(arr,numpy.where(numpy.logical_or(numpy.equal(nwp_bits,2),numpy.equal(nwp_bits,4)),
                                        numpy.left_shift(ones,5),0))
    #print "Processing flags - nwp: min,max=",numpy.minimum.reduce(nwp_bits.flat),numpy.maximum.reduce(nwp_bits.flat)
    retv = numpy.add(retv,arr)
    del is_bit3_set
    del is_bit4_set
    del is_bit5_set

    # 2 bits to describe SEVIRI input data
    # (maps to pps bits 6:)
    is_bit6_set = get_bit_from_flags(data,6)
    is_bit7_set = get_bit_from_flags(data,7)
    # Put together the two bits into a seviri-flag:
    seviri_bits = is_bit6_set * numpy.left_shift(ones,0) + \
                  is_bit7_set * numpy.left_shift(ones,1)
    arr = numpy.where(numpy.greater_equal(seviri_bits,2),numpy.left_shift(ones,6),0)
    #print "Processing flags - seviri: min,max=",numpy.minimum.reduce(seviri_bits.flat),\
    #      numpy.maximum.reduce(seviri_bits.flat)
    retv = numpy.add(retv,arr)
    del is_bit6_set
    del is_bit7_set
    
    # 4 bits to describe which method has been used
    # (maps to pps bits 7&8 and bit 2:)
    is_bit8_set = get_bit_from_flags(data,8)
    is_bit9_set = get_bit_from_flags(data,9)
    is_bit10_set = get_bit_from_flags(data,10)
    is_bit11_set = get_bit_from_flags(data,11)
    # Put together the four bits into a method-flag:
    method_bits = is_bit8_set * numpy.left_shift(ones,0) + \
                  is_bit9_set * numpy.left_shift(ones,1) + \
                  is_bit10_set * numpy.left_shift(ones,2) + \
                  is_bit11_set * numpy.left_shift(ones,3)
    arr = numpy.where(numpy.logical_or(
        numpy.logical_and(numpy.greater_equal(method_bits,1),numpy.less_equal(method_bits,2)),
        numpy.equal(method_bits,13)),
                        numpy.left_shift(ones,2),0)
    arr = numpy.add(arr,
                      numpy.where(numpy.equal(method_bits,1),numpy.left_shift(ones,7),0))
    arr = numpy.add(arr,
                      numpy.where(numpy.logical_and(numpy.greater_equal(method_bits,3),
                                                        numpy.less_equal(method_bits,12)),
                                    numpy.left_shift(ones,8),0))
    #print "Processing flags - method: min,max=",numpy.minimum.reduce(method_bits.flat),\
    #      numpy.maximum.reduce(method_bits.flat)
    # (Maps directly - as well - to the spare bits 9-12) 
    arr = numpy.add(arr,numpy.where(is_bit8_set,numpy.left_shift(ones,9),0))
    arr = numpy.add(arr,numpy.where(is_bit9_set,numpy.left_shift(ones,10),0))
    arr = numpy.add(arr,numpy.where(is_bit10_set,numpy.left_shift(ones,11),0))
    arr = numpy.add(arr,numpy.where(is_bit11_set,numpy.left_shift(ones,12),0))   
    retv = numpy.add(retv,arr)
    del is_bit8_set
    del is_bit9_set
    del is_bit10_set
    del is_bit11_set

    # 2 bits to describe the quality of the processing itself
    # (maps to pps bits 14&15:)
    is_bit12_set = get_bit_from_flags(data,12)
    is_bit13_set = get_bit_from_flags(data,13)
    # Put together the two bits into a quality-flag:
    qual_bits = is_bit12_set * numpy.left_shift(ones,0) + \
                is_bit13_set * numpy.left_shift(ones,1)
    arr = numpy.where(numpy.logical_and(numpy.greater_equal(qual_bits,1),
                                            numpy.less_equal(qual_bits,2)),
                        numpy.left_shift(ones,14),0)
    arr = numpy.add(arr,
                      numpy.where(numpy.equal(qual_bits,2),numpy.left_shift(ones,15),0))
    #print "Processing flags - quality: min,max=",numpy.minimum.reduce(qual_bits.flat),\
    #      numpy.maximum.reduce(qual_bits.flat)
    retv = numpy.add(retv,arr)
    del is_bit12_set
    del is_bit13_set    
    
    return retv.astype('h')


# ------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 6:
        print "Usage: %s <year> <month> <day> <hourmin (HHMM)> <area id>"%(sys.argv[0])
        sys.exit(-9)
    else:
        import string
        year = string.atoi(sys.argv[1])
        month = string.atoi(sys.argv[2])
        day = string.atoi(sys.argv[3])
        hour = string.atoi(sys.argv[4][0:2])
        minute = string.atoi(sys.argv[4][2:4])
        areaid = sys.argv[5]

    import time
    timetup = time.localtime(time.mktime((year,month,day,0,0,0,0,0,0)))    
    jday=timetup[7]
    msgwrite_log("INFO","year,month,day: %d %d %d Julian day = %d"%(year,month,day,jday),moduleid=MODULE_ID)
    
    lon = read_msg_lonlat(LONFILE)
    lat = read_msg_lonlat(LATFILE)
    
    #in_aid="CEuro"
    in_aid=MSG_AREA
    #prefix="SAFNWC_MSG%.1d_CTTH_%.2d%.3d_%.3d_%s"%(SAT_NUMBER,year-2000,jday,slotn,in_aid)    
    prefix="SAFNWC_MSG%.1d_CT___%.4d%.2d%.2d%.2d%.2d_%s"%(MSG_NUMBER,year,month,day,hour,minute,in_aid)
    a=area.area(areaid)

    # Check for existing coverage file for the area:
    covfilename = "%s/msg_coverage_%s.%s.hdf"%(DATADIR,in_aid,areaid)
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
        import numpy
        print " -------- Temperature ---------"
        print ctth.temperature[1000:1005,1000:1005]
        maxt = numpy.where(numpy.not_equal(ctth.temperature.flat,ctth.t_nodata),ctth.temperature.flat,0)
        print "Max & Min: ",numpy.maximum.reduce(maxt),\
              numpy.minimum.reduce(ctth.temperature.flat)
        print that.temperature[1000:1005,1000:1005]
        maxt = numpy.where(numpy.not_equal(that.temperature.flat,ctth.t_nodata),that.temperature.flat,0)
        print "Max & Min: ",numpy.maximum.reduce(maxt),\
              numpy.minimum.reduce(that.temperature.flat)
        print msgctth.temperature.data[1000:1005,1000:1005]
        print "Max & Min: ",numpy.maximum.reduce(msgctth.temperature.data.flat),\
              numpy.minimum.reduce(msgctth.temperature.data.flat)
        #print " ------ Processing flags ------"
        #print msgctth.processing_flags.data[1000:1005,1000:1005]
        #print ctth.processingflag[1000:1005,1000:1005]
        #print " ------ Processing flags ------"
        #print msgctth.processing_flags.data[0:5,0:5]
        #print ctth.processingflag[0:5,0:5]
        """
