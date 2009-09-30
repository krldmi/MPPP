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
import numpy

from msg_communications import *
from msgpp_config import *
from msg_remap_util import *
import misc_utils
from misc_utils import ensure_dir
import msg_image_manipulation
from msg_image_manipulation import gamma_corr

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
    
    if options.has_key("bwrange"):
        ch_range = options["bwrange"]
        min_ch,max_ch = ch_range[0],ch_range[1]
    else:
        min_ch,max_ch = ch.min(), ch.max()
        
    msgwrite_log("INFO","min & max: ",min_ch,max_ch,moduleid=MODULE_ID)

    newch = (ch-min_ch) * 255.0/(max_ch-min_ch)
    layer8bit = numpy.where(newch < 0, 0, newch)
    layer8bit = numpy.where(newch > 255, 255, newch)

    if gamma:
        # Gamma correction:
        msgwrite_log("INFO","Do gamma correction: gamma = %f"%gamma,moduleid=MODULE_ID)
        layer8bit=gamma_corr(gamma,layer8bit)
    elif stretch=="linear":
        # Linear contrast stretch:
        msgwrite_log("INFO","Do a linear contrast stretch: ",moduleid=MODULE_ID)
        layer8bit = msg_image_manipulation.stretch_linear(ch,cutoffs)
    elif stretch == "histogram":
        msgwrite_log("INFO","Do a histogram equalized contrast stretch: ",moduleid=MODULE_ID)
        layer8bit = msg_image_manipulation.stretch_hist_equalize(newch)
    elif stretch == "crude-linear":
        msgwrite_log("INFO","Crude linear contrast stretch done!",moduleid=MODULE_ID)
        
    if inverse:
        msgwrite_log("INFO","Invert the data! ",moduleid=MODULE_ID)
        layer8bit = (255-layer8bit).astype(numpy.uint8)
    else:
        layer8bit=layer8bit.astype(numpy.uint8)
    
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
    nodata = 0
#     if options.has_key("stretch"):
#         stretch=options["stretch"]
#     else:
#         stretch=None
#     gamma = None
#     if not stretch:
#         if options.has_key("gamma"):
#             gamma=options["gamma"]

#     if options.has_key("inverse"):
#         inverse=options["inverse"]
#     else:
#         inverse = 0

#     if options.has_key("bwrange"):
#         if gamma:
#             layer = get_bw_array(ch,gamma=gamma,inverse=inverse,bwrange=options["bwrange"])
#         else:
#             layer = get_bw_array(ch,inverse=inverse,bwrange=options["bwrange"])
#     else:
#         if gamma:
#             layer = get_bw_array(ch,gamma=gamma,inverse=inverse)
#         else:
#             layer = get_bw_array(ch,inverse=inverse,stretch=stretch)

    layer = get_bw_array(ch,**options)
            
    imsize = ch.shape[1],ch.shape[0]
    that=Image.fromarray(layer.filled(nodata).astype(numpy.uint8))    
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    imcopy = that.copy()
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)

    return imcopy



def makergb_template(rgb,outprfx,**options):

    import numpy
    import Image

    nodata = 0

    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    red = rgb[0]
    green = rgb[1]
    blue = rgb[2]

    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]
    else:
        min_red,max_red = misc_utils.extrema(red)
        min_green,max_green = misc_utils.extrema(green)
        min_blue,max_blue = misc_utils.extrema(blue)


    rgb=[None,None,None]

    if (options.has_key("stretch") and options["stretch"] == "linear"):
        rgb[0] = msg_image_manipulation.stretch_linear(red)
        rgb[1] = msg_image_manipulation.stretch_linear(green)
        rgb[2] = msg_image_manipulation.stretch_linear(blue)
    elif (options.has_key("stretch") and options["stretch"] == "histogram"):
        rgb[0] = msg_image_manipulation.stretch_hist_equalize(red)
        rgb[1] = msg_image_manipulation.stretch_hist_equalize(green)
        rgb[2] = msg_image_manipulation.stretch_hist_equalize(blue)
    else:
        rgb[0] = msg_image_manipulation.crude_stretch(red,255,min_red,max_red)
        rgb[1] = msg_image_manipulation.crude_stretch(green,255,min_green,max_green)
        rgb[2] = msg_image_manipulation.crude_stretch(blue,255,min_blue,max_blue)

                
                                

    # Gamma correction:
#     rgb[0]=gamma_corr(gamma_red,rgb[0])
#     rgb[1]=gamma_corr(gamma_green,rgb[1])
#     rgb[2]=gamma_corr(gamma_blue,rgb[2])
    
#     red=Image.fromarray(rgb[0].filled(nodata))
#     green=Image.fromarray(rgb[1].filled(nodata))
#     blue=Image.fromarray(rgb[2].filled(nodata))

    rgb[0]=gamma_corr(gamma_red,rgb[0].filled(nodata))
    rgb[1]=gamma_corr(gamma_green,rgb[1].filled(nodata))
    rgb[2]=gamma_corr(gamma_blue,rgb[2].filled(nodata))
    
    red=Image.fromarray(rgb[0])
    green=Image.fromarray(rgb[1])
    blue=Image.fromarray(rgb[2])

    
    imsize = rgb[0].shape[1],rgb[0].shape[0]

    that=Image.merge("RGB",(red,green,blue))
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    imcopy = that.copy()
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)

    return imcopy,min_red,max_red,min_green,max_green,min_blue,max_blue




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

    red = ch5-ch6
    green = ch8-ch9
    blue = ch5

    imcopy,min_red,max_red,min_green,max_green,min_blue,max_blue = makergb_template((red,green,blue),outprfx,**options)

    msgwrite_log("INFO","Ch5-Ch6 min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch8-Ch9 min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch5 min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

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

    red = ch10-ch9
    green = ch9-ch4r
    blue = ch9

    imcopy,min_red,max_red,min_green,max_green,min_blue,max_blue = makergb_template((red,green,blue),outprfx,**options)

    msgwrite_log("INFO","Ch10-Ch9 min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch9-Ch4r min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch9 min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

    return imcopy

# ------------------------------------------------------------------
def makergb_fog(ch7,ch9,ch10,outprfx,**options):
    """
    Make Fog RGB image composite from SEVIRI channels.
    """
    
    red = ch10-ch9
    green = ch9-ch7
    blue = ch9

    imcopy,min_red,max_red,min_green,max_green,min_blue,max_blue = makergb_template((red,green,blue),outprfx,**options)

    msgwrite_log("INFO","Ch10-Ch9 min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch9-Ch7 min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch9 min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

    return imcopy

# ------------------------------------------------------------------
def makergb_severe_convection(ch1,ch3,ch4,ch5,ch6,ch9,outprfx,**options):
    """
    Make Severe convection RGB image composite from SEVIRI channels.
    """
    red = ch5-ch6
    green = ch4-ch9
    blue = ch3-ch1
    
    imcopy,min_red,max_red,min_green,max_green,min_blue,max_blue = makergb_template((red,green,blue),outprfx,**options)

    msgwrite_log("INFO","Ch5-Ch6 min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch4-Ch9 min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch3-Ch1 min & max: ",min_blue,max_blue,moduleid=MODULE_ID)
    
    return imcopy

# ------------------------------------------------------------------
def makergb_visvisir(vis1,vis2,ch9,outprfx,**options):
    """
    Make Overview RGB image composite from SEVIRI channels.
    """
    red = vis1
    green = vis2
    blue = -ch9

    imcopy,min_red,max_red,min_green,max_green,min_blue,max_blue = makergb_template((red,green,blue),outprfx,**options)

    msgwrite_log("INFO","R: min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","G: min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","B: min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

    return imcopy

# ------------------------------------------------------------------
def makergb_hrovw(vis1,vis2,ch9,ch12,outprfx,**options):
    """Make HR Overview RGB image composite from SEVIRI channels.
    """
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

    red = vis1
    green = vis2
    blue = -ch9


    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]
    else:
        min_red,max_red = misc_utils.extrema(red)
        min_green,max_green = misc_utils.extrema(green)
        min_blue,max_blue = misc_utils.extrema(blue)

    msgwrite_log("INFO","R: min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","G: min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","B: min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

    rgb=[None,None,None]

    rgb[0] = msg_image_manipulation.crude_stretch(red,255,min_red,max_red)
    rgb[1] = msg_image_manipulation.crude_stretch(green,255,min_green,max_green)
    rgb[2] = msg_image_manipulation.crude_stretch(blue,255,min_blue,max_blue)


    # Gamma correction:
    rgb[0]=gamma_corr(gamma_red,rgb[0].filled(nodata))
    rgb[1]=gamma_corr(gamma_green,rgb[1].filled(nodata))
    rgb[2]=gamma_corr(gamma_blue,rgb[2].filled(nodata))
    
    red=Image.fromarray(rgb[0])
    green=Image.fromarray(rgb[1])
    blue=Image.fromarray(rgb[2])
    

    that=Image.merge("RGB",(red,green,blue))

    Y = ch12

    Ymax = Y.max()
    Ymin = Y.min()

    normY = msg_image_manipulation.crude_stretch(Y,255,Ymin,Ymax)
    gammaY = gamma_corr(1.8,normY)

    v = that.convert('YCbCr').split()

    Y = numpy.array(numpy.round(gammaY),numpy.uint8)
    hrv = Image.fromarray(Y, "L")

    that = Image.merge('YCbCr',(hrv,v[1].resize(hrv.size),v[2].resize(hrv.size))).convert('RGB')
    ensure_dir(outprfx+".%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+".%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)

    imcopy = that.copy()
    imsize = imcopy.size
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    ensure_dir(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT)
    that.save(outprfx+"_thumbnail.%s"%RGB_IMAGE_FORMAT,format=RGB_IMAGE_FORMAT,quality=RGB_IMAGE_QUALITY)
    
    return imcopy

# ------------------------------------------------------------------
def makergb_redsnow(ch1,ch3,ch9,outprfx,**options):
    """
    Make Red snow RGB image composite from SEVIRI channels.
    """

    red = ch1
    green = ch3
    blue = -ch9 + 330.66

    options["stretch"] = "linear"
    imcopy,min_red,max_red,min_green,max_green,min_blue,max_blue = makergb_template((red,green,blue),outprfx,**options)

    msgwrite_log("INFO","Ch1 min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","Ch3 min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","-Ch9 + 330.66 min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

    return imcopy

# ------------------------------------------------------------------
def makergb_cloudtop(ch4,ch9,ch10,outprfx,**options):
    """
    Make Cloudtop RGB image composite from SEVIRI channels.
    """

    red = -ch4
    green = -ch9
    blue = -ch10

    imcopy,min_red,max_red,min_green,max_green,min_blue,max_blue = makergb_template((red,green,blue),outprfx,**options)

    msgwrite_log("INFO","-ch4: min & max: ",min_red,max_red,moduleid=MODULE_ID)
    msgwrite_log("INFO","-ch9: min & max: ",min_green,max_green,moduleid=MODULE_ID)
    msgwrite_log("INFO","-ch10: min & max: ",min_blue,max_blue,moduleid=MODULE_ID)

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
    
    #not_missing_data = numpy.greater(bt108,0.00).astype('B')
    #dt_co2 = numpy.where(not_missing_data,(bt108-bt134)/4.0,0)
    #a = numpy.where(not_missing_data,bt108*bt108*bt108*bt108,0)
    #b = numpy.where(not_missing_data,(bt108-dt_co2)*(bt108-dt_co2)*(bt108-dt_co2)*(bt108-dt_co2),0)
    dt_co2 = (bt108-bt134)/4.0
    a = bt108*bt108*bt108*bt108
    b = (bt108-dt_co2)*(bt108-dt_co2)*(bt108-dt_co2)*(bt108-dt_co2)

    #print numpy.minimum.reduce(a.flat),numpy.maximum.reduce(a.flat)
    #print numpy.minimum.reduce(b.flat),numpy.maximum.reduce(b.flat)
    Rcorr = a - b

    a = bt039*bt039*bt039*bt039
    x = numpy.where(a+Rcorr > 0.0,(a + Rcorr), 0)
    print "x: ",x.min(),x.max()
    #print "a: ",numpy.minimum.reduce(a.flat),numpy.maximum.reduce(a.flat)
    #print "Rcorr: ",numpy.minimum.reduce(Rcorr.flat),numpy.maximum.reduce(Rcorr.flat)
    
    retv = x ** 0.25
    
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
