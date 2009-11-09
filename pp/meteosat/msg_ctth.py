"""Module defining a CTTH channel type.
"""
#
#
import epshdf
import area
import numpy
import satellite

from msg_remap_util import get_bit_from_flags

import logging
import logging.config

from msgpp_config import APPLDIR

logging.config.fileConfig(APPLDIR+"/etc/logging.conf")
LOG = logging.getLogger('msg.ctth')


# ----------------------------------------
class MsgCTTHData(object):
    """CTTH data object.
    """
    def __init__(self):
        self.data = None
        self.scaling_factor = 1
        self.offset = 0
        self.num_of_lines = 0
        self.num_of_columns = 0
        self.product = ""
        self.id = ""
        
class MsgCTTH(satellite.GenericChannel):
    """CTTH channel.
    """
    def __init__(self, resolution = None):
        self.filled = False
        self.name = "CTTH"
        self.resolution = resolution
        self.package = ""
        self.saf = ""
        self.product_name = ""
        self.num_of_columns = 0
        self.num_of_lines = 0
        self.projection_name = ""
        self.region_name = ""
        self.cfac = 0
        self.lfac = 0
        self.coff = 0
        self.loff = 0
        self.nb_param = 0
        self.gp_sc_id = 0
        self.image_acquisition_time = 0
        self.spectral_channel_id = 0
        self.nominal_product_time = 0
        self.sgs_product_quality = 0
        self.sgs_product_completeness = 0
        self.product_algorithm_version = ""
        self.cloudiness = None # Effective cloudiness
        self.processing_flags = None
        self.height = None
        self.temperature = None
        self.pressure = None
        

    def isloaded(self):
        return self.filled

    def read_msgCtth(self, filename):
        import _pyhl
        a_node_list = _pyhl.read_nodelist(filename)
        a_node_list.selectAll()
        a_node_list.fetch()
        
        self.cloudiness = MsgCTTHData() # Effective cloudiness
        self.temperature = MsgCTTHData()
        self.height = MsgCTTHData()
        self.pressure = MsgCTTHData()
        self.processing_flags = MsgCTTHData()
        
        # The header
        a_node = a_node_list.getNode("/PACKAGE")
        self.package = a_node.data()
        a_node = a_node_list.getNode("/SAF")
        self.saf = a_node.data()
        a_node = a_node_list.getNode("/PRODUCT_NAME")
        self.product_name = a_node.data()
        a_node = a_node_list.getNode("/NC")
        self.num_of_columns = a_node.data()
        a_node = a_node_list.getNode("/NL")
        self.num_of_lines = a_node.data()
        a_node = a_node_list.getNode("/PROJECTION_NAME")
        self.projection_name = a_node.data()
        a_node = a_node_list.getNode("/REGION_NAME")
        self.region_name = a_node.data()
        a_node = a_node_list.getNode("/CFAC")
        self.cfac = a_node.data()
        a_node = a_node_list.getNode("/LFAC")
        self.lfac = a_node.data()
        a_node = a_node_list.getNode("/COFF")
        self.coff = a_node.data()
        a_node = a_node_list.getNode("/LOFF")
        self.loff = a_node.data()
        a_node = a_node_list.getNode("/NB_PARAMETERS")
        self.nb_param = a_node.data()
        a_node = a_node_list.getNode("/GP_SC_ID")
        self.gp_sc_id = a_node.data()
        a_node = a_node_list.getNode("/IMAGE_ACQUISITION_TIME")
        self.image_acquisition_time = a_node.data()
        a_node = a_node_list.getNode("/SPECTRAL_CHANNEL_ID")
        self.spectral_channel_id = a_node.data()
        a_node = a_node_list.getNode("/NOMINAL_PRODUCT_TIME")
        self.nominal_product_time = a_node.data()
        a_node = a_node_list.getNode("/SGS_PRODUCT_QUALITY")
        self.sgs_product_quality = a_node.data()
        a_node = a_node_list.getNode("/SGS_PRODUCT_COMPLETENESS")
        self.sgs_product_completeness = a_node.data()
        a_node = a_node_list.getNode("/PRODUCT_ALGORITHM_VERSION")
        self.product_algorithm_version = a_node.data()    
        # ------------------------
    
        # The CTTH cloudiness data
        a_node = a_node_list.getNode("/CTTH_EFFECT")
        self.cloudiness.data = a_node.data()
        a_node = a_node_list.getNode("/CTTH_EFFECT/SCALING_FACTOR")
        self.cloudiness.scaling_factor = a_node.data()
        a_node = a_node_list.getNode("/CTTH_EFFECT/OFFSET")
        self.cloudiness.offset = a_node.data()
        a_node = a_node_list.getNode("/CTTH_EFFECT/N_LINES")
        self.cloudiness.num_of_lines = a_node.data()
        a_node = a_node_list.getNode("/CTTH_EFFECT/N_COLS")
        self.cloudiness.num_of_columns = a_node.data()
        a_node = a_node_list.getNode("/CTTH_EFFECT/PRODUCT")
        self.cloudiness.product = a_node.data()
        a_node = a_node_list.getNode("/CTTH_EFFECT/ID")
        self.cloudiness.id = a_node.data()
        # ------------------------
    
        # The CTTH temperature data
        a_node = a_node_list.getNode("/CTTH_TEMPER")
        self.temperature.data = a_node.data()
        a_node = a_node_list.getNode("/CTTH_TEMPER/SCALING_FACTOR")
        self.temperature.scaling_factor = a_node.data()
        a_node = a_node_list.getNode("/CTTH_TEMPER/OFFSET") 
        self.temperature.offset = a_node.data()
        a_node = a_node_list.getNode("/CTTH_TEMPER/N_LINES")
        self.temperature.num_of_lines = a_node.data()
        a_node = a_node_list.getNode("/CTTH_TEMPER/N_COLS")
        self.temperature.num_of_columns = a_node.data()
        a_node = a_node_list.getNode("/CTTH_TEMPER/PRODUCT")
        self.temperature.product = a_node.data()
        a_node = a_node_list.getNode("/CTTH_TEMPER/ID")
        self.temperature.id = a_node.data()
        # ------------------------
    
        # The CTTH pressure data
        a_node = a_node_list.getNode("/CTTH_PRESS")
        self.pressure.data = a_node.data()
        a_node = a_node_list.getNode("/CTTH_PRESS/SCALING_FACTOR")
        self.pressure.scaling_factor = a_node.data()
        a_node = a_node_list.getNode("/CTTH_PRESS/OFFSET")
        self.pressure.offset = a_node.data()
        a_node = a_node_list.getNode("/CTTH_PRESS/N_LINES")
        self.pressure.num_of_lines = a_node.data()
        a_node = a_node_list.getNode("/CTTH_PRESS/N_COLS")
        self.pressure.num_of_columns = a_node.data()
        a_node = a_node_list.getNode("/CTTH_PRESS/PRODUCT")
        self.pressure.product = a_node.data()
        a_node = a_node_list.getNode("/CTTH_PRESS/ID")
        self.pressure.id = a_node.data()
        # ------------------------
    
        # The CTTH height data
        a_node = a_node_list.getNode("/CTTH_HEIGHT")
        self.height.data = a_node.data()
        a_node = a_node_list.getNode("/CTTH_HEIGHT/SCALING_FACTOR")
        self.height.scaling_factor = a_node.data()
        a_node = a_node_list.getNode("/CTTH_HEIGHT/OFFSET")
        self.height.offset = a_node.data()
        a_node = a_node_list.getNode("/CTTH_HEIGHT/N_LINES")
        self.height.num_of_lines = a_node.data()
        a_node = a_node_list.getNode("/CTTH_HEIGHT/N_COLS")
        self.height.num_of_columns = a_node.data()
        a_node = a_node_list.getNode("/CTTH_HEIGHT/PRODUCT")
        self.height.product = a_node.data()
        a_node = a_node_list.getNode("/CTTH_HEIGHT/ID")
        self.height.id = a_node.data()
        # ------------------------
    
        # The CTTH processing/quality flags
        a_node = a_node_list.getNode("/CTTH_QUALITY")
        self.processing_flags.data = a_node.data()
        a_node = a_node_list.getNode("/CTTH_QUALITY/SCALING_FACTOR")
        self.processing_flags.scaling_factor = a_node.data()
        a_node = a_node_list.getNode("/CTTH_QUALITY/OFFSET")
        self.processing_flags.offset = a_node.data()
        a_node = a_node_list.getNode("/CTTH_QUALITY/N_LINES")
        self.processing_flags.num_of_lines = a_node.data()
        a_node = a_node_list.getNode("/CTTH_QUALITY/N_COLS")
        self.processing_flags.num_of_columns = a_node.data()
        a_node = a_node_list.getNode("/CTTH_QUALITY/PRODUCT")
        self.processing_flags.product = a_node.data()
        a_node = a_node_list.getNode("/CTTH_QUALITY/ID")
        self.processing_flags.id = a_node.data()

        self.filled = True


    def save(self, filename):
        """Save the current CTTH channel to HDF5 format.
        """
        ctth = msg_ctth2ppsformat(self)
        LOG.info("Saving CTTH hdf file...")
        epshdf.write_cloudtop(filename, ctth, 6)
        LOG.info("Saving CTTH hdf file done !")

    def project(self, coverage):
        """Project the current CTTH channel along the *coverage*
        """
        dest_area_id = coverage.out_area_id
        
        dest_area = area.area(dest_area_id)

        retv = MsgCTTH()
        retv.cloudiness = MsgCTTHData() # Effective cloudiness
        retv.temperature = MsgCTTHData()
        retv.height = MsgCTTHData()
        retv.pressure = MsgCTTHData()
        retv.processing_flags = MsgCTTHData()

        retv.temperature.data = coverage.project_array(self.temperature.data)
        retv.height.data = coverage.project_array(self.height.data)
        retv.pressure.data = coverage.project_array(self.pressure.data)
        retv.cloudiness.data = coverage.project_array(self.cloudiness.data)
        retv.processing_flags.data = \
            coverage.project_array(self.processing_flags.data)

        retv.region_name = dest_area_id
        retv.projection_name = dest_area.pcs.id
        retv.num_of_columns = dest_area.xsize
        retv.num_of_lines = dest_area.ysize
        
        retv.temperature.offset = self.temperature.offset
        retv.temperature.scaling_factor = self.temperature.scaling_factor
        retv.temperature.num_of_columns = dest_area.xsize
        retv.temperature.num_of_lines = dest_area.ysize
        
        retv.height.offset = self.height.offset
        retv.height.scaling_factor = self.height.scaling_factor
        retv.height.num_of_columns = dest_area.xsize
        retv.height.num_of_lines = dest_area.ysize

        retv.pressure.offset = self.pressure.offset
        retv.pressure.scaling_factor = self.pressure.scaling_factor
        retv.pressure.num_of_columns = dest_area.xsize
        retv.pressure.num_of_lines = dest_area.ysize
        
        retv.cloudiness.offset = self.cloudiness.offset
        retv.cloudiness.scaling_factor = self.cloudiness.scaling_factor
        retv.cloudiness.num_of_columns = dest_area.xsize
        retv.cloudiness.num_of_lines = dest_area.ysize
        
        retv.processing_flags.offset = self.processing_flags.offset
        retv.processing_flags.scaling_factor = \
             self.processing_flags.scaling_factor
        retv.processing_flags.num_of_columns = dest_area.xsize
        retv.processing_flags.num_of_lines = dest_area.ysize    

        retv.name = self.name
        retv.resolution = self.resolution
        retv.filled = True

        return retv




# ------------------------------------------------------------------
def msg_ctth2ppsformat(msgctth, satid="Meteosat 8"):
    """Convert the current CTTH channel to pps format.
    """
    retv = epshdf.CloudTop()
    retv.region = epshdf.SafRegion()
    retv.region.xsize = msgctth.num_of_columns
    retv.region.ysize = msgctth.num_of_lines
    retv.region.id = msgctth.region_name
    retv.region.pcs_id = msgctth.projection_name
    pcsdef = ' '.join(area.area(msgctth.region_name).pcs.definition)
    retv.region.pcs_def = pcsdef
    retv.region.area_extent = area.area(msgctth.region_name).extent
    retv.satellite_id = satid

    retv.processingflag_lut = []
    retv.des = "MSG SEVIRI Cloud Top Temperature & Height"
    retv.ctt_des = "MSG SEVIRI cloud top temperature (K)"
    retv.ctp_des = "MSG SEVIRI cloud top pressure (hPa)"
    retv.ctp_des = "MSG SEVIRI cloud top height (m)"
    retv.cloudiness_des = "MSG SEVIRI effective cloudiness (%)"
    retv.processingflag_des = 'MSG SEVIRI bitwise quality/processing flags'

    retv.t_gain = 1.0
    retv.t_intercept = 100.0
    retv.t_nodata = 255

    arr = (((msgctth.temperature.data * msgctth.temperature.scaling_factor +
             msgctth.temperature.offset) - retv.t_intercept) /
           retv.t_gain).astype('B')
    retv.temperature = numpy.where(numpy.equal(msgctth.temperature.data, 0),
                                   retv.t_nodata,arr).astype('B')
    
    retv.h_gain = 200.0
    retv.h_intercept = 0.0
    retv.h_nodata = 255

    arr = (((msgctth.height.data * msgctth.height.scaling_factor +
             msgctth.height.offset) - retv.h_intercept) /
           retv.h_gain).astype('B')
    retv.height = numpy.where(numpy.equal(msgctth.height.data, 0),
                              retv.h_nodata, arr).astype('B')
    
    retv.p_gain = 25.0
    retv.p_intercept = 0.0
    retv.p_nodata = 255

    arr = (((msgctth.pressure.data * msgctth.pressure.scaling_factor +
             msgctth.pressure.offset) - retv.p_intercept) /
           retv.p_gain).astype('B')
    retv.pressure = numpy.where(numpy.equal(msgctth.pressure.data, 0),
                                retv.p_nodata, arr).astype('B')
    
    retv.cloudiness = msgctth.cloudiness.data
    retv.c_nodata = 255 # Is this correct? FIXME
    
    retv.processingflag = convert_procflags2pps(msgctth.processing_flags.data)
    
    return retv

# ------------------------------------------------------------------
def convert_procflags2pps(data):

    ones = numpy.ones(data.shape,"h")

    # 2 bits to define processing status
    # (maps to pps bits 0 and 1:)
    is_bit0_set = get_bit_from_flags(data, 0)    
    is_bit1_set = get_bit_from_flags(data, 1)
    proc = (is_bit0_set * numpy.left_shift(ones, 0) +
            is_bit1_set * numpy.left_shift(ones, 1))
    del is_bit0_set
    del is_bit1_set

    # Non-processed?
    # If non-processed in msg (0) then set pps bit 0 and nothing else.
    # If non-processed in msg due to FOV is cloud free (1) then do not set any
    # pps bits.
    # If processed (because cloudy) with/without result in msg (2&3) then set
    # pps bit 1.

    arr = numpy.where(numpy.equal(proc, 0), numpy.left_shift(ones, 0), 0)
    arr = numpy.where(numpy.equal(proc, 2), numpy.left_shift(ones, 1), 0)
    arr = numpy.where(numpy.equal(proc, 3), numpy.left_shift(ones, 1), 0)
    retv = numpy.array(arr)
    del proc


    # 1 bit to define if RTTOV-simulations are available?
    # (maps to pps bit 3:)
    is_bit2_set = get_bit_from_flags(data, 2)    
    proc = is_bit2_set

    # RTTOV-simulations available?

    arr = numpy.where(numpy.equal(proc, 1), numpy.left_shift(ones, 3), 0)
    retv = numpy.add(retv, arr)
    del is_bit2_set
    
    # 3 bits to describe NWP input data
    # (maps to pps bits 4&5:)
    is_bit3_set = get_bit_from_flags(data, 3)
    is_bit4_set = get_bit_from_flags(data, 4)
    is_bit5_set = get_bit_from_flags(data, 5)    
    # Put together the three bits into a nwp-flag:
    nwp_bits = (is_bit3_set * numpy.left_shift(ones, 0) +
                is_bit4_set * numpy.left_shift(ones, 1) +
                is_bit5_set * numpy.left_shift(ones, 2))
    arr = numpy.where(numpy.logical_and(numpy.greater_equal(nwp_bits, 3),
                                        numpy.less_equal(nwp_bits, 5)), 
                      numpy.left_shift(ones, 4),
                      0)
    arr = numpy.add(arr, numpy.where(numpy.logical_or(numpy.equal(nwp_bits, 2),
                                                      numpy.equal(nwp_bits, 4)),
                                     numpy.left_shift(ones, 5),
                                     0))

    retv = numpy.add(retv, arr)
    del is_bit3_set
    del is_bit4_set
    del is_bit5_set

    # 2 bits to describe SEVIRI input data
    # (maps to pps bits 6:)
    is_bit6_set = get_bit_from_flags(data, 6)
    is_bit7_set = get_bit_from_flags(data, 7)
    # Put together the two bits into a seviri-flag:
    seviri_bits = (is_bit6_set * numpy.left_shift(ones, 0) +
                   is_bit7_set * numpy.left_shift(ones, 1))
    arr = numpy.where(numpy.greater_equal(seviri_bits, 2),
                      numpy.left_shift(ones, 6), 0)

    retv = numpy.add(retv, arr)
    del is_bit6_set
    del is_bit7_set
    
    # 4 bits to describe which method has been used
    # (maps to pps bits 7&8 and bit 2:)
    is_bit8_set = get_bit_from_flags(data, 8)
    is_bit9_set = get_bit_from_flags(data, 9)
    is_bit10_set = get_bit_from_flags(data, 10)
    is_bit11_set = get_bit_from_flags(data, 11)
    # Put together the four bits into a method-flag:
    method_bits = (is_bit8_set * numpy.left_shift(ones, 0) +
                   is_bit9_set * numpy.left_shift(ones, 1) +
                   is_bit10_set * numpy.left_shift(ones, 2) +
                   is_bit11_set * numpy.left_shift(ones, 3))
    arr = numpy.where(numpy.logical_or(
        numpy.logical_and(numpy.greater_equal(method_bits, 1),
                          numpy.less_equal(method_bits, 2)), 
        numpy.equal(method_bits, 13)), 
                      numpy.left_shift(ones, 2),
                      0)
    arr = numpy.add(arr, 
                    numpy.where(numpy.equal(method_bits, 1),
                                numpy.left_shift(ones, 7),
                                0))
    arr = numpy.add(arr, 
                    numpy.where(numpy.logical_and(
                        numpy.greater_equal(method_bits, 3), 
                        numpy.less_equal(method_bits, 12)), 
                                numpy.left_shift(ones, 8),
                                0))

    # (Maps directly - as well - to the spare bits 9-12) 
    arr = numpy.add(arr, numpy.where(is_bit8_set, numpy.left_shift(ones, 9), 0))
    arr = numpy.add(arr, numpy.where(is_bit9_set,
                                     numpy.left_shift(ones, 10),
                                     0))
    arr = numpy.add(arr, numpy.where(is_bit10_set,
                                     numpy.left_shift(ones, 11),
                                     0))
    arr = numpy.add(arr, numpy.where(is_bit11_set,
                                     numpy.left_shift(ones, 12),
                                     0))   
    retv = numpy.add(retv, arr)
    del is_bit8_set
    del is_bit9_set
    del is_bit10_set
    del is_bit11_set

    # 2 bits to describe the quality of the processing itself
    # (maps to pps bits 14&15:)
    is_bit12_set = get_bit_from_flags(data, 12)
    is_bit13_set = get_bit_from_flags(data, 13)
    # Put together the two bits into a quality-flag:
    qual_bits = (is_bit12_set * numpy.left_shift(ones, 0) +
                 is_bit13_set * numpy.left_shift(ones, 1))
    arr = numpy.where(numpy.logical_and(numpy.greater_equal(qual_bits, 1), 
                                            numpy.less_equal(qual_bits, 2)), 
                        numpy.left_shift(ones, 14), 0)
    arr = numpy.add(arr, 
                    numpy.where(numpy.equal(qual_bits, 2),
                                numpy.left_shift(ones, 15),
                                0))

    retv = numpy.add(retv, arr)
    del is_bit12_set
    del is_bit13_set    
    
    return retv.astype('h')

