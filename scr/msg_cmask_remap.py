#
#
from msg_communications import *
from msg_remap_util import *
from msgpp_config import *

MODULE_ID = "MSG_CMASK_REMAP"

import area
import glob,os

# THIS MODULE ONLY PROVIDES A READER TO THE NWCSAF/MSG
# CLOUDMASK. NO REMAPPING OR ANYTHING, YET.
#
# ----------------------------------------
class msgCloudMaskData:
    def __init__(self):
        self.data = None
        self.scaling_factor=1
        self.offset=0
        self.num_of_lines=0
        self.num_of_columns=0
        self.product=""
        self.id=""
        
class msgCloudMask:
    def __init__(self):
        self.package=""
        self.saf=""
        self.product_name=""
        self.num_of_columns=0
        self.num_of_lines=0
        self.projection_name=""
        self.pcs_def=""
        self.xscale=0
        self.yscale=0
        self.LL_lon=0.0
        self.LL_lat=0.0
        self.UR_lon=0.0
        self.UR_lat=0.0
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
        self.cloudmask=None
        self.processing_flags=None
        self.test_flags=None
        # NO VOLCANIC ASH OR DUST FLAGS TREATED YET!
        
# ------------------------------------------------------------------
def read_msgCmask(filename):
    import _pyhl
    aNodeList=_pyhl.read_nodelist(filename)
    aNodeList.selectAll()
    aNodeList.fetch()

    retv = msgCloudMask()
    retv.cloudmask=msgCloudMaskData()
    retv.processing_flags=msgCloudMaskData()
    retv.test_flags=msgCloudMaskData()
    # Do not bother concerning volcanic ash or dust flags!
    
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
    
    # The cloudmask data
    aNode=aNodeList.getNode("/CMa")
    retv.cloudmask.data=aNode.data()
    aNode=aNodeList.getNode("/CMa/SCALING_FACTOR")
    retv.cloudmask.scaling_factor=aNode.data()
    aNode=aNodeList.getNode("/CMa/OFFSET")
    retv.cloudmask.offset=aNode.data()
    aNode=aNodeList.getNode("/CMa/N_LINES")
    retv.cloudmask.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/CMa/N_COLS")
    retv.cloudmask.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/CMa/PRODUCT")
    retv.cloudmask.product=aNode.data()
    aNode=aNodeList.getNode("/CMa/ID")
    retv.cloudmask.id=aNode.data()
    # ------------------------
    
    # The cloud test data
    aNode=aNodeList.getNode("/CMa_TEST")
    retv.test_flags.data=aNode.data()
    aNode=aNodeList.getNode("/CMa_TEST/SCALING_FACTOR")
    retv.test_flags.scaling_factor=aNode.data()
    aNode=aNodeList.getNode("/CMa_TEST/OFFSET")
    retv.test_flags.offset=aNode.data()
    aNode=aNodeList.getNode("/CMa_TEST/N_LINES")
    retv.test_flags.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/CMa_TEST/N_COLS")
    retv.test_flags.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/CMa_TEST/PRODUCT")
    retv.test_flags.product=aNode.data()
    aNode=aNodeList.getNode("/CMa_TEST/ID")
    retv.test_flags.id=aNode.data()
    # ------------------------
    
    # The cloudmask processing/quality flags
    aNode=aNodeList.getNode("/CMa_QUALITY")
    retv.processing_flags.data=aNode.data()
    aNode=aNodeList.getNode("/CMa_QUALITY/SCALING_FACTOR")
    retv.processing_flags.scaling_factor=aNode.data()
    aNode=aNodeList.getNode("/CMa_QUALITY/OFFSET")
    retv.processing_flags.offset=aNode.data()
    aNode=aNodeList.getNode("/CMa_QUALITY/N_LINES")
    retv.processing_flags.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/CMa_QUALITY/N_COLS")
    retv.processing_flags.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/CMa_QUALITY/PRODUCT")
    retv.processing_flags.product=aNode.data()
    aNode=aNodeList.getNode("/CMa_QUALITY/ID")
    retv.processing_flags.id=aNode.data()
    # ------------------------
    
    return retv


# ------------------------------------------------------------------
def convert_procflags2pps(data):
    import Numeric
    
    ones = Numeric.ones(data.shape,"s")

    # msg illumination bit 0,1,2 (undefined,night,twilight,day,sunglint) maps
    # to pps bits 2, 3 and 4:
    is_bit0_set = get_bit_from_flags(data,0)    
    is_bit1_set = get_bit_from_flags(data,1)    
    is_bit2_set = get_bit_from_flags(data,2)
    illum = is_bit0_set * Numeric.left_shift(ones,0) + \
            is_bit1_set * Numeric.left_shift(ones,1) + \
            is_bit2_set * Numeric.left_shift(ones,2)
    del is_bit0_set
    del is_bit1_set
    del is_bit2_set

    # Night?
    # If night in msg then set pps night bit and nothing else.
    # If twilight in msg then set pps twilight bit and nothing else.
    # If day in msg then unset both the pps night and twilight bits.
    # If sunglint in msg unset both the pps night and twilight bits and set the pps sunglint bit.
    arr = Numeric.where(Numeric.equal(illum,1),Numeric.left_shift(ones,2),0)
    arr = Numeric.where(Numeric.equal(illum,2),Numeric.left_shift(ones,3),arr)
    arr = Numeric.where(Numeric.equal(illum,3),0,arr)
    arr = Numeric.where(Numeric.equal(illum,4),Numeric.left_shift(ones,4),arr)
    retv = Numeric.array(arr)
    del illum
    
    # msg nwp-input bit 3 (nwp present?) maps to pps bit 7:
    # msg nwp-input bit 4 (low level inversion?) maps to pps bit 6:
    is_bit3_set = get_bit_from_flags(data,3)
    is_bit4_set = get_bit_from_flags(data,4)
    nwp = is_bit3_set * Numeric.left_shift(ones,0) + \
          is_bit4_set * Numeric.left_shift(ones,1)
    del is_bit3_set
    del is_bit4_set
    arr = Numeric.where(Numeric.equal(nwp,1),Numeric.left_shift(ones,7),0)
    arr = Numeric.where(Numeric.equal(nwp,2),Numeric.left_shift(ones,7)+Numeric.left_shift(ones,6),arr)
    arr = Numeric.where(Numeric.equal(nwp,3),0,arr)
    retv = Numeric.add(arr,retv)
    del nwp
    
    # msg seviri-input bits 5&6 maps to pps bit 8:
    is_bit5_set = get_bit_from_flags(data,5)
    is_bit6_set = get_bit_from_flags(data,6)
    seviri = is_bit5_set * Numeric.left_shift(ones,0) + \
             is_bit6_set * Numeric.left_shift(ones,1)
    del is_bit5_set
    del is_bit6_set
    retv = Numeric.add(retv,
                       Numeric.where(Numeric.logical_or(Numeric.equal(seviri,2),
                                                        Numeric.equal(seviri,3)),Numeric.left_shift(ones,8),0))
    del seviri
    
    # msg quality bits 7&8 maps to pps bit 9&10:
    is_bit7_set = get_bit_from_flags(data,7)
    is_bit8_set = get_bit_from_flags(data,8)
    quality = is_bit7_set * Numeric.left_shift(ones,0) + \
              is_bit8_set * Numeric.left_shift(ones,1)
    del is_bit7_set
    del is_bit8_set
    arr = Numeric.where(Numeric.equal(quality,2),Numeric.left_shift(ones,9),0)
    arr = Numeric.where(Numeric.equal(quality,3),Numeric.left_shift(ones,10),arr)
    retv = Numeric.add(arr,retv)
    del quality
        
    return retv.astype('s')
