import os
import tempfile
import Image as PilImage
import numpy as np
import shutil
import string
import misc_utils
import msg_communications

MODULE_ID = "IMAGE"

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
    shape = None
    """Shape (dimensions) of the image."""
    
    def __init__(self,channels, mode = "L",range = None, 
                 fill_value = None, palette = None):
        self.mode = mode
        self.fill_value = fill_value
        self.channels = []
        self.palette = palette
        if(isinstance(channels,tuple) or
           isinstance(channels,list)):
            self.height = channels[0].shape[0]
            self.width = channels[0].shape[1]
            self.shape = channels[0].shape

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
            self.shape = channels.shape

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
        :meth:`save` and :meth:`double_save`.
        """
        misc_utils.ensure_dir(filename)

        file,ext = os.path.splitext(filename)
        path,file = os.path.split(filename)
        trash,tmpfilename = tempfile.mkstemp(suffix = ext,
                                             dir = path)
        self.save(tmpfilename)
        os.rename(tmpfilename,filename)
        
    def double_save(self,local_filename,remote_filename):
        """Save the current image to *local_filename*, then copy it to
        *remote_filename*, using a temporary file at first, then renaming it to
        the final remote filename. See also :meth:`save` and
        :meth:`secure_save`.
        """
        self.save(local_filename)

        misc_utils.ensure_dir(remote_filename)

        file,ext = os.path.splitext(remote_filename)
        path,file = os.path.split(remote_filename)
        trash,tmpfilename = tempfile.mkstemp(suffix = ext,
                                             dir = path)
        shutil.copy(local_filename,tmpfilename)
        os.rename(tmpfilename,remote_filename)


    def save(self, filename):
        """Save the image to the given *filename*. See also
        :meth:`double_save` and :meth:`secure_save`.
        """
        file_tuple = os.path.splitext(filename)

        channels = self._finalize()

        misc_utils.ensure_dir(filename)

        if(self.mode == "L"):
            misc_utils.ensure_dir(filename)
            if self.fill_value is not None:
                im = PilImage.fromarray(channels[0].filled(self.fill_value))
                im.save(filename)
            else:
                l = PilImage.fromarray(channels[0].filled(0))
                alpha = np.zeros(channels[0].shape,np.uint8)
                mask = np.ma.getmaskarray(channels[0])
                alpha = np.where(mask, alpha, 255)
                a = PilImage.fromarray(alpha)
                
                PilImage.merge("LA",(l,a)).save(filename)

        elif(self.mode == "RGB"):
            misc_utils.ensure_dir(filename)
            if self.fill_value is not None:
                r = PilImage.fromarray(channels[0].filled(self.fill_value[0]))
                g = PilImage.fromarray(channels[1].filled(self.fill_value[1]))
                b = PilImage.fromarray(channels[2].filled(self.fill_value[2]))
                PilImage.merge("RGB",(r,g,b)).save(filename)
            else:
                r = PilImage.fromarray(channels[0].filled(0))
                g = PilImage.fromarray(channels[1].filled(0))
                b = PilImage.fromarray(channels[2].filled(0))

                alpha = np.zeros(channels[0].shape,np.uint8)
                mask = (np.ma.getmaskarray(channels[0]) | 
                        np.ma.getmaskarray(channels[1]) | 
                        np.ma.getmaskarray(channels[2]))
                alpha = np.where(mask,alpha, 255)
                a = PilImage.fromarray(alpha)

                PilImage.merge("RGBA",(r,g,b,a)).save(filename)

        elif(self.mode == "RGBA"):
            misc_utils.ensure_dir(filename)
            if self.fill_value is not None:
                r = PilImage.fromarray(channels[0].filled(self.fill_value[0]))
                g = PilImage.fromarray(channels[1].filled(self.fill_value[1]))
                b = PilImage.fromarray(channels[2].filled(self.fill_value[2]))
                a = PilImage.fromarray(channels[3].filled(self.fill_value[3]))
                PilImage.merge("RGBA",(r,g,b,a)).save(filename)
            else:
                r = PilImage.fromarray(channels[0].filled(0))
                g = PilImage.fromarray(channels[1].filled(0))
                b = PilImage.fromarray(channels[2].filled(0))

                mask = (np.ma.getmaskarray(channels[0]) | 
                        np.ma.getmaskarray(channels[1]) | 
                        np.ma.getmaskarray(channels[2]) |
                        np.ma.getmaskarray(channels[3]))

                alpha = np.where(mask, 0, channels[3])
                a = PilImage.fromarray(alpha)

                PilImage.merge("RGBA",(r,g,b,a)).save(filename)
                    

    def putalpha(self, alpha):
        """Adds an *alpha* channel to the current image, or replaces it with
        *alpha* if it already exists.
        """
        if(not self.mode.endswith("A")):
            self.convert(self.mode+"A")
        self.channels[-1] = alpha
        

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
            

    def resize(self,shape):
        """Resize the image to the given *shape* tuple, in place.
        """
        factor = channels[0] * 1.0 / shape[0]

        if int(factor) != factor:
            raise ValueError("Resize not of integer factor!")

        i = 0
        for ch in self.channels:
            ch = ch.repeat([factor]*ch.shape[0],axis = 0)
            self.channels[i] = ch.repeat([factor]*a.shape[1],axis = 1)
            i = i + 1

        self.height = self.channels[0].shape[0]
        self.width = self.channels[0].shape[1]
        self.shape = self.channels[0].shape

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
                    raise NameError("Luminance replacement: luminance smaller than the image !")
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
        *inverse* (see :meth:`Image.invert`), *gamma* (see
        :meth:`Image.gamma`), and *stretch* (see :meth:`Image.stretch`).
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
            for i in range(len(self.channels)):
                self.stretch_linear(i,cutoffs = stretch)
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
            for ch in self.channels:
                if(invert[i]):
                    self.channels[i] = 1.0 - ch
                i = i + 1
        elif(invert):
            i = 0
            for ch in self.channels:
                self.channels[i] = 1.0 - ch
                i = i + 1
         
   
    def stretch_hist_equalize(self,ch_nb):
        """Stretch the current image's colors by performing histogram
        equalization on channel *ch_nb*.
        """
        msg_communications.msgwrite_log("INFO",
                                        "Perform a histogram equalized contrast stretch of one image layer",moduleid=MODULE_ID)

        arr = self.channels[ch_nb]

        nwidth=2048.0

        carr = arr.compressed()

        imhist,bins = np.histogram(carr,nwidth,normed=True)
        cdf = imhist.cumsum() - imhist[0]
        cdf = cdf / cdf[-1]

        res = np.ma.empty_like(arr)
        res.mask = arr.mask
        res[~res.mask] = np.interp(carr,bins[:-1],cdf)

        self.channels[ch_nb] = res

    def stretch_linear(self,ch_nb, cutoffs=(0.005,0.005)):
        """Stretch linearly the contrast of the current image on channel
        *ch_nb*, using *cutoffs* for left and right trimming.
        """
        msg_communications.msgwrite_log("INFO","Perform a linear contrast stretch of one image layer",moduleid=MODULE_ID)

        nwidth=2048.0

        arr = self.channels[ch_nb]

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
            self.channels[ch_nb] = np.ma.array((arr - left) / dx, mask = arr.mask)
        else:
            self.channels[ch_nb] = np.ma.zeros(arr.shape)
            msg_communications.msgwrite_log("WARNING","Unable to make a contrast stretch!",moduleid=MODULE_ID)


    def crude_stretch(self, ch_nb, min = None, max = None):
        """Perform simple linear stretching (without any cutoff) on the channel
        *ch_nb* of the current image and normalize to the [0,1] range."""

        if(min is None):
            min = self.channels[ch_nb].min()
        if(max is None):
            max = self.channels[ch_nb].max()

        self.channels[ch_nb] = (self.channels[ch_nb] - min) * 1.0 / (max - min) 
