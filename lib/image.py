"""This module defines the image class. It overlaps largely the PIL library,
but has the advandage of using masked arrays as pixel arrays.
"""

import os
import tempfile
import Image as Pil
import numpy as np
import shutil
import logging
import logging.config

from msgpp_config import APPLDIR
import misc_utils

logging.config.fileConfig(APPLDIR+"/etc/logging.conf")
LOG = logging.getLogger("pp.image")


class Image(object):
    """This class defines images. As such, it contains data of the different
    *channels* of the image (red, green, and blue for example). The *mode*
    tells if the channels define a black and white image ("L"), an rgb image
    ("RGB"), an rgba image ("RGBA"), an YCbCr image ("YCbCr"), or an indexed
    image ("P"), in which case a *palette* is needed. *fill_value* sets how the
    image is filled where data is missing, since channels are numpy masked
    arrays. Setting it to (0,0,0) in RGB mode for example will produce black
    where data is missing. "None" (default) will produce transparency if the
    file format allows it, black otherwise.
    
    The channels are considered to contain floating point values in the range
    [0.0,1.0]. In order to normalize the input data, the *range* parameter
    defines the original range of the data. The conversion to the classical
    [0,255] range and byte type is done automagically when saving the image to
    file.
    """
    channels = None
    mode = None
    width = 0
    height = 0
    fill_value = None
    palette = None
    
    #Shape (dimensions) of the image.
    shape = None
    
    def __init__(self, channels, mode = "L", color_range = None, 
                 fill_value = None, palette = None):
        self.mode = mode
        self.fill_value = fill_value
        self.channels = []
        self.palette = palette
        if isinstance(channels, (tuple, list)):
            self.height = channels[0].shape[0]
            self.width = channels[0].shape[1]
            self.shape = channels[0].shape

            i = 0
            for chn in channels:
                if color_range is not None:
                    color_min = color_range[i][0]
                    color_max = color_range[i][1]
                else:
                    color_min = 0.0
                    color_max = 1.0
                self.channels.append((chn - color_min) * 1.0 / 
                                     (color_max - color_min))
                i = i + 1
        else:
            self.height = channels.shape[0]
            self.width = channels.shape[1]
            self.shape = channels.shape

            if color_range is not None:
                color_min = color_range[0]
                color_max = color_range[1]
            else:
                color_min = 0.0
                color_max = 1.0
            self.channels.append((channels - color_min) * 1.0 / 
                                 (color_max - color_min))

    def _finalize(self):
        """Finalize the image, that is put it in RGB mode, and set the channels
        in 8bit format ([0,255] range).
        """
        channels = []
        if self.mode == "P":
            self.convert("RGB")
        if self.mode == "PA":
            self.convert("RGBA")

        for chn in self.channels:
            channels.append(np.ma.array(chn.clip(0, 1) * 255,
                                        np.uint8,
                                        mask = chn.mask))
        return channels


    def secure_save(self, filename):
        """Save the current image to *filename* using a temporary file at
        first, then renaming it to the final filename. See also
        :meth:`save` and :meth:`double_save`.
        """
        misc_utils.ensure_dir(filename)

        trash, ext = os.path.splitext(filename)
        path, trash = os.path.split(filename)
        trash, tmpfilename = tempfile.mkstemp(suffix = ext,
                                              dir = path)
        del trash

        self.save(tmpfilename)
        os.rename(tmpfilename, filename)
        os.chmod(filename, 0644)


    def double_save(self, local_filename, remote_filename):
        """Save the current image to *local_filename*, then copy it to
        *remote_filename*, using a temporary file at first, then renaming it to
        the final remote filename. See also :meth:`save` and
        :meth:`secure_save`.
        """
        self.secure_save(local_filename)

        misc_utils.ensure_dir(remote_filename)

        file, ext = os.path.splitext(remote_filename)
        path, file = os.path.split(remote_filename)
        trash, tmpfilename = tempfile.mkstemp(suffix = ext,
                                              dir = path)

        try:
            shutil.copy(local_filename, tmpfilename)
        except IOError, (errno, strerror):
            import errno as err
            LOG.error("Copying file %s to %s failed"
                      %(local_filename, tmpfilename))
            LOG.error("I/O error(%d): %s"%(errno, strerror))
            if errno == err.ESTALE:
                log.info("Retrying once...")
                try:
                    shutil.copy(local_filename, tmpfilename)
                except IOError, (errno, strerror):
                    LOG.error("Copying file %s to %s failed"
                              %(local_filename,tmpfilename))
                    LOG.error("I/O error(%d): %s"%(errno, strerror))
                    LOG.info("Retry did not succeed, skipping.")


        try:
            os.chmod(remote_filename, 0644)
            os.rename(tmpfilename, remote_filename)
        except OSError:
            LOG.error("Could not rename to %s !"%remote_filename)
            if os.path.isfile(remote_filename):
                LOG.warning("The file already exists, skipping...")
            elif not os.path.isfile(tmpfilename):
                LOG.error("Copy to %s, failed ! skipping..."%tmpfilename)
            if os.path.isfile(tmpfilename):
                LOG.warning("Temp file is %s, removing it."%tmpfilename)
                os.remove(tmpfilename)


    def save(self, filename):
        """Save the image to the given *filename*. See also
        :meth:`double_save` and :meth:`secure_save`.
        """
        channels = self._finalize()

        misc_utils.ensure_dir(filename)

        if(self.mode == "L"):
            misc_utils.ensure_dir(filename)
            if self.fill_value is not None:
                img = Pil.fromarray(channels[0].filled(self.fill_value))
                img.save(filename)
            else:
                img = Pil.fromarray(channels[0].filled(0))
                alpha = np.zeros(channels[0].shape, np.uint8)
                mask = np.ma.getmaskarray(channels[0])
                alpha = np.where(mask, alpha, 255)
                pil_alpha = Pil.fromarray(alpha)
                
                Pil.merge("LA", (img, pil_alpha)).save(filename)

        elif(self.mode == "RGB"):
            misc_utils.ensure_dir(filename)
            if self.fill_value is not None:
                pil_r = Pil.fromarray(channels[0].filled(self.fill_value[0]))
                pil_g = Pil.fromarray(channels[1].filled(self.fill_value[1]))
                pil_b = Pil.fromarray(channels[2].filled(self.fill_value[2]))
                Pil.merge("RGB", (pil_r, pil_g, pil_b)).save(filename)
            else:
                pil_r = Pil.fromarray(channels[0].filled(0))
                pil_g = Pil.fromarray(channels[1].filled(0))
                pil_b = Pil.fromarray(channels[2].filled(0))

                alpha = np.zeros(channels[0].shape, np.uint8)
                mask = (np.ma.getmaskarray(channels[0]) | 
                        np.ma.getmaskarray(channels[1]) | 
                        np.ma.getmaskarray(channels[2]))
                alpha = np.where(mask, alpha, 255)
                pil_a = Pil.fromarray(alpha)

                Pil.merge("RGBA", (pil_r, pil_g, pil_b, pil_a)).save(filename)

        elif(self.mode == "RGBA"):
            misc_utils.ensure_dir(filename)
            if self.fill_value is not None:
                pil_r = Pil.fromarray(channels[0].filled(self.fill_value[0]))
                pil_g = Pil.fromarray(channels[1].filled(self.fill_value[1]))
                pil_b = Pil.fromarray(channels[2].filled(self.fill_value[2]))
                pil_a = Pil.fromarray(channels[3].filled(self.fill_value[3]))
                Pil.merge("RGBA", (pil_r, pil_g, pil_b, pil_a)).save(filename)
            else:
                pil_r = Pil.fromarray(channels[0].filled(0))
                pil_g = Pil.fromarray(channels[1].filled(0))
                pil_b = Pil.fromarray(channels[2].filled(0))

                mask = (np.ma.getmaskarray(channels[0]) | 
                        np.ma.getmaskarray(channels[1]) | 
                        np.ma.getmaskarray(channels[2]) |
                        np.ma.getmaskarray(channels[3]))

                alpha = np.where(mask, 0, channels[3])
                pil_a = Pil.fromarray(alpha)

                Pil.merge("RGBA", (pil_r, pil_g, pil_b, pil_a)).save(filename)
                    

    def putalpha(self, alpha):
        """Adds an *alpha* channel to the current image, or replaces it with
        *alpha* if it already exists.
        """
        if(not self.mode.endswith("A")):
            self.convert(self.mode+"A")
        self.channels[-1] = alpha
        
    def rgb2ycbcr(self):
        """Convert the image from RGB mode to YCbCr."""

        if not (self.mode == "RGB" or
                self.mode == "RGBA"):
            raise NameError("Image not in RGB mode.")

        kb_ = 0.114
        kr_ = 0.299
        
        r__ = self.channels[0]
        g__ = self.channels[1]
        b__ = self.channels[2]
        
        y__ = kr_ * r__ + (1 - kr_ - kb_) * g__ + kb_ * b__
        cb_ = 1 / (2 * (1 - kb_)) * (b__ - y__)
        cr_ = 1 / (2 * (1 - kr_)) * (r__ - y__)
        
        self.channels[0] = y__
        self.channels[1] = cb_
        self.channels[2] = cr_
        
        if(self.mode == "RGB"):
            self.mode = "YCbCr"
        else:
            self.mode = "YCbCrA"
        
    def ycbcr2rgb(self):
        """Convert the image from YCbCr mode to RGB.""" 

        if not (self.mode == "YCbCr" or
                self.mode == "YCbCrA"):
            raise NameError("Image not in YCbCr mode.")

        kb_ = 0.114
        kr_ = 0.299
        
        y__ = self.channels[0]
        cb_ = self.channels[1]
        cr_ = self.channels[2]

        
        r__ = 2 * cr_ / (1 - kr_) + y__
        b__ = 2 * cb_ / (1 - kb_) + y__
        g__ = (y__ - kr_ * r__ - kb_ * b__) / (1 - kr_ - kb_)
        
        self.channels[0] = r__
        self.channels[1] = g__
        self.channels[2] = b__
        
        if(self.mode == "YCbCr"):
            self.mode = "RGB"
        else:
            self.mode = "RGBA"


    def convert(self, mode):
        """Convert the current image to the given *mode*. See :class:`Image`
        for a list of available modes.
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


            pal = np.ma.array(self.channels[0])
            alpha = np.ma.array(self.channels[-1])
            if self.mode == "PA":
                for i in range(len(self.channels), 4):
                    self.channels.append(np.ma.zeros(np.ma.shape(pal)))
                    self.channels[i].mask = pal.mask

                self.channels[3] = alpha
            else:
                for i in range(len(self.channels), 3):
                    self.channels.append(np.ma.zeros(np.ma.shape(pal)))
                    self.channels[i].mask = pal.mask

            

            rcdf = np.zeros(len(self.palette))
            gcdf = np.zeros(len(self.palette))
            bcdf = np.zeros(len(self.palette))

            for i in range(len(self.palette)):
                rcdf[i] = self.palette[i][0]
                gcdf[i] = self.palette[i][1]
                bcdf[i] = self.palette[i][2]

            self.channels[0] = \
                np.ma.array(np.interp(pal,
                                      np.arange(len(self.palette)),
                                      rcdf),
                            mask = pal.mask)
            self.channels[1] = \
                np.ma.array(np.interp(pal,
                                      np.arange(len(self.palette)),
                                      gcdf),
                            mask = pal.mask)
            self.channels[2] = \
                np.ma.array(np.interp(pal,
                                      np.arange(len(self.palette)),
                                      bcdf),
                            mask = pal.mask)

            self.mode = mode

        elif((self.mode == "RGB" and
            mode == "YCbCr") or
           (self.mode == "RGBA" and
            mode == "YCbCrA")):
            
            self.rgb2ycbcr()

        elif((self.mode == "YCbCr" and
              mode == "RGB") or
             (self.mode == "YCbCrA" and
              mode == "RGBA")):
            
            self.ycbcr2rgb()

        else:
            raise NameError("Conversion from %s to %s not implemented !"
                            %(self.mode,mode))
            
    def clip(self, channels = True):
        """Limit the values of the array to the default [0,1] range. *channels*
        says which channels should be clipped."""
        if not (isinstance(channels, (tuple, list))):
            channels = [channels]*len(self.channels)
            
        for i in range(len(self.channels)):
            if channels[i]:
                self.channels[i] = np.ma.clip(self.channels[i], 0.0, 1.0)

    def resize(self, shape):
        """Resize the image to the given *shape* tuple, in place.
        """
        factor = self.channels[0] * 1.0 / shape[0]

        if int(factor) != factor:
            raise ValueError("Resize not of integer factor!")

        i = 0
        for chn in self.channels:
            chn = chn.repeat([factor]*chn.shape[0], axis = 0)
            self.channels[i] = chn.repeat([factor]*chn.shape[1], axis = 1)
            i = i + 1

        self.height = self.channels[0].shape[0]
        self.width = self.channels[0].shape[1]
        self.shape = self.channels[0].shape

    def replace_luminance(self, luminance):
        """Replace the Y channel of the image by the array *luminance*. If the
        image is not in YCbCr mode, it is converted automatically to and
        from that mode.
        """
        if (luminance.shape != self.channels[0].shape):
            if ((luminance.shape[0] * 1.0 / luminance.shape[1]) ==
                (self.channels[0].shape[0] * 1.0 / self.channels[0].shape[1])):
                if luminance.shape[0] > self.channels[0].shape[0]:
                    self.resize(luminance.shape)
                else:
                    raise NameError("Luminance smaller than the image !")
            else:
                raise NameError("Not the good shape !")
        
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
        *inverse* (see :meth:`Image.invert`), *gamma* (see
        :meth:`Image.gamma`), and *stretch* (see :meth:`Image.stretch`).
        """
        self.invert(inverse)
        self.gamma(gamma)
        self.stretch(stretch)
        
    def gamma(self, gamma = 1.0):
        """Apply gamma correction to the channels of the image. If *gamma* is a
        tuple, then is should have as many elements as the channels of the
        image, and the gamma correction is applied elementwise. If *gamma* is a
        number, the same gamma correction is applied on every channel, if there
        are several channels in the image. The behaviour of :func:`gamma` is
        undefined outside the normal [0,1] range of the channels.
        """
        if gamma == 1.0:
            return
        if (isinstance(gamma, (tuple, list))):
            for i in range(len(gamma)):
                self.channels[i] = np.where(self.channels[i] >= 0,
                                            self.channels[i] ** (1 / gamma[i]),
                                            self.channels[i])
        else:
            i = 0
            for chn in self.channels:
                self.channels[i] = np.where(chn >= 0,
                                            chn ** (1 / gamma),
                                            chn)
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
        if((isinstance(stretch, tuple) or
            isinstance(stretch,list)) and
           len(stretch) == 2):
            for i in range(len(self.channels)):
                self.stretch_linear(i, cutoffs = stretch)
        elif stretch == "linear":
            for i in range(len(self.channels)):
                self.stretch_linear(i)
        elif stretch == "histogram":
            for i in range(len(self.channels)):
                self.stretch_hist_equalize(i)
        elif(stretch == "crude" or
             stretch == "crude-stretch"):
            for i in range(len(self.channels)):
                self.crude_stretch(i)

    def invert(self, invert = False):
        """Inverts all the channels of a image according to *invert*. If invert
        is a tuple or a list, elementwise invertion is performed, otherwise all
        channels are inverted if *invert* is true.
        """
        if(isinstance(invert, tuple) or
           isinstance(invert, list)):
            i = 0
            for chn in self.channels:
                if(invert[i]):
                    self.channels[i] = 1.0 - chn
                i = i + 1
        elif(invert):
            i = 0
            for chn in self.channels:
                self.channels[i] = 1.0 - chn
                i = i + 1
         
   
    def stretch_hist_equalize(self, ch_nb):
        """Stretch the current image's colors by performing histogram
        equalization on channel *ch_nb*.
        """
        com.msgwrite_log("INFO",
                         "Perform a histogram equalized contrast stretch.",
                         moduleid=MODULE_ID)

        arr = self.channels[ch_nb]

        nwidth = 2048.0

        carr = arr.compressed()

        imhist, bins = np.histogram(carr, nwidth, normed=True)
        cdf = imhist.cumsum() - imhist[0]
        cdf = cdf / cdf[-1]

        res = np.ma.empty_like(arr)
        res.mask = arr.mask
        res[~res.mask] = np.interp(carr, bins[:-1], cdf)

        self.channels[ch_nb] = res

    def stretch_linear(self, ch_nb, cutoffs=(0.005, 0.005)):
        """Stretch linearly the contrast of the current image on channel
        *ch_nb*, using *cutoffs* for left and right trimming.
        """
        com.msgwrite_log("INFO",
                         "Perform a linear contrast stretch.",
                         moduleid=MODULE_ID)

        nwidth = 2048.0


        arr = self.channels[ch_nb]

        carr = arr.compressed()
        hist, bins = np.histogram(carr, nwidth, new = True)

        ndim = carr.size

        left = 0
        hist_sum = 0.0
        i = 0
        while i <= nwidth and hist_sum < cutoffs[0]*ndim:
            hist_sum = hist_sum + hist[i]
            i = i + 1

        left = bins[i-1]

        right = 0
        hist_sum = 0.0
        i = nwidth - 1
        while i >= 0 and hist_sum < cutoffs[1]*ndim:
            hist_sum = hist_sum + hist[i]
            i = i - 1

        right = bins[i+1]
        delta_x = (right - left)
        com.msgwrite_log("INFO",
                         "Interval: left=%f,right=%f width=%f"%
                         (left,right,delta_x),
                         moduleid=MODULE_ID)
        if delta_x > 0.0:
            self.channels[ch_nb] = np.ma.array((arr - left) / delta_x, 
                                               mask = arr.mask)
        else:
            self.channels[ch_nb] = np.ma.zeros(arr.shape)
            com.msgwrite_log("WARNING",
                             "Unable to make a contrast stretch!",
                             moduleid=MODULE_ID)


    def crude_stretch(self, ch_nb, min_stretch = None, max_stretch = None):
        """Perform simple linear stretching (without any cutoff) on the channel
        *ch_nb* of the current image and normalize to the [0,1] range."""

        if(min_stretch is None):
            min_stretch = self.channels[ch_nb].min()
        if(max_stretch is None):
            max_stretch = self.channels[ch_nb].max()

        self.channels[ch_nb] = ((self.channels[ch_nb] - min_stretch) * 1.0 / 
                                (max_stretch - min_stretch))
