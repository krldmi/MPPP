#
#
from msgpp_config import *
from msg_remap_util import *

nodata=0.
missingdata=0.

# ------------------------------------------------------------------
def gamma_corr(g,arr):
    import Numeric

    # Assume array to be between 0 and 255: Put the array between 0 and 1:
    arr = Numeric.where(Numeric.equal(arr,0),0.0001,arr/255.0)
    
    retv=Numeric.exp(1./g*Numeric.log(arr))
    maxarr= Numeric.maximum.reduce(retv.flat)
    minarr= Numeric.minimum.reduce(retv.flat)
    if maxarr-minarr > 0.001:
        retv = 255*(retv-minarr)/(maxarr-minarr)
    else:
        print "WARNING!!! maxarr-minarr <=0.001",maxarr-minarr
    print "minarr,maxarr = ",minarr,maxarr
    
    return retv.astype('b')

# ------------------------------------------------------------------
def get_bw_array(ch,gamma,inverse,**options):
    import Numeric
    
    not_missing_data = Numeric.greater(ch,0.0).astype('b')
    if inverse:
        ch=-ch
    
    if options.has_key("bwrange"):
        ch_range = options["bwrange"]
        min_ch,max_ch = ch_range[0],ch_range[1]
        if inverse:
            tmp = max_ch
            max_ch = -min_ch
            min_ch = -tmp
    else:
        min_ch,max_ch = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,ch.flat,99999)),\
                        Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,ch.flat,-99999))
        
    print "min & max: ",min_ch,max_ch

    newch = (ch-min_ch) * 255.0/(max_ch-min_ch)
    layer = Numeric.where(Numeric.greater(newch,255),255,Numeric.where(Numeric.less(newch,0),0,newch)).astype('b')
    # Gamma correction:
    layer=(gamma_corr(gamma,layer) * not_missing_data).astype('b')
    
    return layer

# ------------------------------------------------------------------
def make_bw(ch,outprfx,**options):
    import Image
    
    if options.has_key("gamma"):
        gamma=options["gamma"]
    else:
        gamma = 1.0
    if options.has_key("inverse"):
        inverse=options["inverse"]
    else:
        inverse = 0
    if options.has_key("bwrange"):
        layer = get_bw_array(ch,gamma,inverse,bwrange=options["bwrange"])
    else:
        layer = get_bw_array(ch,gamma,inverse)

    imsize = ch.shape[1],ch.shape[0]
    that=Image.fromstring("P", imsize, layer.tostring())    
        
    that.save(outprfx+".png","png")
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    that.save(outprfx+"_thumbnail.png","png")

    return

# ------------------------------------------------------------------
def makergb_nightfog(ch4r,ch9,ch10,outprfx,**options):
    import sm_display_util
    import Numeric
    import Image
    
    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = Numeric.greater(ch9,0.0).astype('b')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    red = ch10-ch9
    green = ch9-ch4r
    blue = Numeric.where(not_missing_data,ch9,nodata)    

    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]
        print "Ch10-Ch9 min & max: ",min_red,max_red
        print "Ch9-Ch4r min & max: ",min_green,max_green
        print "Ch9 min & max: ",min_blue,max_blue
    else:
        min_red,max_red = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,red.flat,99999)),\
                          Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,red.flat,-99999))
        min_green,max_green = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,green.flat,99999)),\
                              Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,green.flat,-99999))
        min_blue,max_blue = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,blue.flat,99999)),\
                            Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,blue.flat,-99999))
        print "Ch10-Ch9 min & max: ",min_red,max_red
        print "Ch9-Ch4r min & max: ",min_green,max_green
        print "Ch9 min & max: ",min_blue,max_blue

    rgb=[None,None,None]
    newred = (red-min_red) * 255.0/(max_red-min_red)
    rgb[0] = Numeric.where(Numeric.greater(newred,255),255,Numeric.where(Numeric.less(newred,0),0,newred))

    newgreen = (green-min_green) * 255.0/(max_green-min_green)
    rgb[1] = Numeric.where(Numeric.greater(newgreen,255),255,Numeric.where(Numeric.less(newgreen,0),0,newgreen))

    newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
    rgb[2] = Numeric.where(Numeric.greater(newblue,255),255,Numeric.where(Numeric.less(newblue,0),0,newblue))

    # Gamma correction:
    rgb[0]=gamma_corr(gamma_red,rgb[0]) * not_missing_data
    rgb[1]=gamma_corr(gamma_green,rgb[1]) * not_missing_data
    rgb[2]=gamma_corr(gamma_blue,rgb[2]) * not_missing_data
    
    red=Image.fromstring("L", imsize, rgb[0].tostring())
    green=Image.fromstring("L", imsize, rgb[1].tostring())
    blue=Image.fromstring("L", imsize, rgb[2].tostring())
    
    that=Image.merge("RGB",(red,green,blue))
    that.save(outprfx+".png","png")
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    that.save(outprfx+"_thumbnail.png","png")

    return

# ------------------------------------------------------------------
def makergb_fog(ch7,ch9,ch10,outprfx,**options):
    #import sm_display_util
    import Numeric,Image
    
    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = Numeric.greater(ch9,0.0).astype('b')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    red = ch10-ch9
    green = ch9-ch7
    blue = Numeric.where(not_missing_data,ch9,nodata)

    min_red,max_red = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,red.flat,99999)),\
                      Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,red.flat,-99999))
    min_green,max_green = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,green.flat,99999)),\
                          Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,green.flat,-99999))
    min_blue,max_blue = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,blue.flat,99999)),\
                        Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,blue.flat,-99999))
    print "Ch10-Ch9 min & max: ",min_red,max_red
    print "Ch9-Ch7 min & max: ",min_green,max_green
    print "Ch9 min & max: ",min_blue,max_blue

    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]

    print "Ch10-Ch9 min & max: ",min_red,max_red
    print "Ch9-Ch7 min & max: ",min_green,max_green
    print "Ch9 min & max: ",min_blue,max_blue
        
    rgb=[None,None,None]
    newred = (red-min_red) * 255.0/(max_red-min_red)
    rgb[0] = Numeric.where(Numeric.greater(newred,255),255,Numeric.where(Numeric.less(newred,0),0,newred))

    newgreen = (green-min_green) * 255.0/(max_green-min_green)
    rgb[1] = Numeric.where(Numeric.greater(newgreen,255),255,Numeric.where(Numeric.less(newgreen,0),0,newgreen))

    newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
    rgb[2] = Numeric.where(Numeric.greater(newblue,255),255,Numeric.where(Numeric.less(newblue,0),0,newblue))

    # Gamma correction:
    rgb[0]=gamma_corr(gamma_red,rgb[0]) * not_missing_data
    rgb[1]=gamma_corr(gamma_green,rgb[1]) * not_missing_data
    rgb[2]=gamma_corr(gamma_blue,rgb[2]) * not_missing_data
    
    red=Image.fromstring("L", imsize, rgb[0].tostring())
    green=Image.fromstring("L", imsize, rgb[1].tostring())
    blue=Image.fromstring("L", imsize, rgb[2].tostring())
    
    that=Image.merge("RGB",(red,green,blue))
    that.save(outprfx+".png","png")
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    that.save(outprfx+"_thumbnail.png","png")


    """
    # Be sure to have the values inside the range [0,255]:
    red_gain=255.0/(max_red-min_red)
    red_icept=-1.*min_red*red_gain
    print "Red channel: Gain,Intercept = %f,%f"%(red_gain,red_icept)
    green_gain=255.0/(max_green-min_green)
    green_icept=-1.*min_green*green_gain
    print "Green channel: Gain,Intercept = %f,%f"%(green_gain,green_icept)
    blue_gain=255.0/(max_blue-min_blue)
    blue_icept=-1.*min_blue*blue_gain
    print "Blue channel: Gain,Intercept = %f,%f"%(blue_gain,blue_icept)

    gl=[red_gain,green_gain,blue_gain]
    il=[red_icept,green_icept,blue_icept]

    that = sm_display_util.make_rgb([red,green,blue],gl,il,not_missing_data)

    that.save(outprfx+".png","png")
    that.thumbnail((size[0]/2,size[1]/2))
    that.save(outprfx+"_thumbnail.png","png")
    """
    
    return

# ------------------------------------------------------------------
def makergb_severe_convection(ch1,ch3,ch4,ch5,ch6,ch9,outprfx,**options):
    import sm_display_util
    import Numeric,Image
    
    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = Numeric.greater(ch9,0.0).astype('b')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    red = ch5-ch6
    green = ch4-ch9
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
        rgb[0] = Numeric.where(Numeric.greater(newred,255),255,Numeric.where(Numeric.less(newred,0),0,newred))

        newgreen = (green-min_green) * 255.0/(max_green-min_green)
        rgb[1] = Numeric.where(Numeric.greater(newgreen,255),255,Numeric.where(Numeric.less(newgreen,0),0,newgreen))

        newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
        rgb[2] = Numeric.where(Numeric.greater(newblue,255),255,Numeric.where(Numeric.less(newblue,0),0,newblue))

        # Gamma correction:
        rgb[0]=gamma_corr(gamma_red,rgb[0]) * not_missing_data
        rgb[1]=gamma_corr(gamma_green,rgb[1]) * not_missing_data
        rgb[2]=gamma_corr(gamma_blue,rgb[2]) * not_missing_data
    
        red=Image.fromstring("L", imsize, rgb[0].tostring())
        green=Image.fromstring("L", imsize, rgb[1].tostring())
        blue=Image.fromstring("L", imsize, rgb[2].tostring())
    
        that=Image.merge("RGB",(red,green,blue))
        
    else:
        min_red,max_red = Numeric.minimum.reduce(red.flat),Numeric.maximum.reduce(red.flat)
        min_green,max_green = Numeric.minimum.reduce(green.flat),Numeric.maximum.reduce(green.flat)
        min_blue,max_blue = Numeric.minimum.reduce(blue.flat),Numeric.maximum.reduce(blue.flat)     
        min_ir = min(min_red,min_green)
        max_ir = max(max_red,max_green)
        min_vis = min_blue
        max_vis = max_blue
    
        # Be sure to have the values inside the range [0,255]:
        red_gain=255.0/(max_red-min_red)
        red_icept=-1.*min_red*red_gain
        print "Red channel: Gain,Intercept = %f,%f"%(red_gain,red_icept)
        green_gain=255.0/(max_green-min_green)
        green_icept=-1.*min_green*green_gain
        print "Green channel: Gain,Intercept = %f,%f"%(green_gain,green_icept)
        blue_gain=255.0/(max_blue-min_blue)
        blue_icept=-1.*min_blue*blue_gain
        print "Blue channel: Gain,Intercept = %f,%f"%(blue_gain,blue_icept)

        gl=[red_gain,green_gain,blue_gain]
        il=[red_icept,green_icept,blue_icept]
        
        that = sm_display_util.make_rgb([red,green,blue],gl,il,not_missing_data)


    print "Ch5-Ch6 min & max: ",min_red,max_red
    print "Ch4-Ch9 min & max: ",min_green,max_green
    print "Ch3-Ch1 min & max: ",min_blue,max_blue
    
    that.save(outprfx+".png","png")
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    that.save(outprfx+"_thumbnail.png","png")

    return

# ------------------------------------------------------------------
def makergb_visvisir(vis1,vis2,ch9,outprfx,**options):
    import sm_display_util
    import Numeric,Image
    
    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = Numeric.greater(ch9,0.0).astype('b')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    red = vis1
    green = vis2
    blue = Numeric.where(not_missing_data,-ch9,nodata)

    min_red,max_red = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,red.flat,99999)),\
                      Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,red.flat,-99999))
    min_green,max_green = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,green.flat,99999)),\
                          Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,green.flat,-99999))
    min_blue,max_blue = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,blue.flat,99999)),\
                        Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,blue.flat,-99999))

    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]

    print "R: min & max: ",min_red,max_red
    print "G: min & max: ",min_green,max_green
    print "B: min & max: ",min_blue,max_blue

    rgb=[None,None,None]
    newred = (red-min_red) * 255.0/(max_red-min_red)
    rgb[0] = Numeric.where(Numeric.greater(newred,255),255,Numeric.where(Numeric.less(newred,0),0,newred))

    newgreen = (green-min_green) * 255.0/(max_green-min_green)
    rgb[1] = Numeric.where(Numeric.greater(newgreen,255),255,Numeric.where(Numeric.less(newgreen,0),0,newgreen))

    newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
    rgb[2] = Numeric.where(Numeric.greater(newblue,255),255,Numeric.where(Numeric.less(newblue,0),0,newblue))

    # Gamma correction:
    rgb[0]=gamma_corr(gamma_red,rgb[0]) * not_missing_data
    rgb[1]=gamma_corr(gamma_green,rgb[1]) * not_missing_data
    rgb[2]=gamma_corr(gamma_blue,rgb[2]) * not_missing_data
    
    red=Image.fromstring("L", imsize, rgb[0].tostring())
    green=Image.fromstring("L", imsize, rgb[1].tostring())
    blue=Image.fromstring("L", imsize, rgb[2].tostring())
    
    that=Image.merge("RGB",(red,green,blue))
    that.save(outprfx+".png","png")
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    that.save(outprfx+"_thumbnail.png","png")

    return


    """
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
    that = sm_display_util.make_rgb([vis1,vis2,ch9],gl,il,not_missing_data)
    that.save(outprfx+".png","png")
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    that.save(outprfx+"_thumbnail.png","png")
    
    return
    """    

# ------------------------------------------------------------------
def makergb_redsnow(ch1,ch3,ch9,outprfx,**options):
    import sm_display_util
    import Numeric

    not_missing_data = Numeric.greater(ch9,0.0).astype('b')
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
    that.save(outprfx+".png","png")
    that.thumbnail((size[0]/2,size[1]/2))
    that.save(outprfx+"_thumbnail.png","png")

    return

# ------------------------------------------------------------------
def makergb_cloudtop(ch4,ch9,ch10,outprfx,**options):
    import sm_display_util
    import Numeric,Image

    if options.has_key("gamma"):
        gamma_red,gamma_green,gamma_blue=options["gamma"]
    else:
        gamma_red = 1.0
        gamma_green = 1.0
        gamma_blue = 1.0

    not_missing_data = Numeric.greater(ch9,0.0).astype('b')
    imsize = not_missing_data.shape[1],not_missing_data.shape[0]

    red = Numeric.where(not_missing_data,-ch4,nodata)
    green = Numeric.where(not_missing_data,-ch9,nodata)
    blue = Numeric.where(not_missing_data,-ch10,nodata)

    min_red,max_red = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,red.flat,99999)),\
                      Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,red.flat,-99999))
    min_green,max_green = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,green.flat,99999)),\
                          Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,green.flat,-99999))
    min_blue,max_blue = Numeric.minimum.reduce(Numeric.where(not_missing_data.flat,blue.flat,99999)),\
                        Numeric.maximum.reduce(Numeric.where(not_missing_data.flat,blue.flat,-99999))

    if options.has_key("rgbrange"):
        range_red = options["rgbrange"][0]
        range_green = options["rgbrange"][1]
        range_blue = options["rgbrange"][2]
        min_red,max_red = range_red[0],range_red[1]
        min_green,max_green = range_green[0],range_green[1]
        min_blue,max_blue = range_blue[0],range_blue[1]

    print "R: min & max: ",min_red,max_red
    print "G: min & max: ",min_green,max_green
    print "B: min & max: ",min_blue,max_blue

    rgb=[None,None,None]
    newred = (red-min_red) * 255.0/(max_red-min_red)
    rgb[0] = Numeric.where(Numeric.greater(newred,255),255,Numeric.where(Numeric.less(newred,0),0,newred))

    newgreen = (green-min_green) * 255.0/(max_green-min_green)
    rgb[1] = Numeric.where(Numeric.greater(newgreen,255),255,Numeric.where(Numeric.less(newgreen,0),0,newgreen))

    newblue = (blue-min_blue) * 255.0/(max_blue-min_blue)
    rgb[2] = Numeric.where(Numeric.greater(newblue,255),255,Numeric.where(Numeric.less(newblue,0),0,newblue))

    # Gamma correction:
    rgb[0]=gamma_corr(gamma_red,rgb[0]) * not_missing_data
    rgb[1]=gamma_corr(gamma_green,rgb[1]) * not_missing_data
    rgb[2]=gamma_corr(gamma_blue,rgb[2]) * not_missing_data
    
    red=Image.fromstring("L", imsize, rgb[0].tostring())
    green=Image.fromstring("L", imsize, rgb[1].tostring())
    blue=Image.fromstring("L", imsize, rgb[2].tostring())
    
    that=Image.merge("RGB",(red,green,blue))
    that.save(outprfx+".png","png")
    that.thumbnail((imsize[0]/2,imsize[1]/2))
    that.save(outprfx+"_thumbnail.png","png")

    return


    """
    not_missing_data = Numeric.greater(ch9,0.0).astype('b')
    size = not_missing_data.shape[1],not_missing_data.shape[0]

    ir_gain=1.0
    ir_intercept=0.0
    irgain = -2.0 * ir_gain
    iricept = 2.0 * (330.66 - ir_intercept)
    gl=[irgain,irgain,irgain]
    il=[iricept,iricept,iricept]
    that = sm_display_util.make_rgb([ch4,ch9,ch10],gl,il,not_missing_data)
    that.save(outprfx+".png","png")
    that.thumbnail((size[0]/2,size[1]/2))
    that.save(outprfx+"_thumbnail.png","png")

    return
    """
# ------------------------------------------------------------------
def get_ch_projected(ch_file,cov):
    import msg_ctype_remap
    import _satproj
    import os
    
    if os.path.exists(ch_file):
        ch_raw = msg_ctype_remap.read_msg_lonlat(ch_file)
    else:
        print "File %s not available!"%(ch_file)
        return None,0
    
    ch_proj = _satproj.project(cov.coverage,cov.rowidx,cov.colidx,ch_raw)

    return ch_proj,1

# ------------------------------------------------------------------
# CO2 correction of the MSG 3.9 um channel:
#
# T4_CO2corr = (BT(IR3.9)^4 + Rcorr)^0.25
# Rcorr = BT(IR10.8)^4 - (BT(IR10.8)-dt_CO2)^4
# dt_CO2 = (BT(IR10.8)-BT(IR13.4))/4.0
#
def co2corr_bt39(bt039,bt108,bt134):
    import Numeric
    epsilon = 0.001
    
    not_missing_data = Numeric.greater(bt108,0.00).astype('b')
    dt_co2 = Numeric.where(not_missing_data,(bt108-bt134)/4.0,0)
    a = Numeric.where(not_missing_data,bt108*bt108*bt108*bt108,0)
    b = Numeric.where(not_missing_data,(bt108-dt_co2)*(bt108-dt_co2)*(bt108-dt_co2)*(bt108-dt_co2),0)
    print Numeric.minimum.reduce(a.flat),Numeric.maximum.reduce(a.flat)
    print Numeric.minimum.reduce(b.flat),Numeric.maximum.reduce(b.flat)
    Rcorr = a - b

    a = Numeric.where(not_missing_data,bt039*bt039*bt039*bt039,0)
    x = Numeric.where(Numeric.logical_and(not_missing_data,Numeric.greater(a+Rcorr,0.0)),(a + Rcorr),epsilon)
    print "x: ",Numeric.minimum.reduce(x.flat),Numeric.maximum.reduce(x.flat)
    #print "a: ",Numeric.minimum.reduce(a.flat),Numeric.maximum.reduce(a.flat)
    #print "Rcorr: ",Numeric.minimum.reduce(Rcorr.flat),Numeric.maximum.reduce(Rcorr.flat)
    
    retv = Numeric.where(not_missing_data,Numeric.exp(0.25*Numeric.log(x)),0)
    
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
    fname = "%.4d%.2d%.2d%.4d_C0429_1999_S0700_0900"%(year,mon,day,hhmm)

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
