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
    """NWCSAF/MSG Cloud Type data layer
    """    
    def __init__(self):
        self.data = None
        self.scaling_factor=1
        self.offset=0
        self.num_of_lines=0
        self.num_of_columns=0
        self.product=""
        self.id=""
        
class msgCloudType:
    """NWCSAF/MSG Cloud Type data structure as retrieved from HDF5 file
    """
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
    def read_msgCtype(self,filename):
        """Reader for the NWCSAF/MSG cloudtype. Use *filename* to read data.
        """
        import _pyhl
        aNodeList=_pyhl.read_nodelist(filename)
        aNodeList.selectAll()
        aNodeList.fetch()
        
        self.cloudtype=msgCloudTypeData()
        self.processing_flags=msgCloudTypeData()
        self.cloudphase=msgCloudTypeData()
        
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
    
        # The cloudtype data
        aNode=aNodeList.getNode("/CT")
        self.cloudtype.data=aNode.data()
        aNode=aNodeList.getNode("/CT/SCALING_FACTOR")
        self.cloudtype.scaling_factor=aNode.data()
        aNode=aNodeList.getNode("/CT/OFFSET")
        self.cloudtype.offset=aNode.data()
        aNode=aNodeList.getNode("/CT/N_LINES")
        self.cloudtype.num_of_lines=aNode.data()
        aNode=aNodeList.getNode("/CT/N_COLS")
        self.cloudtype.num_of_columns=aNode.data()
        aNode=aNodeList.getNode("/CT/PRODUCT")
        self.cloudtype.product=aNode.data()
        aNode=aNodeList.getNode("/CT/ID")
        self.cloudtype.id=aNode.data()
        # ------------------------
    
        # The cloud phase data
        aNode=aNodeList.getNode("/CT_PHASE")
        self.cloudphase.data=aNode.data()
        aNode=aNodeList.getNode("/CT_PHASE/SCALING_FACTOR")
        self.cloudphase.scaling_factor=aNode.data()
        aNode=aNodeList.getNode("/CT_PHASE/OFFSET")
        self.cloudphase.offset=aNode.data()
        aNode=aNodeList.getNode("/CT_PHASE/N_LINES")
        self.cloudphase.num_of_lines=aNode.data()
        aNode=aNodeList.getNode("/CT_PHASE/N_COLS")
        self.cloudphase.num_of_columns=aNode.data()
        aNode=aNodeList.getNode("/CT_PHASE/PRODUCT")
        self.cloudphase.product=aNode.data()
        aNode=aNodeList.getNode("/CT_PHASE/ID")
        self.cloudphase.id=aNode.data()
        # ------------------------
    
        # The cloudtype processing/quality flags
        aNode=aNodeList.getNode("/CT_QUALITY")
        self.processing_flags.data=aNode.data()
        aNode=aNodeList.getNode("/CT_QUALITY/SCALING_FACTOR")
        self.processing_flags.scaling_factor=aNode.data()
        aNode=aNodeList.getNode("/CT_QUALITY/OFFSET")
        self.processing_flags.offset=aNode.data()
        aNode=aNodeList.getNode("/CT_QUALITY/N_LINES")
        self.processing_flags.num_of_lines=aNode.data()
        aNode=aNodeList.getNode("/CT_QUALITY/N_COLS")
        self.processing_flags.num_of_columns=aNode.data()
        aNode=aNodeList.getNode("/CT_QUALITY/PRODUCT")
        self.processing_flags.product=aNode.data()
        aNode=aNodeList.getNode("/CT_QUALITY/ID")
        self.processing_flags.id=aNode.data()
        # ------------------------

    def save_cloudtype(self,filename):
        ctype = msg_ctype2ppsformat(self)
        msg_communications.msgwrite_log("INFO",
                                        "Saving CType hdf file...",
                                        moduleid=MODULE_ID)
        epshdf.write_cloudtype(filename, ctype, 6)
        msg_communications.msgwrite_log("INFO",
                                        "Saving CType hdf file done !",
                                        moduleid=MODULE_ID)

    
    def project(self,coverage,dest_area):
        """Remaps the NWCSAF/MSG Cloud Type to cartographic map-projection on
        area give by a pre-registered area-id. Faster version of msg_remap!
        """
        import string
        import area
        
        a = area.area(dest_area)

        retv = msgCloudType()
        
        retv.package = self.package
        retv.saf = self.saf
        retv.product_name = self.product_name
        retv.region_name = dest_area
        retv.cfac = self.cfac
        retv.lfac = self.lfac
        retv.coff = self.coff
        retv.loff = self.loff
        retv.nb_param = self.nb_param
        retv.gp_sc_id = self.gp_sc_id
        retv.image_acquisition_time = self.image_acquisition_time
        retv.spectral_channel_id = self.spectral_channel_id
        retv.nominal_product_time = self.nominal_product_time
        retv.sgs_product_quality = self.sgs_product_quality
        retv.sgs_product_completeness = self.sgs_product_completeness
        retv.product_algorithm_version = self.product_algorithm_version
        
        retv.cloudtype=msgCloudTypeData()
        retv.processing_flags=msgCloudTypeData()
        retv.cloudphase=msgCloudTypeData()

        retv.cloudtype.data = coverage.project_array(self.cloudtype.data)
        retv.cloudphase.data = coverage.project_array(self.cloudphase.data)
        retv.processing_flags.data = \
            coverage.project_array(self.processing_flags.data)
        
        retv.region_name = dest_area
        retv.projection_name = a.pcs.id
        pcsdef=string.join(a.pcs.definition)
        retv.pcs_def=pcsdef
        
        retv.num_of_columns = a.xsize
        retv.num_of_lines = a.ysize
        retv.xscale = abs(a.extent[2]-a.extent[0])/a.xsize
        retv.yscale = abs(a.extent[3]-a.extent[1])/a.ysize
        ll_lonlat = pps_gisdata.xy2lonlat(dest_area,0,a.ysize)
        ur_lonlat = pps_gisdata.xy2lonlat(dest_area,a.xsize,0)
        retv.LL_lon = ll_lonlat[0]
        retv.LL_lat = ll_lonlat[1]
        retv.UR_lon = ur_lonlat[0]
        retv.UR_lat = ur_lonlat[1]
        
        
        retv.cloudtype.offset = self.cloudtype.offset    
        retv.cloudtype.scaling_factor = self.cloudtype.scaling_factor    
        retv.cloudtype.id = self.cloudtype.id
        retv.cloudtype.product = self.cloudtype.product
        retv.cloudtype.num_of_columns = a.xsize
        retv.cloudtype.num_of_lines = a.ysize
            
        retv.cloudphase.offset = self.cloudphase.offset    
        retv.cloudphase.scaling_factor = self.cloudphase.scaling_factor    
        retv.cloudphase.id = self.cloudphase.id
        retv.cloudphase.product = self.cloudphase.product
        retv.cloudphase.num_of_columns = a.xsize
        retv.cloudphase.num_of_lines = a.ysize
        
        retv.cloudtype.offset = self.cloudtype.offset    
        retv.cloudtype.scaling_factor = self.cloudtype.scaling_factor    
        retv.cloudtype.id = self.cloudtype.id
        retv.cloudtype.product = self.cloudtype.product
        retv.processing_flags.num_of_columns = a.xsize
        retv.processing_flags.num_of_lines = a.ysize    
        
        return retv


# ------------------------------------------------------------------
def msg_ctype2ppsformat(msgctype,satid="Meteosat 8"):
    """Converts the NWCSAF/MSG Cloud Type to the PPS format,
    in order to have consistency in output format between PPS and MSG.
    """
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
    """Converting cloud type processing flags to
    the PPS format, in order to have consistency between
    PPS and MSG cloud type contents.
    """
    import numpy
    
    ones = numpy.ones(data.shape,"h")

    # msg illumination bit 0,1,2 (undefined,night,twilight,day,sunglint) maps
    # to pps bits 2, 3 and 4:
    is_bit0_set = get_bit_from_flags(data,0)    
    is_bit1_set = get_bit_from_flags(data,1)    
    is_bit2_set = get_bit_from_flags(data,2)
    illum = is_bit0_set * numpy.left_shift(ones,0) + \
            is_bit1_set * numpy.left_shift(ones,1) + \
            is_bit2_set * numpy.left_shift(ones,2)
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
    arr = numpy.where(numpy.equal(illum,1),numpy.left_shift(ones,2),0)
    arr = numpy.where(numpy.equal(illum,2),numpy.left_shift(ones,3),arr)
    arr = numpy.where(numpy.equal(illum,3),0,arr)
    arr = numpy.where(numpy.equal(illum,4),numpy.left_shift(ones,4),arr)
    retv = numpy.array(arr)
    del illum
    #print Numeric.minimum.reduce(retv.flat),Numeric.maximum.reduce(retv.flat)
    
    # msg nwp-input bit 3 (nwp present?) maps to pps bit 7:
    # msg nwp-input bit 4 (low level inversion?) maps to pps bit 6:
    is_bit3_set = get_bit_from_flags(data,3)
    is_bit4_set = get_bit_from_flags(data,4)
    nwp = is_bit3_set * numpy.left_shift(ones,0) + \
          is_bit4_set * numpy.left_shift(ones,1)
    #print Numeric.minimum.reduce(is_bit3_set.flat),Numeric.maximum.reduce(is_bit3_set.flat)
    #print Numeric.minimum.reduce(is_bit4_set.flat),Numeric.maximum.reduce(is_bit4_set.flat)
    #print "Nwp flags: min,max=",Numeric.minimum.reduce(nwp.flat),Numeric.maximum.reduce(nwp.flat)
    del is_bit3_set
    del is_bit4_set
    arr = numpy.where(numpy.equal(nwp,1),numpy.left_shift(ones,7),0)
    arr = numpy.where(numpy.equal(nwp,2),numpy.left_shift(ones,7)+numpy.left_shift(ones,6),arr)
    arr = numpy.where(numpy.equal(nwp,3),0,arr)
    retv = numpy.add(arr,retv)
    del nwp
    #print Numeric.minimum.reduce(retv.flat),Numeric.maximum.reduce(retv.flat)
    
    # msg seviri-input bits 5&6 maps to pps bit 8:
    is_bit5_set = get_bit_from_flags(data,5)
    is_bit6_set = get_bit_from_flags(data,6)
    seviri = is_bit5_set * numpy.left_shift(ones,0) + \
             is_bit6_set * numpy.left_shift(ones,1)
    #print "Seviri flags: min,max=",Numeric.minimum.reduce(seviri.flat),Numeric.maximum.reduce(seviri.flat)
    del is_bit5_set
    del is_bit6_set
    retv = numpy.add(retv,
                       numpy.where(numpy.logical_or(numpy.equal(seviri,2),
                                                        numpy.equal(seviri,3)),numpy.left_shift(ones,8),0))
    del seviri
    #print Numeric.minimum.reduce(retv.flat),Numeric.maximum.reduce(retv.flat)
    
    # msg quality bits 7&8 maps to pps bit 9&10:
    is_bit7_set = get_bit_from_flags(data,7)
    is_bit8_set = get_bit_from_flags(data,8)
    quality = is_bit7_set * numpy.left_shift(ones,0) + \
              is_bit8_set * numpy.left_shift(ones,1)
    #print "Quality flags: min,max=",Numeric.minimum.reduce(quality.flat),Numeric.maximum.reduce(quality.flat)   
    del is_bit7_set
    del is_bit8_set
    arr = numpy.where(numpy.equal(quality,2),numpy.left_shift(ones,9),0)
    arr = numpy.where(numpy.equal(quality,3),numpy.left_shift(ones,10),arr)
    retv = numpy.add(arr,retv)
    del quality
    #print Numeric.minimum.reduce(retv.flat),Numeric.maximum.reduce(retv.flat)
    
    # msg bit 9 (stratiform-cumuliform distinction?) maps to pps bit 11:
    is_bit9_set = get_bit_from_flags(data,9)
    retv = numpy.add(retv,numpy.where(is_bit9_set,numpy.left_shift(ones,11),0))
    del is_bit9_set
    #print Numeric.minimum.reduce(retv.flat),Numericx.maximum.reduce(retv.flat)
    
    return retv.astype('h')

# ------------------------------------------------------------------
def pps_luts():
    """Gets the LUTs for the PPS Cloud Type data fields.
    Returns a tuple with Cloud Type lut, Cloud Phase lut, Processing flags lut
    """
    ctype_lut = ['0: Not processed', '1: Cloud free land', '2: Cloud free sea', '3: Snow/ice contaminated land', '4: Snow/ice contaminated sea', '5: Very low cumiliform cloud', '6: Very low stratiform cloud', '7: Low cumiliform cloud', '8: Low stratiform cloud', '9: Medium level cumiliform cloud', '10: Medium level stratiform cloud', '11: High and opaque cumiliform cloud', '12: High and opaque stratiform cloud', '13:Very high and opaque cumiliform cloud', '14: Very high and opaque stratiform cloud', '15: Very thin cirrus cloud', '16: Thin cirrus cloud', '17: Thick cirrus cloud', '18: Cirrus above low or medium level cloud', '19: Fractional or sub-pixel cloud', '20: Undefined']
    phase_lut = ['1: Not processed or undefined', '2: Water', '4: Ice', '8: Tb11 below 260K', '16: value not defined', '32: value not defined', '64: value not defined', '128: value not defined']
    quality_lut = ['1: Land', '2: Coast', '4: Night', '8: Twilight', '16: Sunglint', '32: High terrain', '64: Low level inversion', '128: Nwp data present', '256: Avhrr channel missing', '512: Low quality', '1024: Reclassified after spatial smoothing', '2048: Stratiform-Cumuliform Distinction performed', '4096: bit not defined', '8192: bit not defined', '16384: bit not defined', '32768: bit not defined']

    return ctype_lut, phase_lut, quality_lut

# ------------------------------------------------------------------
def msg_remap(msgctype,lon,lat,areaid):
    """
    Remaps the NWCSAF/MSG Cloyd Type to cartographic map-projection on
    area give by a pre-registered area-id

    @type msgctype: msgCloudType instance
    @param msgctype: NWCSAF/MSG Cloud Type instance 
    @type lon: Array
    @param lon: Longitude array of input Cloud Type data
    @type lat: Array
    @param lat: Latitude array of input Cloud Type data
    @type areaid: String
    @param areaid: Area id of output result
    @rtype: msgCloudType instance
    @return: NWCSAF/MSG Cloud Type instance
    """
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
    covfilename = "%s/msg_coverage_%s.%s.hdf"%(DATADIR,in_aid,areaid)
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

