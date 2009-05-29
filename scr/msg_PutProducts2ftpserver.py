from msg_communications import *

# ---------------------------------------------------------
if __name__ == "__main__":
    """
    Script to handle the transfer of NWCSAF-MSG (possibly post-processed)
    products to external ftp-site or for ingestion into Prosat
    Is called by msg_PutProducts2ftpserver.ksh
    """
    import ftplib
    import glob
    import time

    user="adybbroe"
    psw="adyton2"
    ftp_site = "ftp.smhi.se"

    time_thr = time.time()
    #time_thr = time_thr - 3600
    time_thr = time_thr - 6*3600
    
    # Open and login on ftp site
    ftp = ftplib.FTP(ftp_site)
    ftp.login(user,psw)
    home_dir=ftp.pwd()

    local_dir = "/local_disk/data/Meteosat/RGBs"
    remote_dir = "%s/TillPia/RGB"%home_dir

    #flist = glob.glob("%s/*scan*.png"%(local_dir))
    flist = glob.glob("%s/*euro4*.png"%(local_dir))
    flist = [s for s in flist if s.find("thumbnail")<0]
    #flist = [s for s in flist if s.find("euro")<0]
    #flist = [s for s in flist if s.find("sswe")<0]
    #flist = [s for s in flist if s.find("nswe")<0]
    
    ftp.cwd(remote_dir)
    putall(ftp,local_dir,remote_dir,flist,time_thr,1)

    local_dir = "/local_disk/data/Meteosat/MesanX"
    #flist = glob.glob("%s/*scan*.png"%(local_dir))
    flist = glob.glob("%s/*euro4*.png"%(local_dir))
    flist = [s for s in flist if s.find("thumbnail")<0]
    #flist = [s for s in flist if s.find("cloudtype_vv2")<0]
    remote_dir = "%s/TillPia/SAF"%home_dir
    ftp.cwd(remote_dir)
    remote_dir=ftp.pwd()
    putall(ftp,local_dir,remote_dir,flist,time_thr,1)
    
    ftp.quit()
