def gamma_corr(g,arr):
    """
    Perform gamma correction *g* to an array *arr*, which is assumed to be
    in the range [0,255], and return the resulting array (same range).
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
