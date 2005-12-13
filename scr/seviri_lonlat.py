"""

#SCAN PROPERTIES
PROD_DIRECTION   S
#in seconds          
SCAN_DELTA_T        0.0
#in milliseconds
SCAN_RATE         600.0     
"""

#Spacecraft
MSG = "MSG1"

#SEVIRI1.5 image projection longitude
PRJ_REF_LONG = 0

#Nominal sub satellite point
SAT_REF_LONG = -3.4

#Number of lines per segment
SEGMENT_LINES = 464

REF_ALT        =         35785.831
NB_COLS        =         3712 
NB_LINES       =         3712 
NB_SLOTS       =         96
TIME_SLOT1     =          900
NB_HRV_DETECTORS =       9
NB_SEV_DETECTORS =       3
SPIN_RATE        =       600 

# VISIR NAVIGATION COEFFICIENTS
COFF = 1856
LOFF = 1856
CFAC = 13642337
LFAC = 13642337

# HRV NAVIGATION COEFFICIENTS
COFF_HRV = 5568
LOFF_HRV = 5568
CFAC_HRV = 40927014
LFAC_HRV = 40927014

H =       42164.0    # Distance between MSG and centre of earth
R_EQ =    6378.1690  # Equator radius for an idealized earth
R_POL=    6356.5838  # Equator polar radius

import math
RAD2DEG = 180./math.pi
DEG2RAD = math.pi/180.

# ----------------------------------------------------------------------------
# Calculations as described in LRIT/HRIT Global Specification section 4.4.3.2
def linecol2lonlat(line,col):
    y=(line-LOFF)*math.pow(2,16)/LFAC * DEG2RAD
    cosy=math.cos(y)
    siny=math.sin(y)
    x=(col - COFF)*math.pow(2,16)/CFAC * DEG2RAD
    cosx=math.cos(x)
    sinx=math.sin(x)

    aux=42164*cosx*cosy
    aux2=cosy*cosy+1.006803*siny*siny
    #sd=math.sqrt(aux*aux-aux2*1737121856)
    sd=math.sqrt(abs(aux*aux-aux2*1737121856))
    sn=(aux-sd)/aux2
    s1=42164 - sn*cosx*cosy
    s2=sn*sinx*cosy
    s3= -sn*siny
    sxy=math.sqrt(s1*s1+s2*s2)

    longitude=math.atan(s2/s1)*RAD2DEG+PRJ_REF_LONG
    latitude=math.atan(1.006803*s3/sxy)*RAD2DEG

    if longitude > 180:
        longitude -=360
    if longitude < -180:
        longitude +=360

    return longitude,latitude
    

# ----------------------------------------------------------------------------
def lonlat2linecol(lon,lat):
    lat=lat*DEG2RAD
    lon=lon*DEG2RAD
    sub_long_rad = PRJ_REF_LONG * DEG2RAD

    c_lat=math.atan(0.993243*math.tan(lat))
    cosc_lat=math.cos(c_lat)
    r_pol2= R_POL*R_POL
    r_eq2 = R_EQ*R_EQ
    rl=R_POL/(math.sqrt(1-((r_eq2-r_pol2)/r_eq2)*cosc_lat*cosc_lat))
    r1=H-rl*cosc_lat*math.cos(lon-sub_long_rad)
    r2=-rl*cosc_lat*math.sin(lon-sub_long_rad)
    r3=rl*math.sin(c_lat);
    rn=math.sqrt(r1*r1+r2*r2+r3*r3)

    # compute variables useful to check if pixel is visible from the satellite
    ad2 = r1*r1 + r2*r2 + r3*r3*r_eq2 / r_pol2
    bd = H*r1
    cd = H*H - r_eq2
    delta2 = bd*bd-ad2*cd
    halfsom = bd*rn/ad2
 
    if delta2 >= 0. and rn <= halfsom:
        # Intermediate coordinates
        #x=math.atan(-r2/r1)
        #y=math.asin(-r3/rn)
        x=math.atan(-r2/r1)*RAD2DEG
        y=math.asin(-r3/rn)*RAD2DEG
        #print "x,y (degrees): ",x,y
        
        xc=COFF + x*math.pow(2,-16)*CFAC
        yl=LOFF + y*math.pow(2,-16)*LFAC

        # Image coordinates calculation 
        xc = int(round(xc))
        yl = int(round(yl))        
    else:
        print "Coordinates can not be seen from the satellite"
        return -9999,-9999
    
    return yl,xc

# ----------------------------------------------------------------------------
def xy2linecol(x,y):
    col=COFF + int(round(x*math.pow(2,-16)*CFAC))
    line=LOFF + int(round(y*math.pow(2,-16)*LFAC))
    return line,col

# ----------------------------------------------------------------------------
def linecol2xy(line,col):
    y=(line-LOFF)*math.pow(2,16)/LFAC
    x=(col - COFF)*math.pow(2,16)/CFAC
    return x,y


# ----------------------------------------------------------------------------
def do_test():
    lon,lat = 0.0,0.0
    line,col=lonlat2linecol(lon,lat)
    print "lon,lat -> line,col: ",lon,lat,line,col
    lon,lat = linecol2lonlat(line,col)
    print "line,col -> lon,lat: ",line,col,lon,lat

    lon,lat = 0.0,50.0
    line,col=lonlat2linecol(lon,lat)
    print "lon,lat -> line,col: ",lon,lat,line,col
    lon,lat = linecol2lonlat(line,col)
    print "line,col -> lon,lat: ",line,col,lon,lat

    lon,lat = 20.0,50.0
    line,col=lonlat2linecol(lon,lat)
    print "lon,lat -> line,col: ",lon,lat,line,col
    lon,lat = linecol2lonlat(line,col)
    print "line,col -> lon,lat: ",line,col,lon,lat

    return

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    do_test()





