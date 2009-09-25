# -*- coding: utf-8 -*-
# **************************************************************************
#
#  COPYRIGHT   : SMHI
#  PRODUCED BY : Swedish Meteorological and Hydrological Institute (SMHI)
#                Folkborgsvaegen 1
#                Norrkoping, Sweden
#
#  PROJECT      : 
#  FILE         : msg_rgb_remap.py
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
# $Id: msg_rgb_remap.py,v 1.16 2009/05/29 22:12:16 Adam.Dybbroe Exp $
#
# $Log: msg_rgb_remap.py,v $
# Revision 1.16  2009/05/29 22:12:16  Adam.Dybbroe
# Added documentation of code.
# Improved function get_ch_projected to be able to also read the hdf5 packed channel data files.
#
# Revision 1.15  2007/11/01 00:10:42  adybbroe
# Solving for overflow in division, when trying to stretch channel data
# with no values (vis channels in darkness).
#
# Revision 1.14  2007/10/31 22:09:08  adybbroe
# Corrected bug: ppss_imagelib -> pps_imagelib
#
# Revision 1.13  2007/10/31 20:00:46  adybbroe
# Updated function makergb_severe_convection similarly to the previous
# update of makergb_visvisir.
#
# Revision 1.12  2007/10/31 19:50:05  adybbroe
# Updated function makergb_visvisir: Now using PPS-library function to
# check the physical range of the solar channels, in order to try to
# avoid noisy RGB's when there is no or very little daylight in the
# image. If the range of the channel is less than a threshold the whole
# channel is set to zero.
#
# Revision 1.11  2007/10/30 14:39:39  adybbroe
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
from msg_communications import *
from msgpp_config import *
from msg_remap_util import *
from misc_utils import ensure_dir

MODULE_ID = "MSG_RGB_REMAP"

COMPRESS_LVL = 6

# --------------------------
class SeviriChObj:
    def __init__(self):
        self.data = None
        self.intercept = 0.0
        self.gain = 1.0

# --------------------------



# ------------------------------------------------------------------
def gamma_corr(g,arr):
    """
    Applies gamma correction to an array, which is assumed to be in
    the range 0 to 256.

    @type g: float scalar
    @param g: The gamma correction factor 
    @type arr: numpy array
    @param arr: Array with values assumed to be in the range 0 to 256.
    @rtype: numpy array
    @return: One-byte (uchar) array after gamma correction
    """
    import numpy

    # Assume array to be between 0 and 255: Put the array between 0 and 1:
    arr = numpy.where(numpy.equal(arr,0),0.0001,arr/255.0)
    
    retv=numpy.exp(1./g*numpy.log(arr))
    maxarr= numpy.maximum.reduce(retv.flat)
    minarr= numpy.minimum.reduce(retv.flat)
    msgwrite_log("INFO","minarr,maxarr = ",minarr,maxarr,moduleid=MODULE_ID)
    if maxarr-minarr > 0.001:
        retv = (255*(retv-minarr)/(maxarr-minarr)).astype('B')
    else:
        msgwrite_log("WARNING","maxarr-minarr <=0.001",maxarr-minarr,moduleid=MODULE_ID)
        retv = numpy.zeros(retv.shape,'B')
    
    return retv

# ------------------------------------------------------------------
# Doing either a gamma correction or a linear contrast stretch:
def get_bw_array(ch,**options):
    """
    Derive an 8-bit stretched (either gamma, linear or histogram equalized)
    image layer from a given array of calibrated sensor channel data.

    @type ch: numpy array
    @param ch: Array with calibrated channel data (Tb or Refl)
    @type options: Options
    @keyword missingdata: Missing data value
    @keyword nodata: Nodata value
    @keyword cutoffs: Tuple with left and right interval cut-offs
    @keyword stretch: String determining the stretch-method
    @keyword gamma: Gamma correction factor
    @keyword inverse: Switch. 1=Invert data, 0=Don't invert data
    @rtype: numpy array
    @return: 8-bit scaled and stretched image data layer
    """
    import numpy
    import pps_imagelib # From PPS/ACPG
    
    if options.has_key("missingdata"):
        missingdata = options["missingdata"]
    else:
        missingdata = 0
    if options.has_key("nodata"):
        nodata = options["nodata"]
    else:
        nodata = 0
    if options.has_key("cutoffs"):
        cutoffs = options["cutoffs"]
    else:
        cutoffs = [0.005,0.005]
    if options.has_key("stretch"):
        stretch=options["stretch"]
    else:
        stretch=None
    gamma=None
    if not stretch:
        if options.has_key("gamma"):
            gamma = options["gamma"]

    if options.has_key("inverse"):
        inverse = options["inverse"]
    else:
        inverse = 0
        
    not_missing_data = numpy.greater(ch,0.0).astype('B')
    #not_missing_data = numpy.logical_and(numpy.not_equal(ch,missingdata),
    #                                       numpy.not_equal(ch,nodata)).astype('b')
    #not_missing_data = numpy.logical_and(numpy.not_equal(ch,NODATA),
    #                                       numpy.not_equal(ch,MISSINGDATA)).astype('b')
    #if inverse:
    #    ch=-ch
    
    if options.has_key("bwrange"):
        ch_range = options["bwrange"]
        min_ch,max_ch = ch_range[0],ch_range[1]
        #if inverse:
        #    tmp = max_ch
        #    max_ch = -min_ch
        #    min_ch = -tmp
    else:
        min_ch,max_ch = numpy.minimum.reduce(numpy.where(not_missing_data.flat,ch.flat,99999)),\
                        numpy.maximum.reduce(numpy.where(not_missing_data.flat,ch.flat,-99999))
        
    msgwrite_log("INFO","min & max: ",min_ch,max_ch,moduleid=MODULE_ID)

    newch = (ch-min_ch) * 255.0/(max_ch-min_ch)
    layer8bit = numpy.where(numpy.greater(newch,255),255,numpy.where(numpy.less(newch,0),0,newch))
    if gamma:
        # Gamma correction:
        msgwrite_log("INFO","Do gamma correction: gamma = %f"%gamma,moduleid=MODULE_ID)
        layer8bit=gamma_corr(gamma,layer8bit)
    elif stretch=="linear":
        # Linear contrast stretch:
        msgwrite_log("INFO","Do a linear contrast stretch: ",moduleid=MODULE_ID)
        #layer = pps_imagelib.stretch_linear(newch,0,0,cutoffs) * not_missing_data
        layer8bit = pps_imagelib.stretch_linear(ch,nodata,missingdata,cutoffs)
    elif stretch == "histogram":
        msgwrite_log("INFO","Do a histogram equalized contrast stretch: ",moduleid=MODULE_ID)
        layer8bit = pps_imagelib.stretch_hist_equalize(newch,0,0)
    elif stretch == "crude-linear":
        msgwrite_log("INFO","Crude linear contrast stretch done!",moduleid=MODULE_ID)
        
    if inverse:
        msgwrite_log("INFO","Invert the data! ",moduleid=MODULE_ID)
        layer8bit = ((255-layer8bit) * not_missing_data).astype('B')
    else:
        layer8bit=(layer8bit * not_missing_data).astype('B')
    
    return layer8bit

# ------------------------------------------------------------------
def make_bw(ch,outprfx,**options):
    """
    Make an 8-bit one layer image and save to output file.

    @type ch: numpy array
    @param ch: Array with calibrated channel data (Tb or Refl)
    @type outprfx: String
    @param outprfx: Output file name prefix (name excluding extention).
    @type options: Options
    @keyword stretch: String determining the stretch-method
    @keyword inverse: Switch. 1=Invert data, 0=Don't invert data
    @keyword bwrange: Tuple with start and end values of input array
    @rtype: numpy array
    @return: 8-bit scaled and stretched image data layer
    """
    import Image

    if options.has_key("stretch"):
        stretch=options["stretch"]
    else:
        stretch=None
    gamma = None
    if not stretch:
        if options.has_key("gamma"):
            gamma=options["gamma"]

    if options.has_key("inverse"):
        inverse=options["inverse"]
    else:
        inverse = 0

    if options.has_key("bwrange"):
        if gamma:
            layer = get_bw_array(ch,gamma=gamma,inverse=inverse,bwrange=options["bwrange"])
        else:
            layer = get_bw_array(ch,inverse=inverse,bwrange=options["bwrange"])
    else:
        if gamma:
            layer = get_bw_array(ch,gamma=gamma,inverse=inverse)
        else:
            layer = get_bw_array(ch,inverse=inverse,stretch=stretch)
            
    imsize = ch.shape[1],ch.shape[0]
    that=Image.fromstring("P", imsize, layer.tostring())    
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    imcopy = that.copy()
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)

    return imcopy


# ------------------------------------------------------------------
# This rgb (airmass) is not yet possible, as we do not have any channel 8 as a by-product
# from the NWCSAF-package! FIXME!
# This is the recipe from EUMETSAT:
# WV6.2 - WV7.3	                -25 till   0 K	gamma 1
# IR9.7 - IR10.8		-40 till  +5 K	gamma 1
# WV6.2		               +243 till 208 K	gamma 1
#
# Adam Dybbroe 2007-10-30
#
def makergb_airmass(ch5,ch6,ch8,ch9,outprfx,**options):
    """
    Make Airmass RGB image composite from SEVIRI channels.
    
    @type ch5: Array of floats
    @param ch5: SEVIRI channel 5 calibrated Tbs on area (remapped)
    @type ch6: Array of floats
    @param ch6: SEVIRI channel 6 calibrated Tbs on area (remapped)
    @type ch8: Array of floats
    @param ch8: SEVIRI channel 8 calibrated Tbs on area (remapped)
    @type ch9: Array of floats
    @param ch9: SEVIRI channel 9 calibrated Tbs on area (remapped)
    @rtype: Image instance
    @return: Result image instance
    """
    import sm_display_util
    import numpy
    import Image
    nodata = 0
    
    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = numpy.greater(ch9,0.0).astype('B')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    red = ch5-ch6
    green = ch8-ch9
    blue = ch5

    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]
    else:
        min_red,max_red = numpy.minimum.reduce(numpy.where(not_missing_data.flat,red.flat,99999)),\
                          numpy.maximum.reduce(numpy.where(not_missing_data.flat,red.flat,-99999))
        min_green,max_green = numpy.minimum.reduce(numpy.where(not_missing_data.flat,green.flat,99999)),\
                              numpy.maximum.reduce(numpy.where(not_missing_data.flat,green.flat,-99999))
        min_blue,max_blue = numpy.minimum.reduce(numpy.where(not_missing_data.flat,blue.flat,99999)),\
                            numpy.maximum.reduce(numpy.where(not_missing_data.flat,blue.flat,-99999))

    msgwrite_log("INFO","Ch5-Ch6 min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch8-Ch9 min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch5 min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

    rgb=[None,None,None]
    newred = (red-min_red) * 255.0/(max_red-min_red)
    rgb[0] = numpy.where(numpy.greater(newred,255),255,numpy.where(numpy.less(newred,0),0,newred))

    newgreen = (green-min_green) * 255.0/(max_green-min_green)
    rgb[1] = numpy.where(numpy.greater(newgreen,255),255,numpy.where(numpy.less(newgreen,0),0,newgreen))

    newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
    rgb[2] = numpy.where(numpy.greater(newblue,255),255,numpy.where(numpy.less(newblue,0),0,newblue))

    # Gamma correction:
    rgb[0]=gamma_corr(gamma_red,rgb[0]) * not_missing_data
    rgb[1]=gamma_corr(gamma_green,rgb[1]) * not_missing_data
    rgb[2]=gamma_corr(gamma_blue,rgb[2]) * not_missing_data
    
    red=Image.fromstring("L", imsize, rgb[0].tostring())
    green=Image.fromstring("L", imsize, rgb[1].tostring())
    blue=Image.fromstring("L", imsize, rgb[2].tostring())
    
    that=Image.merge("RGB",(red,green,blue))
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    imcopy = that.copy()
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)

    return imcopy

# ------------------------------------------------------------------
def makergb_nightfog(ch4r,ch9,ch10,outprfx,**options):
    """
    Make Nightfog RGB image composite from SEVIRI channels.
    
    @type ch4r: Array of floats
    @param ch4r: CO2-corrected SEVIRI channel 4 calibrated Tbs on area (remapped)
    @type ch9: Array of floats
    @param ch9: SEVIRI channel 9 calibrated Tbs on area (remapped)
    @type ch10: Array of floats
    @param ch10: SEVIRI channel 10 calibrated Tbs on area (remapped)
    @rtype: Image instance
    @return: Result image instance
    """
    import sm_display_util
    import numpy
    import Image
    nodata = 0
    
    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = numpy.greater(ch9,0.0).astype('B')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    red = ch10-ch9
    green = ch9-ch4r
    blue = numpy.where(not_missing_data,ch9,nodata)    

    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]
    else:
        min_red,max_red = numpy.minimum.reduce(numpy.where(not_missing_data.flat,red.flat,99999)),\
                          numpy.maximum.reduce(numpy.where(not_missing_data.flat,red.flat,-99999))
        min_green,max_green = numpy.minimum.reduce(numpy.where(not_missing_data.flat,green.flat,99999)),\
                              numpy.maximum.reduce(numpy.where(not_missing_data.flat,green.flat,-99999))
        min_blue,max_blue = numpy.minimum.reduce(numpy.where(not_missing_data.flat,blue.flat,99999)),\
                            numpy.maximum.reduce(numpy.where(not_missing_data.flat,blue.flat,-99999))

    msgwrite_log("INFO","Ch10-Ch9 min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch9-Ch4r min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch9 min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

    rgb=[None,None,None]
    newred = (red-min_red) * 255.0/(max_red-min_red)
    rgb[0] = numpy.where(numpy.greater(newred,255),255,numpy.where(numpy.less(newred,0),0,newred))

    newgreen = (green-min_green) * 255.0/(max_green-min_green)
    rgb[1] = numpy.where(numpy.greater(newgreen,255),255,numpy.where(numpy.less(newgreen,0),0,newgreen))

    newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
    rgb[2] = numpy.where(numpy.greater(newblue,255),255,numpy.where(numpy.less(newblue,0),0,newblue))

    # Gamma correction:
    rgb[0]=gamma_corr(gamma_red,rgb[0]) * not_missing_data
    rgb[1]=gamma_corr(gamma_green,rgb[1]) * not_missing_data
    rgb[2]=gamma_corr(gamma_blue,rgb[2]) * not_missing_data
    
    red=Image.fromstring("L", imsize, rgb[0].tostring())
    green=Image.fromstring("L", imsize, rgb[1].tostring())
    blue=Image.fromstring("L", imsize, rgb[2].tostring())
    
    that=Image.merge("RGB",(red,green,blue))
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    imcopy = that.copy()
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)

    return imcopy

# ------------------------------------------------------------------
def makergb_fog(ch7,ch9,ch10,outprfx,**options):
    """
    Make Fog RGB image composite from SEVIRI channels.
    """
    
    #import sm_display_util
    import numpy,Image
    nodata = 0
    
    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = numpy.greater(ch9,0.0).astype('B')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    red = ch10-ch9
    green = ch9-ch7
    blue = numpy.where(not_missing_data,ch9,nodata)

    min_red,max_red = numpy.minimum.reduce(numpy.where(not_missing_data.flat,red.flat,99999)),\
                      numpy.maximum.reduce(numpy.where(not_missing_data.flat,red.flat,-99999))
    min_green,max_green = numpy.minimum.reduce(numpy.where(not_missing_data.flat,green.flat,99999)),\
                          numpy.maximum.reduce(numpy.where(not_missing_data.flat,green.flat,-99999))
    min_blue,max_blue = numpy.minimum.reduce(numpy.where(not_missing_data.flat,blue.flat,99999)),\
                        numpy.maximum.reduce(numpy.where(not_missing_data.flat,blue.flat,-99999))
    msgwrite_log("INFO","Ch10-Ch9 min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch9-Ch7 min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch9 min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]

    msgwrite_log("INFO","Ch10-Ch9 min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch9-Ch7 min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch9 min & max: ",min_blue,max_blue,moduleid=MODULE_ID)
        
    rgb=[None,None,None]
    newred = (red-min_red) * 255.0/(max_red-min_red)
    rgb[0] = numpy.where(numpy.greater(newred,255),255,numpy.where(numpy.less(newred,0),0,newred))

    newgreen = (green-min_green) * 255.0/(max_green-min_green)
    rgb[1] = numpy.where(numpy.greater(newgreen,255),255,numpy.where(numpy.less(newgreen,0),0,newgreen))

    newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
    rgb[2] = numpy.where(numpy.greater(newblue,255),255,numpy.where(numpy.less(newblue,0),0,newblue))

    # Gamma correction:
    rgb[0]=gamma_corr(gamma_red,rgb[0]) * not_missing_data
    rgb[1]=gamma_corr(gamma_green,rgb[1]) * not_missing_data
    rgb[2]=gamma_corr(gamma_blue,rgb[2]) * not_missing_data
    
    red=Image.fromstring("L", imsize, rgb[0].tostring())
    green=Image.fromstring("L", imsize, rgb[1].tostring())
    blue=Image.fromstring("L", imsize, rgb[2].tostring())
    
    that=Image.merge("RGB",(red,green,blue))
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    imcopy = that.copy()
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    
    return imcopy

# ------------------------------------------------------------------
def makergb_severe_convection(ch1,ch3,ch4,ch5,ch6,ch9,outprfx,**options):
    """
    Make Severe convection RGB image composite from SEVIRI channels.
    """
    import sm_display_util
    import numpy,Image
    nodata = 0
    missingdata = 0
    delta_max = 1.0
    
    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = numpy.greater(ch9,0.0).astype('B')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    red = ch5-ch6
    green = ch4-ch9

    # Use PPS library function to check range in SEVIRI vis/nir channels.
    # The PPS function was made for avhrr data, but works more general.
    # Adam Dybbroe, 2007-10-31
    import pps_imagelib
    seviri_ch = SeviriChObj()
    seviri_ch.data = ch1
    seviri_ch.gain = 1.0
    seviri_ch.intercept = 0.0
    ch1,min_ch1,max_ch1 = pps_imagelib.check_physicalrange(seviri_ch,nodata,missingdata,delta_max)
    seviri_ch.data = ch3
    ch3,min_ch3,max_ch3 = pps_imagelib.check_physicalrange(seviri_ch,nodata,missingdata,delta_max)

    blue = ch3-ch1
    
    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]

        rgb=[None,None,None]
        newred = (red-min_red) * 255.0/(max_red-min_red)
        rgb[0] = numpy.where(numpy.greater(newred,255),255,numpy.where(numpy.less(newred,0),0,newred))

        newgreen = (green-min_green) * 255.0/(max_green-min_green)
        rgb[1] = numpy.where(numpy.greater(newgreen,255),255,numpy.where(numpy.less(newgreen,0),0,newgreen))

        newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
        rgb[2] = numpy.where(numpy.greater(newblue,255),255,numpy.where(numpy.less(newblue,0),0,newblue))

        # Gamma correction:
        rgb[0]=gamma_corr(gamma_red,rgb[0]) * not_missing_data
        rgb[1]=gamma_corr(gamma_green,rgb[1]) * not_missing_data
        rgb[2]=gamma_corr(gamma_blue,rgb[2]) * not_missing_data
    
        red=Image.fromstring("L", imsize, rgb[0].tostring())
        green=Image.fromstring("L", imsize, rgb[1].tostring())
        blue=Image.fromstring("L", imsize, rgb[2].tostring())
    
        that=Image.merge("RGB",(red,green,blue))
        
    else:
        min_red,max_red = numpy.minimum.reduce(red.flat),numpy.maximum.reduce(red.flat)
        min_green,max_green = numpy.minimum.reduce(green.flat),numpy.maximum.reduce(green.flat)
        min_blue,max_blue = numpy.minimum.reduce(blue.flat),numpy.maximum.reduce(blue.flat)
        min_ir = min(min_red,min_green)
        max_ir = max(max_red,max_green)
        min_vis = min_blue
        max_vis = max_blue
    
        # Be sure to have the values inside the range [0,255]:
        red_gain=255.0/(max_red-min_red)
        red_icept=-1.*min_red*red_gain
        msgwrite_log("INFO","Red channel: Gain,Intercept = %f,%f"%(red_gain,red_icept),moduleid=MODULE_ID)
        
        green_gain=255.0/(max_green-min_green)
        green_icept=-1.*min_green*green_gain
        print "Green channel: Gain,Intercept = %f,%f"%(green_gain,green_icept)

        if (max_blue - min_blue) > delta_max:
            blue_gain=255.0/(max_blue-min_blue)
            blue_icept=-1.*min_blue*blue_gain
        else:
            blue_gain=1.0
            blue_icept=0.0
        msgwrite_log("INFO","Blue channel: Gain,Intercept = %f,%f"%(blue_gain,blue_icept),moduleid=MODULE_ID)

        gl=[red_gain,green_gain,blue_gain]
        il=[red_icept,green_icept,blue_icept]
        
        that = sm_display_util.make_rgb([red,green,blue],gl,il,not_missing_data)

    msgwrite_log("INFO","Ch5-Ch6 min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch4-Ch9 min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch3-Ch1 min & max: ",min_blue,max_blue,moduleid=MODULE_ID)
    
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    imcopy = that.copy()
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)

    return imcopy

# ------------------------------------------------------------------
def makergb_visvisir(vis1,vis2,ch9,outprfx,**options):
    """
    Make Overview RGB image composite from SEVIRI channels.
    """
    import sm_display_util
    import numpy,Image
    nodata=0
    missingdata = 0
    delta_max = 1.0
    
    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = numpy.greater(ch9,0.0).astype('B')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    #red = vis1
    #green = vis2
    blue = numpy.where(not_missing_data,-ch9,nodata)

    # Use PPS library function to check range in SEVIRI vis/nir channels.
    # The PPS function was made for avhrr data, but works more general.
    # Adam Dybbroe, 2007-10-31
    import pps_imagelib
    seviri_ch = SeviriChObj()
    seviri_ch.data = vis1
    seviri_ch.gain = 1.0
    seviri_ch.intercept = 0.0
    red,min_red,max_red = pps_imagelib.check_physicalrange(seviri_ch,nodata,missingdata,delta_max)

    seviri_ch.data = vis2
    green,min_green,max_green = pps_imagelib.check_physicalrange(seviri_ch,nodata,missingdata,delta_max)

    #min_red,max_red = numpy.minimum.reduce(numpy.where(not_missing_data.flat,red.flat,99999)),\
    #                  numpy.maximum.reduce(numpy.where(not_missing_data.flat,red.flat,-99999))
    #min_green,max_green = numpy.minimum.reduce(numpy.where(not_missing_data.flat,green.flat,99999)),\
    #                      numpy.maximum.reduce(numpy.where(not_missing_data.flat,green.flat,-99999))
    min_blue,max_blue = numpy.minimum.reduce(numpy.where(not_missing_data.flat,blue.flat,99999)),\
                        numpy.maximum.reduce(numpy.where(not_missing_data.flat,blue.flat,-99999))

    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]

    msgwrite_log("INFO","R: min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","G: min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","B: min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

    rgb=[None,None,None]
    if (max_red - min_red) > delta_max:
        newred = (red-min_red) * 255.0/(max_red-min_red)
        rgb[0] = numpy.where(numpy.greater(newred,255),255,numpy.where(numpy.less(newred,0),0,newred))
    else:
        rgb[0] = red

    if (max_green - min_green) > delta_max:
        newgreen = (green-min_green) * 255.0/(max_green-min_green)
        rgb[1] = numpy.where(numpy.greater(newgreen,255),255,numpy.where(numpy.less(newgreen,0),0,newgreen))
    else:
        rgb[1] = green

    newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
    rgb[2] = numpy.where(numpy.greater(newblue,255),255,numpy.where(numpy.less(newblue,0),0,newblue))

    # Gamma correction:
    rgb[0]=gamma_corr(gamma_red,rgb[0]) * not_missing_data
    rgb[1]=gamma_corr(gamma_green,rgb[1]) * not_missing_data
    rgb[2]=gamma_corr(gamma_blue,rgb[2]) * not_missing_data
    
    red=Image.fromstring("L", imsize, rgb[0].tostring())
    green=Image.fromstring("L", imsize, rgb[1].tostring())
    blue=Image.fromstring("L", imsize, rgb[2].tostring())
    
    that=Image.merge("RGB",(red,green,blue))
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    imcopy = that.copy()
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    
    return imcopy

# ------------------------------------------------------------------
def makergb_hrovw(vis1,vis2,ch9,ch12,outprfx,**options):
    """
    Make HR Overview RGB image composite from SEVIRI channels.
    """
    import sm_display_util
    import numpy,Image
    nodata=0
    missingdata = 0
    delta_max = 1.0
    
    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = numpy.greater(ch9,0.0).astype('B')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    #red = vis1
    #green = vis2
    blue = numpy.where(not_missing_data,-ch9,nodata)

    # Use PPS library function to check range in SEVIRI vis/nir channels.
    # The PPS function was made for avhrr data, but works more general.
    # Adam Dybbroe, 2007-10-31
    import pps_imagelib
    seviri_ch = SeviriChObj()
    seviri_ch.data = vis1
    seviri_ch.gain = 1.0
    seviri_ch.intercept = 0.0
    red,min_red,max_red = pps_imagelib.check_physicalrange(seviri_ch,nodata,missingdata,delta_max)

    seviri_ch.data = vis2
    green,min_green,max_green = pps_imagelib.check_physicalrange(seviri_ch,nodata,missingdata,delta_max)

    #min_red,max_red = numpy.minimum.reduce(numpy.where(not_missing_data.flat,red.flat,99999)),\
    #                  numpy.maximum.reduce(numpy.where(not_missing_data.flat,red.flat,-99999))
    #min_green,max_green = numpy.minimum.reduce(numpy.where(not_missing_data.flat,green.flat,99999)),\
    #                      numpy.maximum.reduce(numpy.where(not_missing_data.flat,green.flat,-99999))
    min_blue,max_blue = numpy.minimum.reduce(numpy.where(not_missing_data.flat,blue.flat,99999)),\
                        numpy.maximum.reduce(numpy.where(not_missing_data.flat,blue.flat,-99999))

    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]

    msgwrite_log("INFO","R: min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","G: min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","B: min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

    rgb=[None,None,None]
    if (max_red - min_red) > delta_max:
        newred = (red-min_red) * 255.0/(max_red-min_red)
        rgb[0] = numpy.where(numpy.greater(newred,255),255,numpy.where(numpy.less(newred,0),0,newred))
    else:
        rgb[0] = red

    if (max_green - min_green) > delta_max:
        newgreen = (green-min_green) * 255.0/(max_green-min_green)
        rgb[1] = numpy.where(numpy.greater(newgreen,255),255,numpy.where(numpy.less(newgreen,0),0,newgreen))
    else:
        rgb[1] = green

    newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
    rgb[2] = numpy.where(numpy.greater(newblue,255),255,numpy.where(numpy.less(newblue,0),0,newblue))

    # Gamma correction:
    rgb[0]=numpy.array(numpy.round(gamma_corr(gamma_red,rgb[0]) * not_missing_data),numpy.uint8)
    rgb[2]=numpy.array(numpy.round(gamma_corr(gamma_blue,rgb[2]) * not_missing_data),numpy.uint8)
    rgb[1]=numpy.array(numpy.round(gamma_corr(gamma_green,rgb[1]) * not_missing_data),numpy.uint8)

    Y =  16.0 + 1.0/256.0 * (65.738 * rgb[0] + 129.057 * rgb[1] + 25.064 * rgb[2])

    vmin = numpy.amin(Y[numpy.where(not_missing_data)])
    vmax = numpy.amax(Y[numpy.where(not_missing_data)])

    red=Image.fromarray(rgb[0], "L")
    green=Image.fromarray(rgb[1], "L")
    blue=Image.fromarray(rgb[2], "L")
    
    that=Image.merge("RGB",(red,green,blue))

    Y = ch12

    Ymax = numpy.amax(Y[Y>0])
    Ymin = numpy.amin(Y[Y>0])

    normY = (Y-Ymin)*255.0/(Ymax-Ymin)
    gammaY = gamma_corr(1.8,normY[Y>0])
    normY[Y>0] = gammaY
    normY[Y<=0] = nodata

    v = that.convert('YCbCr').split()

    coeff = (vmax - vmin) * 1.0

    Y = numpy.array(numpy.round(normY),numpy.uint8)
    hrv = Image.fromarray(Y, "L")

    that = Image.merge('YCbCr',(hrv,v[1].resize(hrv.size),v[2].resize(hrv.size))).convert('RGB')
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)

    imcopy = that.copy()
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    
    return imcopy

# ------------------------------------------------------------------
def makergb_redsnow(ch1,ch3,ch9,outprfx,**options):
    """
    Make Red snow RGB image composite from SEVIRI channels.
    """
    import sm_display_util
    import numpy

    not_missing_data = numpy.greater(ch9,0.0).astype('B')
    size = not_missing_data.shape[1],not_missing_data.shape[0]

    ir_gain=1.0
    ir_intercept=0.0
    vis_gain=1.0
    vis_intercept=0.0
    irgain = -2.0 * ir_gain
    iricept = 2.0 * (330.66 - ir_intercept)
    visgain = 2.55 * vis_gain
    visicept = 2.55 * vis_intercept
    gl=[visgain,visgain,irgain]
    il=[visicept,visicept,iricept]
    that = sm_display_util.make_rgb([ch1,ch3,ch9],gl,il,not_missing_data)
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    imcopy = that.copy()
    that.thumbnail((size[0]/2,size[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)

    return imcopy

# ------------------------------------------------------------------
def makergb_cloudtop(ch4,ch9,ch10,outprfx,**options):
    """
    Make Cloudtop RGB image composite from SEVIRI channels.
    """
    import sm_display_util
    import numpy,Image
    nodata=0

    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = numpy.greater(ch9,0.0).astype('B')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    red = numpy.where(not_missing_data,-ch4,nodata)
    green = numpy.where(not_missing_data,-ch9,nodata)
    blue = numpy.where(not_missing_data,-ch10,nodata)

    min_red,max_red = numpy.minimum.reduce(numpy.where(not_missing_data.flat,red.flat,99999)),\
                      numpy.maximum.reduce(numpy.where(not_missing_data.flat,red.flat,-99999))
    min_green,max_green = numpy.minimum.reduce(numpy.where(not_missing_data.flat,green.flat,99999)),\
                          numpy.maximum.reduce(numpy.where(not_missing_data.flat,green.flat,-99999))
    min_blue,max_blue = numpy.minimum.reduce(numpy.where(not_missing_data.flat,blue.flat,99999)),\
                        numpy.maximum.reduce(numpy.where(not_missing_data.flat,blue.flat,-99999))

    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]

    msgwrite_log("INFO","R: min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","G: min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","B: min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

    rgb=[None,None,None]
    newred = (red-min_red) * 255.0/(max_red-min_red)
    rgb[0] = numpy.where(numpy.greater(newred,255),255,numpy.where(numpy.less(newred,0),0,newred))

    newgreen = (green-min_green) * 255.0/(max_green-min_green)
    rgb[1] = numpy.where(numpy.greater(newgreen,255),255,numpy.where(numpy.less(newgreen,0),0,newgreen))

    newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
    rgb[2] = numpy.where(numpy.greater(newblue,255),255,numpy.where(numpy.less(newblue,0),0,newblue))

    # Gamma correction:
    rgb[0]=gamma_corr(gamma_red,rgb[0]) * not_missing_data
    rgb[1]=gamma_corr(gamma_green,rgb[1]) * not_missing_data
    rgb[2]=gamma_corr(gamma_blue,rgb[2]) * not_missing_data
    
    red=Image.fromstring("L", imsize, rgb[0].tostring())
    green=Image.fromstring("L", imsize, rgb[1].tostring())
    blue=Image.fromstring("L", imsize, rgb[2].tostring())
    
    that=Image.merge("RGB",(red,green,blue))
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    imcopy = that.copy()
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)

    return imcopy

# ------------------------------------------------------------------
# Store the sun or satellite zenith and azimuth angles in hdf5
def sunsat_angles2hdf(filename,zenith,azimuth,angletype):
    """
    Store the sun or satellite zenith and azimuth angles in hdf5
    """
    import _pyhl

    a=_pyhl.nodelist()

    shape=[zenith.shape[0],zenith.shape[1]]
    
    b=_pyhl.node(_pyhl.GROUP_ID,"/info")
    a.addNode(b)
    if angletype == "sun":
        b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/description")
        b.setScalarValue(-1,"MSG SEVIRI sun zenith and azimuth angles","string",-1)
        a.addNode(b)
    elif angletype == "sat":
        b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/description")
        b.setScalarValue(-1,"MSG SEVIRI satellite zenith and azimuth angles","string",-1)
        a.addNode(b)        
    else:
        print "Error!"
        return -1
    
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/num_of_rows")
    b.setScalarValue(-1,shape[0],"int",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/num_of_columns")
    b.setScalarValue(-1,shape[1],"int",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/nodata")
    b.setScalarValue(-1,-99999.0,"float",-1)
    a.addNode(b)
    
    if angletype == "sun":
        b=_pyhl.node(_pyhl.DATASET_ID,"/sunzenith")
    else:
        b=_pyhl.node(_pyhl.DATASET_ID,"/satzenith")
    b.setArrayValue(1,shape,zenith,"float",-1)
    a.addNode(b)

    if angletype == "sun":
        b=_pyhl.node(_pyhl.DATASET_ID,"/sunazimuth")
    else:
        b=_pyhl.node(_pyhl.DATASET_ID,"/satazimuth")
        
    b.setArrayValue(1,shape,azimuth,"float",-1)
    a.addNode(b)

    a.write(filename,COMPRESS_LVL)
    return 0

# ------------------------------------------------------------------
# Store the MSG SEVIRI geolocation in hdf5
def lonlat2hdf(filename,lon,lat):
    """
    Store the MSG SEVIRI geolocation in hdf5
    """
    import _pyhl

    a=_pyhl.nodelist()

    shape=[lon.shape[0],lon.shape[1]]
    
    b=_pyhl.node(_pyhl.GROUP_ID,"/info")
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/description")
    b.setScalarValue(-1,"MSG SEVIRI geolocation - longitudes and latitudes","string",-1)
    a.addNode(b)

    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/num_of_rows")
    b.setScalarValue(-1,shape[0],"int",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/num_of_columns")
    b.setScalarValue(-1,shape[1],"int",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/nodata")
    b.setScalarValue(-1,-99999.0,"float",-1)
    a.addNode(b)
    
    b=_pyhl.node(_pyhl.DATASET_ID,"/longitude")
    b.setArrayValue(1,shape,lon,"float",-1)
    a.addNode(b)

    b=_pyhl.node(_pyhl.DATASET_ID,"/latitude")
    b.setArrayValue(1,shape,lat,"float",-1)
    a.addNode(b)

    a.write(filename,COMPRESS_LVL)

    return 0

# ------------------------------------------------------------------
# Store the raw (unprojected BT&RAD or REF) SEVIRI channel data to hdf5
def raw_channel2hdf(filename,ch_tuple,channel_number,type="BT"):
    """
    Store the raw (unprojected BT&RAD or REF) SEVIRI channel data to hdf5
    """
    import _pyhl

    if len(ch_tuple)==1:
        ch = ch_tuple[0]
    else:
        ch,ch_radiance=ch_tuple
        
    a=_pyhl.nodelist()

    shape=[ch.shape[0],ch.shape[1]]
    
    b=_pyhl.node(_pyhl.GROUP_ID,"/info")
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/description")
    if type == "BT":
        b.setScalarValue(-1,"MSG SEVIRI channel number %d - Radiances (w/(m**2*sr)) Brightness temperatures (K)"%channel_number,"string",-1)
    elif type == "REF":
        b.setScalarValue(-1,"MSG SEVIRI channel number %d - Reflectivities (%%)"%channel_number,"string",-1)
    else:
        print "Failed: Data are neither reflectances (REF) nor brightness temperatures (BT)"
        return -1    
    a.addNode(b)

    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/num_of_rows")
    b.setScalarValue(-1,shape[0],"int",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/num_of_columns")
    b.setScalarValue(-1,shape[1],"int",-1)
    a.addNode(b)
    b=_pyhl.node(_pyhl.ATTRIBUTE_ID,"/info/nodata")
    b.setScalarValue(-1,-99999.0,"float",-1)
    a.addNode(b)
    
    if type == "BT":
        c=_pyhl.node(_pyhl.DATASET_ID,"/rad")
        c.setArrayValue(1,shape,ch_radiance,"float",-1)
        a.addNode(c)
        b=_pyhl.node(_pyhl.DATASET_ID,"/bt")
    elif type == "REF":
        b=_pyhl.node(_pyhl.DATASET_ID,"/ref")

    b.setArrayValue(1,shape,ch,"float",-1)
    a.addNode(b)

    a.write(filename,COMPRESS_LVL)
    
    return 0

    
# ------------------------------------------------------------------
def get_ch_projected(ch_file,cov):
    """
    Read calibrated SEVIRI channel data from file and project
    the data to a cartographic map area, given by the coverage field.

    @type ch_file: String
    @param ch_file: Filename with SEVIRI channel data (The binary raw dump from the NWCSAF/MSG package)
    @rtype: Tuple (array,int)
    @return: Tuple with an array of channel data and a 0/1 okay switch (1=okay,0=failure)
    """
    import msg_remap_util
    import _satproj
    import os
    missingdata=-99998
    
    if os.path.exists(ch_file):
        # The following has a rather crude way of letting this
        # function being able to read both the raw binary channels
        # dumps (from the NWCSAF-package) and those already converted
        # to hdf5.  There is a lack of proper error handling!
        #
        # Adam Dybbroe, 2008-12-08
        try:
            ch_raw = msg_remap_util.read_msg_lonlat(ch_file)
        except:
            print "Probably the file is an hdf5 file. Try read Tb's or Reflectivities"
            channelObj = read_raw_channels_hdf5(ch_file)
            if channelObj.ref:
                ch_raw = channelObj.ref
            else:
                ch_raw = channelObj.bt
    else:
        print "File %s not available!"%(ch_file)
        return None,0
    
    ch_proj = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,ch_raw,missingdata)

    return ch_proj,1

def project_array(coverage, a):
    import _satproj

    if (a is None):
        return None

    return _satproj.project(coverage.coverage,
                            coverage.rowidx,
                            coverage.colidx,
                            a.filled(),
                            int(a.fill_value))

# ------------------------------------------------------------------
# CO2 correction of the MSG 3.9 um channel:
#
# T4_CO2corr = (BT(IR3.9)^4 + Rcorr)^0.25
# Rcorr = BT(IR10.8)^4 - (BT(IR10.8)-dt_CO2)^4
# dt_CO2 = (BT(IR10.8)-BT(IR13.4))/4.0
#
def co2corr_bt39(bt039,bt108,bt134):
    """
    CO2 correction of the MSG 3.9 um channel:
    
    T4_CO2corr = (BT(IR3.9)^4 + Rcorr)^0.25
    Rcorr = BT(IR10.8)^4 - (BT(IR10.8)-dt_CO2)^4
    dt_CO2 = (BT(IR10.8)-BT(IR13.4))/4.0

    @type bt039: Array
    @param bt039: Channel 4 (3.9um) brightness temperatures

    """
    import numpy
    epsilon = 0.001
    
    not_missing_data = numpy.greater(bt108,0.00).astype('B')
    dt_co2 = numpy.where(not_missing_data,(bt108-bt134)/4.0,0)
    a = numpy.where(not_missing_data,bt108*bt108*bt108*bt108,0)
    b = numpy.where(not_missing_data,(bt108-dt_co2)*(bt108-dt_co2)*(bt108-dt_co2)*(bt108-dt_co2),0)
    print numpy.minimum.reduce(a.flat),numpy.maximum.reduce(a.flat)
    print numpy.minimum.reduce(b.flat),numpy.maximum.reduce(b.flat)
    Rcorr = a - b

    a = numpy.where(not_missing_data,bt039*bt039*bt039*bt039,0)
    x = numpy.where(numpy.logical_and(not_missing_data,numpy.greater(a+Rcorr,0.0)),(a + Rcorr),epsilon)
    print "x: ",numpy.minimum.reduce(x.flat),numpy.maximum.reduce(x.flat)
    #print "a: ",numpy.minimum.reduce(a.flat),numpy.maximum.reduce(a.flat)
    #print "Rcorr: ",numpy.minimum.reduce(Rcorr.flat),numpy.maximum.reduce(Rcorr.flat)
    
    retv = numpy.where(not_missing_data,numpy.exp(0.25*numpy.log(x)),0)
    
    return retv

# ------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 6:
        print "Usage: %s <area id> <year> <month> <day> <hhmm>"%(sys.argv[0])
        sys.exit(-9)
    else:
        import string
        areaid = sys.argv[1]
        year = string.atoi(sys.argv[2])
        mon = string.atoi(sys.argv[3])
        day = string.atoi(sys.argv[4])
        hhmm = string.atoi(sys.argv[5])

    import _satproj
    import area
    import msg_ctype_remap
    
    lon = msg_ctype_remap.read_msg_lonlat(LONFILE)
    lat = msg_ctype_remap.read_msg_lonlat(LATFILE)

    a=area.area(areaid)
    cov = _satproj.create_coverage(a,lon,lat,1)

    fileprfx="%s/%.4d/%.2d/%.2d"%(RGBDIR_IN,year,mon,day)
    fname = "%.4d%.2d%.2d%.2d%.2d_C%.4d_%.4d_S%.4d_%.4d"%(year,mon,day,hhmm,MSG_AREA_CENTER[0],MSG_AREA_CENTER[1],ROWS,COLS)

    ch1file = "%s/1_%s.REF"%(fileprfx,fname)
    ch3file = "%s/3_%s.REF"%(fileprfx,fname)
    ch4file = "%s/4_%s.BT"%(fileprfx,fname)    
    ch5file = "%s/5_%s.BT"%(fileprfx,fname)
    ch6file = "%s/6_%s.BT"%(fileprfx,fname)
    ch7file = "%s/7_%s.BT"%(fileprfx,fname)
    ch9file = "%s/9_%s.BT"%(fileprfx,fname)
    ch10file = "%s/10_%s.BT"%(fileprfx,fname)
    ch11file = "%s/11_%s.BT"%(fileprfx,fname)

    ch1,ok1=get_ch_projected(ch1file,cov)
    ch3,ok3=get_ch_projected(ch3file,cov)
    ch4,ok4=get_ch_projected(ch4file,cov)    
    ch5,ok5=get_ch_projected(ch5file,cov)
    ch6,ok6=get_ch_projected(ch6file,cov)
    ch7,ok7=get_ch_projected(ch7file,cov)
    ch9,ok9=get_ch_projected(ch9file,cov)
    ch10,ok10=get_ch_projected(ch10file,cov)
    ch11,ok11=get_ch_projected(ch11file,cov)

    ok4r=0
    if ok4 and ok9 and ok11:
        ch4r = co2corr_bt39(ch4,ch9,ch11)
        ok4r = 1
        
    # Daytime convection:
    if ok1 and ok3 and ok4 and ok5 and ok6 and ok9:
        outname = "%s/met8_%.4d%.2d%.2d%.4d_%s_rgb_severe_convection"%(RGBDIR_OUT,year,mon,day,hhmm,areaid)    
        makergb_severe_convection(ch1,ch3,ch4,ch5,ch6,ch9,outname)

    # Fog and low clouds
    if ok4r and ok9 and ok10:
        outname = "%s/met8_%.4d%.2d%.2d%.4d_%s_rgb_nightfog"%(RGBDIR_OUT,year,mon,day,hhmm,areaid)
        makergb_nightfog(ch4r,ch9,ch10,outname)
    if ok7 and ok9 and ok10:
        outname = "%s/met8_%.4d%.2d%.2d%.4d_%s_rgb_fog"%(RGBDIR_OUT,year,mon,day,hhmm,areaid)
        makergb_fog(ch7,ch9,ch10,outname)

    # "red snow": Low clouds and snow daytime
    if ok1 and ok3 and ok9:
        outname = "%s/met8_%.4d%.2d%.2d%.4d_%s_rgb_redsnow_016"%(RGBDIR_OUT,year,mon,day,hhmm,areaid)
        makergb_redsnow(ch1,ch3,ch9,outname)

    # "cloudtop": Low clouds, thin cirrus, nighttime
    if ok4 and ok9 and ok10:
        outname = "%s/met8_%.4d%.2d%.2d%.4d_%s_rgb_cloudtop"%(RGBDIR_OUT,year,mon,day,hhmm,areaid)
        makergb_cloudtop(ch4,ch9,ch10,outname)
    if ok4r and ok9 and ok10:
        outname = "%s/met8_%.4d%.2d%.2d%.4d_%s_rgb_cloudtop_co2corr"%(RGBDIR_OUT,year,mon,day,hhmm,areaid)
        makergb_cloudtop(ch4r,ch9,ch10,outname)
