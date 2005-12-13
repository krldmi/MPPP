from seviri_lonlat import *

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print "USAGE: %s <line> <col>"%(sys.argv[0])
        sys.exit(0)
    else:
        import string
        line = string.atoi(sys.argv[1])
        col = string.atoi(sys.argv[2])

    lon,lat = linecol2lonlat(line,col)
    print "line,col -> lon,lat: ",line,col,lon,lat


