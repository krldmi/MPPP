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
import image

try:
    from osgeo import gdal
    from osgeo.gdalconst import *
    from osgeo import osr
except Exception, exc:
    errmsg = `exc.__str__()`
    print "The exception was: ",errmsg
    pass


MODULE_ID = "GEO IMAGE"

class GeoImage(image.Image):
    """This class defines geographic images. As such, it contains not only data
    of the different *channels* of the image, but also the area on which it is
    defined (*area_id* parameter) and *time_slot* of the snapshot.
    
    The channels are considered to contain floating point values in the range
    [0.0,1.0]. In order to normalize the input data, the *range* parameter
    defines the original range of the data. The conversion to the classical
    [0,255] range and byte type is done automagically when saving the image to
    file.

    See also :class:`image.Image` for more information.
    """
    area_id = None
    time_slot = None

    def __init__(self,channels, area_id, time_slot, 
                 mode = "L",range = None, fill_value = None, palette = None):
        self.area_id = area_id
        self.time_slot = time_slot
        super(GeoImage,self).__init__(channels, mode, range, fill_value, palette)

    def save(self, filename):
        """Save the image to the given *filename*. If the extension is "tif",
        the image is saved to geotiff_ format. See also
        :meth:`image.Image.save`, :meth:`image.Image.double_save`, and
        :meth:`image.Image.secure_save`.

        .. _geotiff: http://trac.osgeo.org/geotiff/
        """
        file_tuple = os.path.splitext(filename)

        if(file_tuple[1] == ".tif" and
           # HACK -- We should add the globe region to acpg ! Martin,
           # 2009-10-09
           self.area_id != "globe"):
            self._geotiff_save(filename)
        else:
            super(GeoImage,self).save(filename)

    def _geotiff_save(self,filename):
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

