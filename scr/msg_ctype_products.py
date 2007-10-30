# -*- coding: UTF-8 -*-
# **************************************************************************
#
#  COPYRIGHT   : SMHI
#  PRODUCED BY : Swedish Meteorological and Hydrological Institute (SMHI)
#                Folkborgsvaegen 1
#                Norrköping, Sweden
#
#  PROJECT      : 
#  FILE         : msg_ctype_products.py
#  TYPE         : Python program
#  PACKAGE      : Nowcasting-SAF Post processing for MSG
#
#  SUMMARY      : 
# 
#  DESCRIPTION  :
#
#  SYNOPSIS     :
#
#  OPTIONS      : None
#
# *************************************************************************
#
# CVS History:
#
# $Id: msg_ctype_products.py,v 1.10 2007/10/30 14:39:39 adybbroe Exp $
#
# $Log: msg_ctype_products.py,v $
# Revision 1.10  2007/10/30 14:39:39  adybbroe
# Changes to bring in and older version from cvs release 0.27, that seem
# to have been lost. The stretching of channel 9 bw data for SVT should
# be less sensitive to diurnal cycle now again - this was in previously
# but was lost in release 0.30. Also added functions to write channel
# data (brighness temperatures, radiances and reflectances) from the
# NWCSAF/MSG temporary binary format in hdf5. This should be useful for
# archiving.
#
#
# *************************************************************************
#
#
#
from msgpp_config import *
from msg_remap_util import *
from msg_ctype_remap import *
from msg_rgb_remap import *

# ------------------------------------------------------------------
# Product for the Swedish road authorities (Vaegverket): Focus on low clouds and fog.
# Cloudfree green and blue background.
# All clouds, except "very low" and "low" according to classification are represented in greyscale
# using the 10 micron IR channel (channel number 9 on SEVIRI).
# All low and very low clouds are represented in their usual colours (red and orange/yellow).
#
def make_ctype_prod01(irch,ctypefile,areaid,**options):
    import acpgimage,_acpgpilext
    import smhi_safnwc_legends
    import Numeric
    import Image
    import pps_array2image
    
    if options.has_key("overlay"):
        withCoast = options["overlay"]
    else:
        withCoast = 0
        
    if options.has_key("gamma"):
        gamma=options["gamma"]
    else:
        gamma = 1.0

    # Generate bw IR image:
    if options.has_key("gamma"):
        bw = get_bw_array(irch,stretch="gamma",gamma=gamma,inverse=1)
    else:
        bw = get_bw_array(irch,stretch="crude-linear",bwrange=[225.0,285.0],inverse=1)

    if not os.path.exists(ctypefile):
        print "ERROR: Cloud Type product not found! Filename = %s"%ctypefile
        return
        
    # Read the Cloud Type product:
    that = epshdf.read_cloudtype(ctypefile,1,0,0)
    legend = smhi_safnwc_legends.get_vv_legend()
    arr = Numeric.where(Numeric.logical_and(Numeric.less_equal(that.cloudtype,8),
                                            Numeric.greater_equal(that.cloudtype,5)),that.cloudtype-2,bw)
    arr = Numeric.where(Numeric.less_equal(that.cloudtype,2),that.cloudtype,arr).astype('b')
    # Put the snow&ice as cloudfree land/sea:
    #arr = Numeric.where(Numeric.logical_and(Numeric.less_equal(that.cloudtype,4),
    #                                        Numeric.greater_equal(that.cloudtype,3)),that.cloudtype-2,arr)
    # The above was in before (version 0.27) but seems to have been lost - but knowone has complained!
    # Check with Claes Brundin!
    # Adam Dybbroe, 2007-10-30
    #
    shape = that.cloudtype.shape    
    size=shape[1],shape[0]
    this = Image.fromstring("P",size,arr.tostring())
    newleg=[]
    for i in legend:    
	newleg = newleg + list(i)
    this.putpalette(newleg)
    this = this.convert("RGB")
    retv = this.copy()
    
    if withCoast:
        msgwrite_log("INFO","Add coastlines and political borders to image. Area = %s"%(areaid),moduleid=MODULE_ID)
        rimg = acpgimage.image(areaid)
        rimg.info["nodata"]=255
        rimg.data = arr.astype('b')
        area_overlayfile = "%s/coastlines_%s.asc"%(AUX_DIR,areaid)
        msgwrite_log("INFO","Read overlay. Try find something prepared on the area...",moduleid=MODULE_ID)
        try:
            overlay = _acpgpilext.read_overlay(area_overlayfile)
            msgwrite_log("INFO","Got overlay for area: ",area_overlayfile,moduleid=MODULE_ID)
        except:            
            msgwrite_log("INFO","Didn't find an area specific overlay. Have to read world-map...",moduleid=MODULE_ID)
            overlay = _acpgpilext.read_overlay(COAST_FILE)
            pass        
        thumb = this.copy()
        msgwrite_log("INFO","Add overlay",moduleid=MODULE_ID)
        this = pps_array2image.add_overlay(rimg,overlay,this)

    if PRODUCT_IMAGES["PGE02"].has_key(areaid) and  PRODUCT_IMAGES["PGE02"][areaid].has_key("standard"):
        imformat = PRODUCT_IMAGES["PGE02"][areaid]["standard"][0]
        imagefile = ctypefile.split(".hdf")[0] + "_ir.%s"%imformat
        this.save(imagefile)
        thumb.thumbnail((size[0]/3,size[1]/3))
        thumbnail = ctypefile.split(".hdf")[0] + "_ir.thumbnail.%s"%imformat
        thumb.save(thumbnail)
    else:
        msgwrite_log("WARNING","No image format specified in configuration... No image saved!",moduleid=MODULE_ID)
        
    return retv,this

# ------------------------------------------------------------------
# Product for tv: Cloud movie with cloudfree green and blue background.
# All clouds according to classification are represented in greyscale using the 10 micron IR channel
# (channel number 9 on SEVIRI).
#
def make_ctype_prod02(irch,ctypefile,areaid,**options):
    import acpgimage,_acpgpilext
    import smhi_safnwc_legends
    import Numeric
    import Image
    import pps_array2image
    nodata = 0 # Should check this and make a better solution for future relases, Ad 2007-10-30
    
    if options.has_key("overlay"):
        withCoast = options["overlay"]
    else:
        withCoast = 0
        
    if options.has_key("gamma"):
        gamma=options["gamma"]
    else:
        gamma = 1.0
    if options.has_key("stretch"):
        stretch=options["stretch"]
    else:
        stretch = "linear"

    if not os.path.exists(ctypefile):
        msgwrite_log("ERROR","Cloud Type product not found! Filename = %s"%ctypefile,moduleid=MODULE_ID)
        return

    # Read the Cloud Type product:
    that = epshdf.read_cloudtype(ctypefile,1,0,0)
    legend = smhi_safnwc_legends.get_tv_legend()

    # Stretching ir-channel only on the cloudy pixels!
    irch = Numeric.where(Numeric.less_equal(that.cloudtype,4),0,irch)

    # Generate bw IR image:
    if options.has_key("gamma"):
        bw = get_bw_array(irch,stretch="gamma",gamma=gamma,inverse=1,nodata=nodata,missingdata=0)
    else:
        bw = get_bw_array(irch,stretch="crude-linear",bwrange=[225.0,285.0],inverse=1,missingdata=0,nodata=nodata)
        
    arr = Numeric.where(Numeric.less_equal(that.cloudtype,4),that.cloudtype,bw).astype('b')

    shape = that.cloudtype.shape    
    size=shape[1],shape[0]
    this = Image.fromstring("P",size,arr.tostring())
    newleg=[]
    for i in legend:    
	newleg = newleg + list(i)
    this.putpalette(newleg)
    this = this.convert("RGB")
    retv = this.copy()
    thumb = this.copy()
    
    if withCoast:
        msgwrite_log("INFO","Add coastlines and political borders to image. Area = %s"%(areaid),moduleid=MODULE_ID)
        rimg = acpgimage.image(areaid)
        rimg.info["nodata"]=255
        rimg.data = arr.astype('b')
        area_overlayfile = "%s/coastlines_%s.asc"%(AUX_DIR,areaid)
        msgwrite_log("INFO","Read overlay. Try find something prepared on the area...",moduleid=MODULE_ID)
        try:
            overlay = _acpgpilext.read_overlay(area_overlayfile)
            msgwrite_log("INFO","Got overlay for area: ",area_overlayfile,moduleid=MODULE_ID)
        except:            
            msgwrite_log("INFO","Didn't find an area specific overlay. Have to read world-map...",moduleid=MODULE_ID)
            overlay = _acpgpilext.read_overlay(COAST_FILE)
            pass        
        msgwrite_log("INFO","Add overlay",moduleid=MODULE_ID)
        this = pps_array2image.add_overlay(rimg,overlay,this)

    if PRODUCT_IMAGES["PGE02"].has_key(areaid) and  PRODUCT_IMAGES["PGE02"][areaid].has_key("standard"):
        imformat = PRODUCT_IMAGES["PGE02"][areaid]["standard"][0]
        imagefile = ctypefile.split(".hdf")[0] + "_irtv.%s"%imformat
        this.save(imagefile,quality=100)
        thumb.thumbnail((size[0]/3,size[1]/3))
        thumbnail = ctypefile.split(".hdf")[0] + "_irtv.thumbnail.%s"%imformat
        thumb.save(thumbnail,quality=100)
    else:
        msgwrite_log("WARNING","No image format specified in configuration... No image saved!",moduleid=MODULE_ID)

    return retv,this

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
    import Image, Numeric
    import _satproj
    import epshdf
    import area
    import glob,os

    MetSat=MSG_SATELLITE
    in_aid=MSG_AREA
    a=area.area(areaid)

    timetup = time.localtime(time.mktime((year,month,day,0,0,0,0,0,0)))    
    jday=timetup[7]
    print "year,month,day: %d %d %d Julian day = %d"%(year,month,day,jday)
    hour = slotn/4
    min = (slotn%4)*15
    
    lon = read_msg_lonlat(LONFILE)
    lat = read_msg_lonlat(LATFILE)
    
    # Check for existing coverage file for the area:
    covfilename = "%s/cst/msg_coverage_%s.%s.hdf"%(APPLDIR,in_aid,areaid)
    if not os.path.exists(covfilename):
        cov = _satproj.create_coverage(a,lon,lat,1)
        writeCoverage(cov,covfilename,in_aid,areaid)
    else:
        cov,info = readCoverage(covfilename)
        print info.items()

    #fileprfx="%s"%(RGBDIR_IN)
    fileprfx="%s/%.4d/%.2d/%.2d"%(RGBDIR_IN,year,month,day)
    fname = "%.4d%.2d%.2d%.2d%.2d_C%.4d_%.4d_S%.4d_%.4d"%(year,month,day,hour,min,MSG_AREA_CENTER[0],MSG_AREA_CENTER[1],ROWS,COLS)

    fl = glob.glob("%s/*_%s*"%(fileprfx,fname))
    if len(fl) == 0:
        print "No files for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,min)
    else:
        print "Try extract SEVIRI channel(s) for this time: %.4d%.2d%.2d%.2d%.2d"%(year,month,day,hour,min)

    ch9file = "%s/9_%s.BT"%(fileprfx,fname)
    ch9,ok9=get_ch_projected(ch9file,cov)

    if not ok9:
        print "ERROR: Failed extracting SEVIRI channel 9 data"
        sys.exit(-9)

    s=string.ljust(areaid,12)
    ext=string.replace(s," ","_")
    ctypefile = "%s/%s_%.4d%.2d%.2d_%.2d%.2d.%s.cloudtype.hdf"%(CTYPEDIR_OUT,MetSat,year,month,day,hour,min,areaid)
    print "Output file: ",ctypefile

    make_ctype_prod01(ch9,ctypefile,areaid,gamma=1.6,overlay=1)
    

