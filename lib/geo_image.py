import os
import tempfile
import Image
import numpy as np
import shutil
import string
import area
import image_processing
import misc_utils
import msg_communications
import acpgimage
import msgpp_config
import _acpgpilext
import pps_array2image

try:
    from osgeo import gdal
    from osgeo.gdalconst import *
    from osgeo import osr
except Exception, exc:
    errmsg = `exc.__str__()`
    print "The exception was: ",errmsg
    pass


MODULE_ID = "GEO IMAGE"

class GeoImage:
    """This class defines geographic images. As such, it contains not only data
    of the different *channels* (r, g, b for example), but also the area on
    which it is defined (*area_id* parameter) and *time_slot* of the
    snapshot. The *mode* tells if the channels define a black and white image
    ("L"), an rgb image ("RGB"), an rgba image ("RGBA"), an YCbCr image
    ("YCbCr"), or an indexed image ("P"), in which case a *palette* is
    needed. *fill_value* sets how the image is filled where data is
    missing. Setting it to (0,0,0) in RGB mode for example will produce black
    where data is missing. "None" will produce transparency instead (if the
    file format allows it).
    
    The channels are considered to contain floating point values in the range
    [0.0:1.0]. In order to normalize the input data, the *range* parameter
    defines the original range of the data. The conversion to the classical
    [0:255] range and byte type is done automagically when saving the image to
    file.
    """
    area_id = None
    time_slot = None
    channels = None
    mode = None
    width = 0
    height = 0
    fill_value = None
    palette = None

    def __init__(self,channels, area_id, time_slot, 
                 mode = "L",range = None, fill_value = None, palette = None):
        self.area_id = area_id
        self.time_slot = time_slot
        self.mode = mode
        self.fill_value = fill_value
        self.channels = []
        self.palette = palette
        if(isinstance(channels,tuple) or
           isinstance(channels,list)):
            self.height = channels[0].shape[0]
            self.width = channels[0].shape[1]
            
            i = 0
            for ch in channels:
                if range is not None:
                    min = range[i][0]
                    max = range[i][1]
                else:
                    min = 0.0
                    max = 1.0
                self.channels.append((ch - min) * 1.0 / (max - min))
                i = i + 1
        else:
            self.height = channels.shape[0]
            self.width = channels.shape[1]

            if range is not None:
                min = range[0]
                max = range[1]
            else:
                min = 0.0
                max = 1.0
            self.channels.append((channels - min) * 1.0 / (max - min))

    def _finalize(self):
        channels = []
        if self.mode == "P":
            self.convert("RGB")
        if self.mode == "PA":
            self.convert("RGBA")

        for ch in self.channels:
            channels.append(np.ma.array(ch.clip(0,1)*255,
                                        np.uint8,
                                        mask = ch.mask))
        return channels


    def secure_save(self, filename):
        """Save the current image to *filename* using a temporary file at
        first, then renaming it to the final filename. See also
        :meth:`GeoImage.save` and :meth:`GeoImage.double_save`.
        """
        misc_utils.ensure_dir(filename)

        file,ext = os.path.splitext(filename)
        path,file = os.path.split(filename)
        trash,tmpfilename = tempfile.mkstemp(suffix = ext,
                                             dir = path)
        self.save(tmpfilename)
        os.rename(tmpfilename,filename)
        os.chmod(filename, 0644)        

    def double_save(self,local_filename,remote_filename):
        """Save the current image to *local_filename*, then copy it to
        *remote_filename*, using a temporary file at first, then renaming it to
        the final remote filename. See also :meth:`GeoImage.save` and
        :meth:`GeoImage.secure_save`.
        """
        self.secure_save(local_filename)

        misc_utils.ensure_dir(remote_filename)

        file,ext = os.path.splitext(remote_filename)
        path,file = os.path.split(remote_filename)
        trash,tmpfilename = tempfile.mkstemp(suffix = ext,
                                             dir = path)
        shutil.copy(local_filename,tmpfilename)
        try:
            os.rename(tmpfilename,remote_filename)
        except OSError:
            msg_communications.msgwrite_log("ERROR","Could not rename to %s ! Saving of this file failed !"%remote_filenam,moduleid=MODULE_ID)
            if os.path.isfile(remote_filemame):
                msg_communications.msgwrite_log("WARNING","The file already exists, skipping...",moduleid=MODULE_ID)
                if os.path.isfile(tmpfilename):
                    os.remove(tmpfilename)
            elif not os.path.isfile(tmpfilename):
                msg_communications.msgwrite_log("ERROR","Copy to %s, failed ! skipping..."%tmpfilename,moduleid=MODULE_ID)
            else:
                msg_communications.msgwrite_log("WARNING","Temp file is %s, removing it"%tmpfilename,moduleid=MODULE_ID)
            os.remove(tmpfilename)

        os.chmod(remote_filename, 0644)

    def save(self, filename):
        """Save the image to the given *filename*. If the extension is "tif",
        the image is saved to geotiff_ format. See also
        :meth:`GeoImage.double_save` and :meth:`GeoImage.secure_save`.

        .. _geotiff: http://trac.osgeo.org/geotiff/
        """
        file_tuple = os.path.splitext(filename)

        misc_utils.ensure_dir(filename)

        msg_communications.msgwrite_log("INFO","Saving image in mode: ",self.mode,moduleid=MODULE_ID)


        # Suppress geotiff ability for now -- Martin, 2009-10-12
        if(file_tuple[1] == ".tif" and
           # HACK -- We should add the globe region to acpg ! Martin,
           # 2009-10-09
           self.area_id != "globe"):
            self.geotiff_save(filename)
            return
        else:
            channels = self._finalize()
            if(self.mode == "L"):
                misc_utils.ensure_dir(filename)
                if self.fill_value is not None:
                    im = Image.fromarray(channels[0].filled(self.fill_value))
                    im.save(filename)
                else:
                    l = Image.fromarray(channels[0].filled(0))
                    alpha = np.zeros(channels[0].shape,np.uint8)
                    mask = np.ma.getmaskarray(channels[0])
                    alpha = np.where(mask, alpha, 255)
                    a = Image.fromarray(alpha)

                    Image.merge("LA",(l,a)).save(filename)

            elif(self.mode == "RGB"):
                misc_utils.ensure_dir(filename)
                if self.fill_value is not None:
                    r = Image.fromarray(channels[0].filled(self.fill_value[0]))
                    g = Image.fromarray(channels[1].filled(self.fill_value[1]))
                    b = Image.fromarray(channels[2].filled(self.fill_value[2]))
                    Image.merge("RGB",(r,g,b)).save(filename)
                else:
                    r = Image.fromarray(channels[0].filled(0))
                    g = Image.fromarray(channels[1].filled(0))
                    b = Image.fromarray(channels[2].filled(0))

                    alpha = np.zeros(channels[0].shape,np.uint8)
                    mask = (np.ma.getmaskarray(channels[0]) | 
                            np.ma.getmaskarray(channels[1]) | 
                            np.ma.getmaskarray(channels[2]))
                    alpha = np.where(mask,alpha, 255)
                    a = Image.fromarray(alpha)

                    Image.merge("RGBA",(r,g,b,a)).save(filename)
                    
            elif(self.mode == "RGBA"):
                misc_utils.ensure_dir(filename)
                if self.fill_value is not None:
                    r = Image.fromarray(channels[0].filled(self.fill_value[0]))
                    g = Image.fromarray(channels[1].filled(self.fill_value[1]))
                    b = Image.fromarray(channels[2].filled(self.fill_value[2]))
                    a = Image.fromarray(channels[3].filled(self.fill_value[3]))
                    Image.merge("RGBA",(r,g,b,a)).save(filename)
                else:
                    r = Image.fromarray(channels[0].filled(0))
                    g = Image.fromarray(channels[1].filled(0))
                    b = Image.fromarray(channels[2].filled(0))

                    mask = (np.ma.getmaskarray(channels[0]) | 
                            np.ma.getmaskarray(channels[1]) | 
                            np.ma.getmaskarray(channels[2]) |
                            np.ma.getmaskarray(channels[3]))

                    alpha = np.where(mask, 0, channels[3])
                    a = Image.fromarray(alpha)

                    Image.merge("RGBA",(r,g,b,a)).save(filename)
                    

    def geotiff_save(self,filename):
        """Save the image to the given *filename* in geotiff_ format.
        
        .. _geotiff: http://trac.osgeo.org/geotiff/
        """
        raster = gdal.GetDriverByName("GTiff")
                    
        channels = self._finalize()

        msg_communications.msgwrite_log("INFO","Saving to GeoTiff. ",moduleid=MODULE_ID)

        if(self.mode == "L"):
            misc_utils.ensure_dir(filename)
            if self.fill_value is not None:
                dst_ds = raster.Create( filename, 
                                        self.width, 
                                        self.height, 
                                        1, 
                                        gdal.GDT_Byte)
                ch = channels[0].filled(self.fill_value)
                dst_ds.GetRasterBand(1).WriteArray(ch)
            
            else:
                dst_ds = raster.Create( filename, 
                                        self.width, 
                                        self.height, 
                                        2, 
                                        gdal.GDT_Byte)
                dst_ds.GetRasterBand(1).WriteArray(channels[0].filled(0))
                alpha = np.zeros(channels[0].shape,np.uint8)
                mask = np.ma.getmaskarray(channels[0])
                alpha = np.where(mask, alpha, 255)
                dst_ds.GetRasterBand(2).WriteArray(alpha)
        elif(self.mode == "RGB"):
            misc_utils.ensure_dir(filename)
            if self.fill_value is not None:
                dst_ds = raster.Create( filename, 
                                        self.width, 
                                        self.height, 
                                        3, 
                                        gdal.GDT_Byte)

                ch = channels[0].filled(self.fill_value[0])
                dst_ds.GetRasterBand(1).WriteArray(ch)

                ch = channels[1].filled(self.fill_value[1])
                dst_ds.GetRasterBand(2).WriteArray(ch)

                ch = channels[2].filled(self.fill_value[2])
                dst_ds.GetRasterBand(3).WriteArray(ch)
            else:
                mask = (channels[0].mask |
                        channels[1].mask |
                        channels[2].mask)
                dst_ds = raster.Create( filename, 
                                        self.width, 
                                        self.height, 
                                        4, 
                                        gdal.GDT_Byte)
                dst_ds.GetRasterBand(1).WriteArray(channels[0].filled(0))
                dst_ds.GetRasterBand(2).WriteArray(channels[1].filled(0))
                dst_ds.GetRasterBand(3).WriteArray(channels[2].filled(0))

                alpha = np.zeros(channels[0].shape,np.uint8)
                mask = (np.ma.getmaskarray(channels[0]) | 
                        np.ma.getmaskarray(channels[1]) | 
                        np.ma.getmaskarray(channels[2]))
                alpha = np.where(mask,alpha, 255)
                dst_ds.GetRasterBand(4).WriteArray(alpha)

        elif(self.mode == "RGBA"):
            misc_utils.ensure_dir(filename)
            dst_ds = raster.Create( filename, 
                                    self.width, 
                                    self.height, 
                                    4, 
                                    gdal.GDT_Byte)
            if self.fill_value is not None:
                ch = channels[0].filled(self.fill_value[0])
                dst_ds.GetRasterBand(1).WriteArray(ch)

                ch = channels[1].filled(self.fill_value[1])
                dst_ds.GetRasterBand(2).WriteArray(ch)

                ch = channels[2].filled(self.fill_value[2])
                dst_ds.GetRasterBand(3).WriteArray(ch)

                ch = channels[3].filled(self.fill_value[3])
                dst_ds.GetRasterBand(4).WriteArray(ch)
            else:
                dst_ds.GetRasterBand(1).WriteArray(channels[0].filled(0))
                dst_ds.GetRasterBand(2).WriteArray(channels[1].filled(0))
                dst_ds.GetRasterBand(3).WriteArray(channels[2].filled(0))

                mask = (np.ma.getmaskarray(channels[0]) | 
                        np.ma.getmaskarray(channels[1]) | 
                        np.ma.getmaskarray(channels[2]) |
                        np.ma.getmaskarray(channels[3]))
                
                alpha = np.where(mask, 0, channels[3])

                dst_ds.GetRasterBand(4).WriteArray(alpha)



                
        # Create raster GeoTransform based on upper left corner and pixel
        # resolution
            
        area_input = area.area(self.area_id)
        topLeftXY = area_input.extent[0],area_input.extent[3]
        scalexy = area_input.xscale,-area_input.yscale
        
        adfGeoTransform = [topLeftXY[0],scalexy[0],0,
                           topLeftXY[1],0,scalexy[1]]
        
        dst_ds.SetGeoTransform(adfGeoTransform)
        srs = osr.SpatialReference()
        srs.SetProjCS(area_input.pcs.id)
        pcs_def = "+"+string.join(area_input.pcs.definition," +")
        status = srs.ImportFromProj4(pcs_def)
        
        srs.SetWellKnownGeogCS('WGS84')
        dst_ds.SetProjection(srs.ExportToWkt())

        tag = {'TIFFTAG_DATETIME':self.time_slot.strftime("%Y:%m:%d %H:%M:%S")}

        dst_ds.SetMetadata(tag,'')
        
        # Close the dataset
        
        dst_ds = None


    def putalpha(self, alpha):
        """Adds an *alpha* channel to the current image, or replaces it with
        *alpha* if it already exists.
        """
        if(not self.mode.endswith("A")):
            self.convert(self.mode+"A")
        self.channels[-1] = alpha
        

    def convert(self, mode):
        """Convert the current to the given *mode*.
        """
        if mode == self.mode:
            return

        if(mode == self.mode+"A"):
            self.channels.append(np.ma.ones(self.channels[0].shape))
            self.mode = mode

        elif((self.mode == "P" and
            mode == "RGB") or
           (self.mode == "PA" and
            mode == "RGBA")):


            p = np.ma.array(self.channels[0])
            a = np.ma.array(self.channels[-1])
            if self.mode == "PA":
                for i in range(len(self.channels),4):
                    self.channels.append(np.ma.zeros(p.shape))
                    self.channels[i].mask = p.mask

                self.channels[3] = a
            else:
                for i in range(len(self.channels),3):
                    self.channels.append(np.ma.zeros(p.shape))
                    self.channels[i].mask = p.mask

            

            rcdf = np.zeros(len(self.palette))
            gcdf = np.zeros(len(self.palette))
            bcdf = np.zeros(len(self.palette))

            for i in range(len(self.palette)):
                rcdf[i] = self.palette[i][0]
                gcdf[i] = self.palette[i][1]
                bcdf[i] = self.palette[i][2]

            self.channels[0] = \
                np.ma.array(np.interp(p,
                                      np.arange(len(self.palette)),
                                      rcdf),
                            mask = p.mask)
            self.channels[1] = \
                np.ma.array(np.interp(p,
                                      np.arange(len(self.palette)),
                                      gcdf),
                            mask = p.mask)
            self.channels[2] = \
                np.ma.array(np.interp(p,
                                      np.arange(len(self.palette)),
                                      bcdf),
                            mask = p.mask)

            self.mode = mode

        elif((self.mode == "RGB" and
            mode == "YCbCr") or
           (self.mode == "RGBA" and
            mode == "YCbCrA")):
            
            Kb = 0.114
            Kr = 0.299

            R = self.channels[0]
            G = self.channels[1]
            B = self.channels[2]

            Y = Kr * R + (1 - Kr - Kb) * G + Kb * B
            Cb = 1 / (2 * (1 - Kb)) * (B - Y)
            Cr = 1 / (2 * (1 - Kr)) * (R - Y)
            
            self.channels[0] = Y
            self.channels[1] = Cb
            self.channels[2] = Cr
            
            self.mode = mode

        elif((self.mode == "YCbCr" and
              mode == "RGB") or
             (self.mode == "YCbCrA" and
              mode == "RGBA")):
            
            Kb = 0.114
            Kr = 0.299

            Y = self.channels[0]
            Cb = self.channels[1]
            Cr = self.channels[2]

            
            R = 2 * Cr / (1 - Kr) + Y
            B = 2 * Cb / (1 - Kb) + Y
            G = (Y - Kr * R - Kb * B) / (1 - Kr - Kb)

            self.channels[0] = R
            self.channels[1] = G
            self.channels[2] = B

            self.mode = mode
            
        else:
            raise NameError("Conversion from %s to %s not implemented !"
                            %(self.mode,mode))
            

    def clip(self,c = True):
        """Limit the values of the array to the default [0,1] range. *c* says
        which channels should be clipped."""
        if not (isinstance(c, tuple) or
                isinstance(c, list)):
            c = [c]*len(self.channels)
            
        for i in range(len(self.channels)):
            if c[i]:
                self.channels[i] = np.ma.clip(self.channels[i],0.0,1.0)

    def resize(self,shape):
        """Resize the image to the given *shape* tuple, in place.
        """
        factor = channels[0] * 1.0 / shape[0]

        if int(factor) != factor:
            raise NameError("Resize not of integer factor!")

        i = 0
        for ch in self.channels:
            ch = ch.repeat([factor]*ch.shape[0],axis = 0)
            self.channels[i] = ch.repeat([factor]*a.shape[1],axis = 1)
            i = i + 1

    def replace_luminance(self,luminance):
        """Replace the Y channel of the image by the array *luminance*. If the
        image is not in YCbCr mode, it is converted automatically to and
        from that mode.
        """
        if (luminance.shape != self.channels[0].shape):
            if ((luminance.shape[0] * 1.0 / luminance.shape[1]) ==
                (channels[0].shape[0] * 1.0 / channels[0].shape[1])):
                if luminance.shape[0] > channels[0].shape[0]:
                    for ch in channels:
                        self.resize(luminance.shape)
                else:
                    luminance = resize(luminance)
            else:
                raise NameError("Luminance replacement: Not the good shape !")
        
        mode = self.mode
        if mode.endswith("A"):
            self.convert("YCbCrA")
            self.channels[0] = luminance
            self.convert(mode)
        else:
            self.convert("YCbCr")
            self.channels[0] = luminance
            self.convert(mode)
            
    def enhance(self, inverse = False, gamma = 1.0, stretch = "no"):
        """Image enhancement function. It applies **in this order** inversion,
        gamma correction, and stretching to the current image, with parameters
        *inverse* (see :meth:`GeoImage.invert`), *gamma* (see
        :meth:`GeoImage.gamma`), and *stretch* (see :meth:`GeoImage.stretch`).
        """
        self.invert(inverse)
        self.gamma(gamma)
        self.stretch(stretch)
        
    def gamma(self,gamma = 1.0):
        """Apply gamma correction to the channels of the image. If *gamma* is a
        tuple, then is should have as many elements as the channels of the
        image, and the gamma correction is applied elementwise. If *gamma* is a
        number, the same gamma correction is applied on every channel, if there
        are several channels in the image. The behaviour of :func:`gamma` is
        undefined outside the normal [0,1] range of the channels.
        """
        if gamma == 1.0:
            return
        if (isinstance(gamma,tuple) or
            isinstance(gamma,list)):
            for i in range(len(gamma)):
                self.channels[i] = np.where(self.channels[i] >= 0,
                                            self.channels[i] ** (1 / gamma[i]),
                                            self.channels[i])
        else:
            i = 0
            for ch in self.channels:
                self.channels[i] = np.where(ch >= 0,
                                            ch ** (1 / gamma),
                                            ch)
                i = i + 1
        
    def stretch(self, stretch = "no"):
        """Apply stretching to the current image. The value of *stretch* sets
        the type of stretching applied. The values "histogram", "linear",
        "crude" (or "crude-stretch") perform respectively histogram
        equalization, contrast stretching (with 5% cutoff on both sides), and
        contrast stretching without cutoff. If a tuple or a list of two values
        is given as input, then a contrast stretching is performed with the
        values as cutoff. These values should be normalized in the range
        [0.0,1.0].
        """
        if((isinstance(stretch,tuple) or
            isinstance(stretch,list)) and
           len(stretch) == 2):
            cutoffs = stretch
            i = 0
            for ch in self.channels:
                self.channels[i] = stretch_linear(ch, cutoffs)
                i = i + 1
        elif stretch == "linear":
            i = 0
            for ch in self.channels:
                self.channels[i] = stretch_linear(ch)
                i = i + 1
        elif stretch == "histogram":
            i = 0
            for ch in self.channels:
                self.channels[i] = stretch_hist_equalize(ch)
                i = i + 1
        elif(stretch == "crude" or
             stretch == "crude-stretch"):
            i = 0
            for ch in self.channels:
                self.channels[i] = crude_stretch(ch)
                i = i + 1

    def invert(self, invert = False):
        """Inverts all the channels of a image according to *invert*. If invert
        is a tuple or a list, elementwise invertion is performed, otherwise all
        channels are inverted if *invert* is true.
        """
        if(isinstance(invert, tuple) or
           isinstance(invert, list)):
            i = 0
            for ch in self.channels:
                if(invert[i]):
                    self.channels[i] = 1.0 - ch
                i = i + 1
        elif(invert):
            i = 0
            for ch in self.channels:
                self.channels[i] = 1.0 - ch
                i = i + 1
         
    def add_overlay(self, color = (0,0,0)):
        """Add coastline and political borders to image, using *color*.
        """
        self.convert("RGB")


        arr = np.zeros(self.channels[0].shape,np.uint8)
        
        msg_communications.msgwrite_log("INFO","Add coastlines and political borders to image. Area = %s"%(self.area_id),moduleid=MODULE_ID)
        rimg = acpgimage.image(self.area_id)
        rimg.info["nodata"]=255
        rimg.data = arr
        area_overlayfile = "%s/coastlines_%s.asc"%(msgpp_config.AUX_DIR,self.area_id)
        msg_communications.msgwrite_log("INFO","Read overlay. Try find something prepared on the area...",moduleid=MODULE_ID)
        try:
            overlay = _acpgpilext.read_overlay(area_overlayfile)
            msg_communications.msgwrite_log("INFO","Got overlay for area: ",area_overlayfile,moduleid=MODULE_ID)
        except:            
            msg_communications.msgwrite_log("INFO","Didn't find an area specific overlay. Have to read world-map...",moduleid=MODULE_ID)
            overlay = _acpgpilext.read_overlay(msgpp_config.COAST_FILE)
            pass        
        msg_communications.msgwrite_log("INFO","Add overlay",moduleid=MODULE_ID)
        overlay_image = pps_array2image.add_overlay(rimg,
                                                    overlay,
                                                    Image.fromarray(arr),
                                                    color = 1)

        val = np.ma.asarray(overlay_image)

        self.channels[0] = np.ma.where(val == 1, color[0], self.channels[0])
        self.channels[0].mask = np.where(val == 1,
                                         False,
                                         np.ma.getmaskarray(self.channels[0]))

        self.channels[1] = np.ma.where(val == 1, color[1], self.channels[1])
        self.channels[1].mask = np.where(val == 1,
                                         False,
                                         np.ma.getmaskarray(self.channels[1]))

        self.channels[2] = np.ma.where(val == 1, color[2], self.channels[2])
        self.channels[2].mask = np.where(val == 1,
                                         False,
                                         np.ma.getmaskarray(self.channels[2]))


   
def stretch_hist_equalize(arr):
    """Stretch a monochromatic masked array *arr* by performing
    histogram equalization. The stretched array is returned.
    """
    msg_communications.msgwrite_log("INFO",
                                    "Perform a histogram equalized contrast stretch of one image layer",moduleid=MODULE_ID)

    nwidth=2048.0

    carr = arr.compressed()

    imhist,bins = np.histogram(carr,nwidth,normed=True)
    cdf = imhist.cumsum() - imhist[0]
    cdf = cdf / cdf[-1]
    
    res = np.ma.empty_like(arr)
    res.mask = arr.mask
    res[~res.mask] = np.interp(carr,bins[:-1],cdf)
    
    return res

def stretch_linear(arr,cutoffs=(0.005,0.005)):
    """Stretch linearly the contrast of a monochromatic masked array
    *arr*, using *cutoffs* for left and right trimming.
    """
    msg_communications.msgwrite_log("INFO","Perform a linear contrast stretch of one image layer",moduleid=MODULE_ID)

    nwidth=2048.0
    
    carr = arr.compressed()

    hist,bins = np.histogram(carr, nwidth)

    ndim = carr.size

    left = 0
    sum = 0.0
    i = 0
    while i <= nwidth and sum < cutoffs[0]*ndim:
	sum = sum + hist[i]
	i = i + 1

    left = bins[i-1]

    right = 0
    sum = 0.0
    i = nwidth - 1
    while i >= 0 and sum < cutoffs[1]*ndim:
	sum = sum + hist[i]
	i = i - 1


    right = bins[i+1]
    dx = (right-left)
    msg_communications.msgwrite_log("INFO","Interval: left=%f,right=%f width=%f"%(left,right,dx),moduleid=MODULE_ID)
    if dx > 0.0:
	res = np.ma.array((arr - left) / dx, mask = arr.mask)
    else:
	res = np.ma.zeros(arr.shape)
	msg_communications.msgwrite_log("WARNING","Unable to make a contrast stretch!",moduleid=MODULE_ID)

    return res

def crude_stretch(arr, min = None, max = None):
    """Perform simple linear stretching (without any cutoff) on *arr* and
    normalize to the [*min*,\ *max*] range."""

    if(min is None):
        min = arr.min()
    if(max is None):
        max = arr.max()
        
    return (arr - min) * 1.0 / (max - min) 
