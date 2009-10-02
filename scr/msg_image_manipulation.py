import numpy
import msg_communications

MODULE_ID = "MSG IMAGE PROCESSING"

def gamma_corr(g,arr):
    """
    Perform gamma correction *g* to an array *arr*, which is assumed
    to be in the range [0,255], and return the resulting array (same
    range). The values of the array are also stretched to range.
    """

    # Assume array to be between 0 and 255: Put the array between 0 and 1:

    retv = (arr/255.0)**(1.0/g)

    maxarr= retv.max()
    minarr= retv.min()
    
    msg_communications.msgwrite_log("INFO","minarr,maxarr = ",minarr,maxarr,moduleid=MODULE_ID)
    
    if maxarr-minarr > 0.001:
        retv = (255*(retv-minarr)/(maxarr-minarr)).astype(numpy.uint8)
    else:
        msg_communications.msgwrite_log("WARNING","maxarr-minarr <=0.001",maxarr-minarr,moduleid=MODULE_ID)
        retv = numpy.zeros(retv.shape,numpy.uint8)
    
    return retv


def stretch_hist_equalize(arr):
    """Stretch a monochromatic masked array *arr* by performing
    histogram equalization. The stretched array is returned.
    """
    msg_communications.msgwrite_log("INFO",
                                    "Perform a histogram equalized contrast stretch of one image layer",moduleid=MODULE_ID)

    nwidth=255.0

    imhist,bins = numpy.histogram(arr.compressed(),nwidth,normed=True)
    cdf = imhist.cumsum() - imhist[0]
    cdf = 255.0 * cdf / cdf[-1]
    
    res = numpy.ma.empty_like(arr)
    res.mask = arr.mask
    res[~res.mask] = numpy.interp(arr.compressed(),bins[:-1],cdf)
    
    return res

def stretch_linear(arr,cutoffs=[0.005,0.005]):
    """Stretch linearly the contrast of a monochromatic masked array
    *arr*, using *cutoffs* for left and right trimming.
    """
    msg_communications.msgwrite_log("INFO","Perform a linear contrast stretch of one image layer",moduleid=MODULE_ID)
    import Scientific.Statistics.Histogram
    import numpy.oldnumeric as Numeric

    nwidth=255
    
    hist,bins = numpy.histogram(arr.compressed(), nwidth)

    ndim = arr.compressed().size

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
        res =  numpy.ma.empty_like(arr)
        res.mask = arr.mask
	res = 255 * (arr - left) / dx
	res = numpy.where(res < 255, res, 255)
	res = numpy.where(res > 0, res, 0)
	res = res.astype(numpy.uint8)
    else:
	res = numpy.zeros(arr.shape,numpy.uint8)
	msg_communications.msgwrite_log("WARNING","Unable to make a contrast stretch!",moduleid=MODULE_ID)

    return res

def crude_stretch(arr, norm = 255, min = None, max = None):
    """Perform simple linear stretching (without any cutoff) and normalize."""

    if(min is None):
        min = arr.min()
    if(max is None):
        max = arr.max()

    res = (arr-min) * (norm * 1.0)/(max - min)
    res = numpy.where(res > norm, norm, res)
    res = numpy.where(res < 0, 0, res)

    return res.astype(numpy.uint8)
