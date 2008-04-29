#
#
from msg_communications import *

from msgpp_config import *
from msg_remap_util import *

import pps_gisdata # From NWCSAF/PPS - ACPG

MODULE_ID = "MSG_CTYPE_REMAP"

import _satproj # From NWCSAF/PPS - ACPG-FUTURE
import epshdf # From NWCSAF/PPS - ACPG
import area
import glob,os
import pps_array2image # From NWCSAF/PPS - ACPG

# ----------------------------------------
class msgCloudTypeData:
    def __init__(self):
        self.data = None
        self.scaling_factor=1
        self.offset=0
        self.num_of_lines=0
        self.num_of_columns=0
        self.product=""
        self.id=""
        
class msgCloudType:
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
        self.cloudtype=None
        self.processing_flags=None
        self.cloudphase=None
        
# ------------------------------------------------------------------
def read_msgCtype(filename):
    import _pyhl
    aNodeList=_pyhl.read_nodelist(filename)
    aNodeList.selectAll()
    #nodenames = aNodeList.getNodeNames()
    #aNodeList.selectNode("/CT")
    aNodeList.fetch()

    retv = msgCloudType()
    retv.cloudtype=msgCloudTypeData()
    retv.processing_flags=msgCloudTypeData()
    retv.cloudphase=msgCloudTypeData()

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
    
    # The cloudtype data
    aNode=aNodeList.getNode("/CT")
    retv.cloudtype.data=aNode.data()
    aNode=aNodeList.getNode("/CT/SCALING_FACTOR")
    retv.cloudtype.scaling_factor=aNode.data()
    aNode=aNodeList.getNode("/CT/OFFSET")
    retv.cloudtype.offset=aNode.data()
    aNode=aNodeList.getNode("/CT/N_LINES")
    retv.cloudtype.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/CT/N_COLS")
    retv.cloudtype.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/CT/PRODUCT")
    retv.cloudtype.product=aNode.data()
    aNode=aNodeList.getNode("/CT/ID")
    retv.cloudtype.id=aNode.data()
    # ------------------------
    
    # The cloud phase data
    aNode=aNodeList.getNode("/CT_PHASE")
    retv.cloudphase.data=aNode.data()
    aNode=aNodeList.getNode("/CT_PHASE/SCALING_FACTOR")
    retv.cloudphase.scaling_factor=aNode.data()
    aNode=aNodeList.getNode("/CT_PHASE/OFFSET")
    retv.cloudphase.offset=aNode.data()
    aNode=aNodeList.getNode("/CT_PHASE/N_LINES")
    retv.cloudphase.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/CT_PHASE/N_COLS")
    retv.cloudphase.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/CT_PHASE/PRODUCT")
    retv.cloudphase.product=aNode.data()
    aNode=aNodeList.getNode("/CT_PHASE/ID")
    retv.cloudphase.id=aNode.data()
    # ------------------------
    
    # The cloudtype processing/quality flags
    aNode=aNodeList.getNode("/CT_QUALITY")
    retv.processing_flags.data=aNode.data()
    aNode=aNodeList.getNode("/CT_QUALITY/SCALING_FACTOR")
    retv.processing_flags.scaling_factor=aNode.data()
    aNode=aNodeList.getNode("/CT_QUALITY/OFFSET")
    retv.processing_flags.offset=aNode.data()
    aNode=aNodeList.getNode("/CT_QUALITY/N_LINES")
    retv.processing_flags.num_of_lines=aNode.data()
    aNode=aNodeList.getNode("/CT_QUALITY/N_COLS")
    retv.processing_flags.num_of_columns=aNode.data()
    aNode=aNodeList.getNode("/CT_QUALITY/PRODUCT")
    retv.processing_flags.product=aNode.data()
    aNode=aNodeList.getNode("/CT_QUALITY/ID")
    retv.processing_flags.id=aNode.data()
    # ------------------------
    
    return retv

# ------------------------------------------------------------------
def msg_ctype2ppsformat(msgctype,satid="Meteosat 8"):
    import area,string

    retv = epshdf.CloudType()
    retv.region=epshdf.SafRegion()
    retv.region.xsize=msgctype.num_of_columns
    retv.region.ysize=msgctype.num_of_lines
    retv.region.id=msgctype.region_name
    retv.region.pcs_id=msgctype.projection_name
    pcsdef=string.join(area.area(msgctype.region_name).pcs.definition)
    retv.region.pcs_def=pcsdef
    retv.region.area_extent=area.area(msgctype.region_name).extent
    retv.satellite_id=satid

    luts = pps_luts()
    retv.cloudtype_lut = luts[0]
    retv.phaseflag_lut = []
    retv.qualityflag_lut = []
    retv.cloudtype_des="MSG SEVIRI Cloud Type"
    retv.qualityflag_des = 'MSG SEVIRI bitwise quality/processing flags'
    retv.phaseflag_des = 'MSG SEVIRI Cloud phase flags'
    
    retv.cloudtype=msgctype.cloudtype.data
    retv.cloudphase=msgctype.cloudphase.data
    retv.qualityflag=convert_procflags2pps(msgctype.processing_flags.data)
    
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
    #print Numeric.minimum.reduce(is_bit0_set.flat),Numeric.maximum.reduce(is_bit0_set.flat)
    #print Numeric.minimum.reduce(is_bit1_set.flat),Numeric.maximum.reduce(is_bit1_set.flat)
    #print Numeric.minimum.reduce(is_bit2_set.flat),Numeric.maximum.reduce(is_bit2_set.flat)
    del is_bit0_set
    del is_bit1_set
    del is_bit2_set
    #print "Illumination flags: min,max=",Numeric.minimum.reduce(illum.flat),Numeric.maximum.reduce(illum.flat)
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
    #print Numeric.minimum.reduce(retv.flat),Numeric.maximum.reduce(retv.flat)
    
    # msg nwp-input bit 3 (nwp present?) maps to pps bit 7:
    # msg nwp-input bit 4 (low level inversion?) maps to pps bit 6:
    is_bit3_set = get_bit_from_flags(data,3)
    is_bit4_set = get_bit_from_flags(data,4)
    nwp = is_bit3_set * Numeric.left_shift(ones,0) + \
          is_bit4_set * Numeric.left_shift(ones,1)
    #print Numeric.minimum.reduce(is_bit3_set.flat),Numeric.maximum.reduce(is_bit3_set.flat)
    #print Numeric.minimum.reduce(is_bit4_set.flat),Numeric.maximum.reduce(is_bit4_set.flat)
    #print "Nwp flags: min,max=",Numeric.minimum.reduce(nwp.flat),Numeric.maximum.reduce(nwp.flat)
    del is_bit3_set
    del is_bit4_set
    arr = Numeric.where(Numeric.equal(nwp,1),Numeric.left_shift(ones,7),0)
    arr = Numeric.where(Numeric.equal(nwp,2),Numeric.left_shift(ones,7)+Numeric.left_shift(ones,6),arr)
    arr = Numeric.where(Numeric.equal(nwp,3),0,arr)
    retv = Numeric.add(arr,retv)
    del nwp
    #print Numeric.minimum.reduce(retv.flat),Numeric.maximum.reduce(retv.flat)
    
    # msg seviri-input bits 5&6 maps to pps bit 8:
    is_bit5_set = get_bit_from_flags(data,5)
    is_bit6_set = get_bit_from_flags(data,6)
    seviri = is_bit5_set * Numeric.left_shift(ones,0) + \
             is_bit6_set * Numeric.left_shift(ones,1)
    #print "Seviri flags: min,max=",Numeric.minimum.reduce(seviri.flat),Numeric.maximum.reduce(seviri.flat)
    del is_bit5_set
    del is_bit6_set
    retv = Numeric.add(retv,
                       Numeric.where(Numeric.logical_or(Numeric.equal(seviri,2),
                                                        Numeric.equal(seviri,3)),Numeric.left_shift(ones,8),0))
    del seviri
    #print Numeric.minimum.reduce(retv.flat),Numeric.maximum.reduce(retv.flat)
    
    # msg quality bits 7&8 maps to pps bit 9&10:
    is_bit7_set = get_bit_from_flags(data,7)
    is_bit8_set = get_bit_from_flags(data,8)
    quality = is_bit7_set * Numeric.left_shift(ones,0) + \
              is_bit8_set * Numeric.left_shift(ones,1)
    #print "Quality flags: min,max=",Numeric.minimum.reduce(quality.flat),Numeric.maximum.reduce(quality.flat)   
    del is_bit7_set
    del is_bit8_set
    arr = Numeric.where(Numeric.equal(quality,2),Numeric.left_shift(ones,9),0)
    arr = Numeric.where(Numeric.equal(quality,3),Numeric.left_shift(ones,10),arr)
    retv = Numeric.add(arr,retv)
    del quality
    #print Numeric.minimum.reduce(retv.flat),Numeric.maximum.reduce(retv.flat)
    
    # msg bit 9 (stratiform-cumuliform distinction?) maps to pps bit 11:
    is_bit9_set = get_bit_from_flags(data,9)
    retv = Numeric.add(retv,Numeric.where(is_bit9_set,Numeric.left_shift(ones,11),0))
    del is_bit9_set
    #print Numeric.minimum.reduce(retv.flat),Numeric.maximum.reduce(retv.flat)
    
    return retv.astype('s')

# ------------------------------------------------------------------
def pps_luts():
    ctype_lut = ['0: Not processed', '1: Cloud free land', '2: Cloud free sea', '3: Snow/ice contaminated land', '4: Snow/ice contaminated sea', '5: Very low cumiliform cloud', '6: Very low stratiform cloud', '7: Low cumiliform cloud', '8: Low stratiform cloud', '9: Medium level cumiliform cloud', '10: Medium level stratiform cloud', '11: High and opaque cumiliform cloud', '12: High and opaque stratiform cloud', '13:Very high and opaque cumiliform cloud', '14: Very high and opaque stratiform cloud', '15: Very thin cirrus cloud', '16: Thin cirrus cloud', '17: Thick cirrus cloud', '18: Cirrus above low or medium level cloud', '19: Fractional or sub-pixel cloud', '20: Undefined']
    phase_lut = ['1: Not processed or undefined', '2: Water', '4: Ice', '8: Tb11 below 260K', '16: value not defined', '32: value not defined', '64: value not defined', '128: value not defined']
    quality_lut = ['1: Land', '2: Coast', '4: Night', '8: Twilight', '16: Sunglint', '32: High terrain', '64: Low level inversion', '128: Nwp data present', '256: Avhrr channel missing', '512: Low quality', '1024: Reclassified after spatial smoothing', '2048: Stratiform-Cumuliform Distinction performed', '4096: bit not defined', '8192: bit not defined', '16384: bit not defined', '32768: bit not defined']

    return ctype_lut, phase_lut, quality_lut

# ------------------------------------------------------------------
def msg_remap(msgctype,lon,lat,areaid):
    import area    
    a=area.area(areaid)
    b = _satproj.create_coverage(a,lon,lat,1)    
    msgctype.cloudtype.data = _satproj.project(b.coverage,b.rowidx,b.colidx,msgctype.cloudtype.data)
    msgctype.cloudphase.data = _satproj.project(b.coverage,b.rowidx,b.colidx,msgctype.cloudphase.data)
    msgctype.processing_flags.data = _satproj.project(b.coverage,b.rowidx,b.colidx,msgctype.processing_flags.data)    
    del b

    msgctype.region_name = areaid
    msgctype.projection_name = a.pcs.id
    msgctype.num_of_columns = a.xsize
    msgctype.num_of_lines = a.ysize
    msgctype.cloudtype.num_of_columns = a.xsize
    msgctype.cloudtype.num_of_lines = a.ysize
    msgctype.cloudphase.num_of_columns = a.xsize
    msgctype.cloudphase.num_of_lines = a.ysize
    msgctype.processing_flags.num_of_columns = a.xsize
    msgctype.processing_flags.num_of_lines = a.ysize    

    return msgctype

# ------------------------------------------------------------------
def OLDmsgCtype_remap_fast(cov,msgctype,areaid,a):
    msgctype.cloudtype.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctype.cloudtype.data)
    msgctype.cloudphase.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctype.cloudphase.data)
    msgctype.processing_flags.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctype.processing_flags.data)    

    msgctype.region_name = areaid
    msgctype.projection_name = a.pcs.id
    msgctype.num_of_columns = a.xsize
    msgctype.num_of_lines = a.ysize
    msgctype.cloudtype.num_of_columns = a.xsize
    msgctype.cloudtype.num_of_lines = a.ysize
    msgctype.cloudphase.num_of_columns = a.xsize
    msgctype.cloudphase.num_of_lines = a.ysize
    msgctype.processing_flags.num_of_columns = a.xsize
    msgctype.processing_flags.num_of_lines = a.ysize    

    return msgctype

# ------------------------------------------------------------------
def msgCtype_remap_fast(cov,msgctype,areaid,a):
    import string
    
    retv = msgCloudType()
    
    retv.package = msgctype.package
    retv.saf = msgctype.saf
    retv.product_name = msgctype.product_name
    #retv.num_of_columns = msgctype.num_of_columns
    #retv.num_of_lines = msgctype.num_of_lines
    #retv.projection_name = msgctype.projection_name
    #retv.region_name = msgctype.region_name
    retv.cfac = msgctype.cfac
    retv.lfac = msgctype.lfac
    retv.coff = msgctype.coff
    retv.loff = msgctype.loff
    retv.nb_param = msgctype.nb_param
    retv.gp_sc_id = msgctype.gp_sc_id
    retv.image_acquisition_time = msgctype.image_acquisition_time
    retv.spectral_channel_id = msgctype.spectral_channel_id
    retv.nominal_product_time = msgctype.nominal_product_time
    retv.sgs_product_quality = msgctype.sgs_product_quality
    retv.sgs_product_completeness = msgctype.sgs_product_completeness
    retv.product_algorithm_version = msgctype.product_algorithm_version
    
    retv.cloudtype=msgCloudTypeData()
    retv.processing_flags=msgCloudTypeData()
    retv.cloudphase=msgCloudTypeData()

    retv.cloudtype.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctype.cloudtype.data)
    retv.cloudphase.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctype.cloudphase.data)
    retv.processing_flags.data = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,msgctype.processing_flags.data)    

    retv.region_name = areaid
    retv.projection_name = a.pcs.id
    pcsdef=string.join(a.pcs.definition)
    retv.pcs_def=pcsdef

    retv.num_of_columns = a.xsize
    retv.num_of_lines = a.ysize
    retv.xscale = abs(a.extent[2]-a.extent[0])/a.xsize
    retv.yscale = abs(a.extent[3]-a.extent[1])/a.ysize
    ll_lonlat = pps_gisdata.xy2lonlat(areaid,0,a.ysize)
    ur_lonlat = pps_gisdata.xy2lonlat(areaid,a.xsize,0)
    retv.LL_lon = ll_lonlat[0]
    retv.LL_lat = ll_lonlat[1]
    retv.UR_lon = ur_lonlat[0]
    retv.UR_lat = ur_lonlat[1]

    
    retv.cloudtype.offset = msgctype.cloudtype.offset    
    retv.cloudtype.scaling_factor = msgctype.cloudtype.scaling_factor    
    retv.cloudtype.id = msgctype.cloudtype.id
    retv.cloudtype.product = msgctype.cloudtype.product
    retv.cloudtype.num_of_columns = a.xsize
    retv.cloudtype.num_of_lines = a.ysize

    retv.cloudphase.offset = msgctype.cloudphase.offset    
    retv.cloudphase.scaling_factor = msgctype.cloudphase.scaling_factor    
    retv.cloudphase.id = msgctype.cloudphase.id
    retv.cloudphase.product = msgctype.cloudphase.product
    retv.cloudphase.num_of_columns = a.xsize
    retv.cloudphase.num_of_lines = a.ysize

    retv.cloudtype.offset = msgctype.cloudtype.offset    
    retv.cloudtype.scaling_factor = msgctype.cloudtype.scaling_factor    
    retv.cloudtype.id = msgctype.cloudtype.id
    retv.cloudtype.product = msgctype.cloudtype.product
    retv.processing_flags.num_of_columns = a.xsize
    retv.processing_flags.num_of_lines = a.ysize    

    return retv

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

    MetSat=MSG_SATELLITE

    import time
    timetup = time.localtime(time.mktime((year,month,day,0,0,0,0,0,0)))    
    jday=timetup[7]
    msgwrite_log("INFO","year,month,day: %d %d %d Julian day = %d"%(year,month,day,jday),moduleid=MODULE_ID)
    #hour = slotn/4
    #minute = (slotn%4)*15
    
    lon = read_msg_lonlat(LONFILE)
    lat = read_msg_lonlat(LATFILE)
    
    in_aid=MSG_AREA
    #prefix="SAFNWC_MSG%.1d_CT___%.2d%.3d_%.3d_%s"%(MSG_NUMBER,year-2000,jday,slotn,in_aid)    
    prefix="SAFNWC_MSG%.1d_CT___%.4d%.2d%.2d%.2d%.2d_%s"%(MSG_NUMBER,year,month,day,hour,minute,in_aid)
    a=area.area(areaid)

    # Check for existing coverage file for the area:
    covfilename = "%s/cst/msg_coverage_%s.%s.hdf"%(APPLDIR,in_aid,areaid)
    if not os.path.exists(covfilename):
        cov = _satproj.create_coverage(a,lon,lat,1)
        writeCoverage(cov,covfilename,in_aid,areaid)
    else:
        cov,info = readCoverage(covfilename)
        #print info.items()

    for infile in glob.glob("%s/%s*h5"%(CTYPEDIR_IN,prefix)):
        s=string.ljust(areaid,12)
        ext=string.replace(s," ","_")
        outfile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.cloudtype.hdf"%(CTYPEDIR_OUT,MetSat,year,month,day,hour,minute,areaid)
        msgwrite_log("INFO","Output file: ",outfile,moduleid=MODULE_ID)
        if not os.path.exists(outfile):
            msgctype = read_msgCtype(infile)
            msgctype = msgCtype_remap_fast(cov,msgctype,areaid,a)
            ctype = msg_ctype2ppsformat(msgctype)
            epshdf.write_cloudtype(outfile,ctype,6)

        # Test reading it and generating a png image....
        that = epshdf.read_cloudtype(outfile,1,0,0)
        legend = pps_array2image.get_cms_modified()
        this = pps_array2image.cloudtype2image(that.cloudtype,legend)
        size=this.size
        imagefile = outfile.split(".hdf")[0] + ".png"
        this.save(imagefile)
        this.thumbnail((size[0]/3,size[1]/3))
        thumbnail = outfile.split(".hdf")[0] + ".thumbnail.png"
        this.save(thumbnail)

