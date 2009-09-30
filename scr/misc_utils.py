
def UTC_time_from_string(string):
    """Converts a string of the shape YYYYMMDDhhmm to utc time
    """
    import time
    return time.mktime(time.strptime(string,"%Y%m%d%H%M"))-time.timezone

def ensure_dir(f):
    """Checks if the dir of f exists, otherwise create it.
    """
    import os
    d = os.path.dirname(f)
    if not os.path.isdir(d):
        os.makedirs(d)

def extrema(a):
    return a.min(),a.max()
