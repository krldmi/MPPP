from seviri_lonlat import *

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print "USAGE: %s <lon> <lat>"%(sys.argv[0])
        sys.exit(0)
    else:
        import string
        lon = string.atof(sys.argv[1])
        lat = string.atof(sys.argv[2])

    line,col = lonlat2linecol(lon,lat)
    print "lon,lat -> line,col: ",lon,lat,line,col



