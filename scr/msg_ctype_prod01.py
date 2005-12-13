#
#
from msgpp_config import *
from msg_remap_util import *
from msg_ctype_remap import *
from msg_rgb_remap import *

# ------------------------------------------------------------------
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
    bw = get_bw_array(irch,1,gamma)

    if not os.path.exists(ctypefile):
        print "ERROR: Cloud Type product not found! Filename = %s"%ctypefile
        return
        
    # Read the Cloud Type product:
    that = epshdf.read_cloudtype(ctypefile,1,0,0)
    legend = smhi_safnwc_legends.get_vv_legend()
    arr = Numeric.where(Numeric.logical_and(Numeric.less_equal(that.cloudtype,8),
                                            Numeric.greater_equal(that.cloudtype,5)),that.cloudtype-2,bw)
    arr = Numeric.where(Numeric.less_equal(that.cloudtype,2),that.cloudtype,arr).astype('b')
    
    shape = that.cloudtype.shape    
    size=shape[1],shape[0]
    this = Image.fromstring("P",shape,arr.tostring())
    newleg=[]
    for i in legend:    
	newleg = newleg + list(i)
    this.putpalette(newleg)
    this = this.convert("RGB")

    if withCoast:
        print "INFO: Add coastlines and political borders to image. Area = %s"%(areaid)
        rimg = acpgimage.image(areaid)
        rimg.info["nodata"]=255
        rimg.data = arr.astype('b')
        area_overlayfile = "%s/coastlines_%s.asc"%(AUX_DIR,areaid)
        print "INFO: Read overlay. Try find something prepared on the area..."
        try:
            overlay = _acpgpilext.read_overlay(area_overlayfile)
            print "INFO: Got overlay for area: ",area_overlayfile
        except:            
            print "INFO: Didn't find an area specific overlay. Have to read world-map..."
            overlay = _acpgpilext.read_overlay(COAST_FILE)
            pass        
        thumb = this.copy()
        print "INFO: Add overlay"
        this = pps_array2image.add_overlay(rimg,overlay,this)

    imagefile = ctypefile.split(".hdf")[0] + "_ir.png"
    this.save(imagefile)
    thumb.thumbnail((size[0]/3,size[1]/3))
    thumbnail = ctypefile.split(".hdf")[0] + "_ir.thumbnail.png"
    thumb.save(thumbnail)

    return

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
    fname = "%.4d%.2d%.2d%.2d%.2d_C%.4d_%.4d_S%.4d_%.4d"%(year,month,day,hour,min,MSG_AREA_CENTER[0],MSG_AREA_CENTER[1],ROWS,COL)

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
    

