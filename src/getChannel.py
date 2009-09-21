import os

os.environ['SAFNWC'] = os.environ['HOME']+"/usr/src/msg"
os.environ['SAFNWC_BIN'] = os.environ['SAFNWC']+"/bin"
os.environ['SAFNWC_LIB'] = os.environ['SAFNWC']+"/bin"
os.environ['PATH'] = os.environ['PATH']+":"+os.environ['SAFNWC_BIN']
os.environ['LD_LIBRARY_PATH'] = os.environ['LD_LIBRARY_PATH']+":"+os.environ['SAFNWC_LIB']
os.environ['BUFR_TABLES'] = os.environ['SAFNWC']+"/src/bufr_000360/bufrtables/"
os.environ['LOCAL_DEFINITION_TEMPLATES'] = os.environ['SAFNWC']+"/src/gribex_000360/gribtemplates/"

import Image
import numpy
import msg


def normalizeArray(a,maxval):
    return numpy.array(numpy.round(((a-numpy.amin(a))/(numpy.amax(a)-numpy.amin(a)))*maxval),numpy.uint8)

def getComponent(channel, component, inverted=False):
    if(component not in channel):
        return None

    comp = numpy.array(channel[component])
    mask = channel["MASK"]

    if(inverted):
        comp[numpy.logical_not(mask)]=numpy.amax(comp[mask])    
        comp=numpy.amax(comp)-comp
    else:
        comp[numpy.logical_not(mask)]=numpy.amin(comp[mask])    

    return comp

def getRadiance(channel, inverted=False):
    return getComponent(channel,"RAD",inverted)

def getReflectance(channel, inverted=False):
    return getComponent(channel,"REFL",inverted)

def getBT(channel, inverted=False):
    return getComponent(channel,"BT",inverted)

def getMask(channel):
    return channel["MASK"]


a=msg.getChannel("200909141145","safnwc_EuropeCanary.cfg","1")

rad = getRadiance(a)

im = Image.new('L',rad.shape)

im = Image.fromarray(normalizeArray(rad,255))

#im.show()


ch1 = msg.getChannel("200909141145","safnwc_EuropeCanary.cfg","1")
ch2 = msg.getChannel("200909141145","safnwc_EuropeCanary.cfg","2")
ch9 = msg.getChannel("200909141145","safnwc_EuropeCanary.cfg","9")
ch12 = msg.getChannel("200909141145","safnwc_EuropeCanary.cfg","12")

im1 = Image.fromarray(normalizeArray(getReflectance(ch1),255))
im2 = Image.fromarray(normalizeArray(getReflectance(ch2),255))
im9i = Image.fromarray(normalizeArray(getBT(ch9,True),255))
im12 = Image.fromarray(normalizeArray(getReflectance(ch12),255))

visir = Image.merge('RGB',(im1,im2,im9i));
hrv = im12
v = visir.convert('YCbCr').split()
im = Image.merge('YCbCr',(hrv,v[1].resize(hrv.size),v[2].resize(hrv.size))).convert('RGB')

im.show()
