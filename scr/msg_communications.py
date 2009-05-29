ncwd = 0
    
TRUE = 1
FALSE = 0

# --------------------------------------------------------
def msgwrite_log(level, txt, *param,**options):
    """
    Write log information with time stamp.

    @type level: String
    @param level: Log information type (e.g. INFO, DEBUG,...) 
    @type txt: String
    @param txt: The text to be logged
    @type param: List
    @param param: List of optional input parameters
    @type options: Dictionary
    @param options: Dictionary of optional parameters
    @keyword module_id: The module id as a string
    @return: None
    """
    import time,sys

    if options.has_key("moduleid") and options["moduleid"]!=None:
        mid=options["moduleid"]
    else:
        mid=MODID
        
    now = time.time()
    time_ = time.gmtime(now)
    tdate = "%.4d/%.2d/%.2d %.2d:%.2d:%.2d"%(time_[0],time_[1],
					     time_[2],time_[3],
					     time_[4],time_[5])

    str = "[%s: %s : %s] %s"%(level,tdate,mid,txt)
    for p in param:
        str = "%s %s"%(str, p)
	
    tmp = sys.stdout
    sys.stdout=sys.stderr
    print str
    sys.stdout = tmp
    
    return
    
# ---------------------------------------------------------------
def retrieve(ftp, destdir, names):
    """
    Retrieve data from ftp connection.
    Goes down in every sub-directory iteratively.

    @type ftp: ftp instance
    @param ftp: ftp instance of the open ftp-connection
    @type destdir: String
    @param destdir: Name of directory where to download the data
    @type names: List 
    @param names: List of filenames to be retrieved from current directory
    @return: None
    """
    import os, string
    msgwrite_log("INFO","Destination: ",destdir,moduleid="MSG_FTP")
    if not os.path.exists(destdir):
	os.mkdir(destdir)
   
    for name in names:
	if name == "" or len(string.split(name,":"))==2:
	    break

	msgwrite_log("INFO","Retrieve file: ",name,moduleid="MSG_FTP")
	local_name = destdir + name
	fd = open(local_name, "w")
	ftp.retrbinary("RETR " + name, fd.write, 1024)
	fd.close()

    subdirs = []
    for name in names:
	ll = string.split(name,":")
	if len(ll) == 2:
	    subdirs.append(ll[0])

    if len(subdirs) == 0:
	ftp.cwd("../")
	return
    
    #print "Sub dirs: ",subdirs

    for dir in subdirs:
	ftp.cwd(dir+"/")
	names = ftp.nlst("*")
	path = destdir + dir + "/"
	retrieve(ftp,path,names)

    ftp.cwd("../")

# ---------------------------------------------------------------
def putall(ftp, localdir, ftpdir, flist, time_thr, delete=TRUE):
    """
    Function to put data over an ftp connection.

    @param ftp: ftp instance holding the ftp-connection
    @param localdir: Directory path of local area (this side of the connection)
    @param ftpdir: Directory path of destination area (the other side of connection)
    @param flist: List of file names
    @param time_thr: Threshold (sec since 1970) defining which files to consider. Files older than time_thr will not be considered
    @param delete: Switch = TRUE or FALSE. If true all files that have not been overwritten will be cleaned.
    @return: None
    """
    import os, glob
    import stat

    msgwrite_log("INFO","Source directory: ",localdir,moduleid="MSG_FTP")
    
    try:
        names_ftpsite = ftp.nlst()
    except:
        names_ftpsite = []
        pass

    print "FILES on ftp server:"
    print names_ftpsite
    
    names = []
    for file in flist:
        name = os.path.split(file)[1]
	names.append(name)

        if os.path.islink(file): continue
        if os.path.isdir(file): continue
        
        time_of_lastmod = os.stat(file)[stat.ST_MTIME]
        # Don't consider files older than specified by the time window:
        if time_of_lastmod < time_thr:
            msgwrite_log("INFO","File %s is older than %d: Don't bother..."%(file,time_thr),moduleid="MSG_FTP")
            continue
        else:
            #print file, name
            pass
	
	#print "Clean file: ",name,
	#try:
	#    ftp.sendcmd("dele %s"%name)
	#except:
	#    pass
	    
	#print "Put file: ",name
	local_name = file
	fd = open(local_name, "r")
	ftp.storbinary("STOR " + name, fd, 1024)
	fd.close()

    if delete==TRUE:
        # Clean the files which have not been overwritten:
        for name in names_ftpsite:
            if name in names:
                msgwrite_log("INFO","File %s was just put there..."%name,moduleid="MSG_FTP")
                continue
            else:
                try:
                    msgwrite_log("INFO","delete file %s"%name,moduleid="MSG_FTP")
                    ftp.sendcmd("dele %s"%name)
                except:
                    msgwrite_log("WARNING","Couldn't delete file %s"%name,moduleid="MSG_FTP")
                    pass

    subdirs = []
    for file in flist:
	name = os.path.split(file)[1]
        time_of_lastmod = os.stat(file)[stat.ST_MTIME]
        # Don't consider files older than specified by the time window:
        if time_of_lastmod < time_thr:
            msgwrite_log("INFO","Directory %s is older than %d: Don't bother..."%\
		      (file,time_thr),moduleid="MSG_FTP")
            continue

	if os.path.isdir(file):
	    name = os.path.split(file)[1]
	    subdirs.append(name)

    if len(subdirs) == 0:
	ftp.cwd("../")
	return
    
    #print "Sub dirs: ",subdirs

    for dir in subdirs:
	path = ftpdir+"/"+dir
	try:
	    ftp.cwd(path+"/")
	except:
	    msgwrite_log("INFO","Make directory:",moduleid="MSG_FTP")
	    ftp.mkd(path)
	    ftp.cwd(path+"/")

	flist = glob.glob(localdir+dir+"/*")
	msgwrite_log("INFO","Number of file in sub directory: %d"%len(flist),moduleid="MSG_FTP")
	putall(ftp,localdir+dir+"/",path,flist,time_thr,delete)

    ftp.cwd("../")

# ------------------------------------------------------------

