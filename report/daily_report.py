from products import PRODUCTS
import os
import datetime
import glob
import pickle

import time_utils
import msgpp_config
from msg_communications import *

MODULE_ID = "daily_report"

HRIT_IN="/data/24/saf/geo_in"

MAIL_ADDRESS_FROM = "martin.raspaud@smhi.se"
MAIL_ADDRESS_TO = "martin.raspaud@smhi.se"
MAIL_SUBJECT = "MSG-PP production monitoring - notification"
AUTOMATIC_MESSAGE = "This is an automatic e-mail message sent from the msg server."
MAILSERVER = "corre.smhi.se"

def sendmail(message):
    import smtplib

    from_adr = MAIL_ADDRESS_FROM
    to_adr   = MAIL_ADDRESS_TO
    subj     = MAIL_SUBJECT
    aut_msg  = AUTOMATIC_MESSAGE
    mail_server_addr = MAILSERVER
    
    mail_msg = "From: %s\nSubject: %s\nTo: %s\n%s\n\n%s"%(from_adr,subj,to_adr, aut_msg, message)
    
    mail_server = smtplib.SMTP(mail_server_addr)
    mail_server.set_debuglevel(0)
    mail_server.sendmail(from_adr, to_adr, mail_msg)
    mail_server.quit()

    return

def check_output_data(time_slots):
    dirs = {}
    files = []
    
    for a in PRODUCTS:
        for p in PRODUCTS[a]:
            for f in PRODUCTS[a][p]:
                if(isinstance(f,tuple) or
                   isinstance(f,list)):
                    files = files + list(f)
                else:
                    files.append(f)

    for f in files:
        file_tuple = os.path.split(f)
        dir = file_tuple[0]
        if dirs.has_key(dir):
            dirs[dir].append(f)
        else:
            dirs[dir] = [f]

    gcpt = 0
    incomplete_slots = 0
    his = []
    log = ""
    for time_slot in time_slots:
        scpt = 0
        for dir in dirs:
            cpt = 0
            for f in dirs[dir]:
                cpt = cpt + len(glob.glob(time_slot.strftime(f)))
            gcpt = gcpt + len(dirs[dir])-cpt
            scpt = scpt + len(dirs[dir])-cpt
            if(len(dirs[dir])-cpt > 0):
                log = log + ("At %s, we have %d files missing in %s.\n")%(time_slot,len(dirs[dir])-cpt,dir)
        if scpt != 0:
            incomplete_slots = incomplete_slots + 1
        his.append(scpt)


    if gcpt > 0:
        text = "*** Statistics for the previous day : Slot %s to slot %s ***\n"%(time_slots[0],time_slots[-1]) 
        text = "%s\t*** Testing output products ***\n"%(text)
        text = "%s\tTotal number of slots with missing data: %d\n"%(text,incomplete_slots)
        text = "%s\n%s\n"%(text,log)

        output_file = msgpp_config.APPLDIR + "/log/log_out"+ time_slots[-1].strftime("%Y%m%d%H%M")+".bin"

        msgwrite_log("INFO","pickling to %s."%(output_file),moduleid=MODULE_ID)

        outputfd = open(output_file, 'wb')
        pickle.dump(time_slots, outputfd,-1)
        pickle.dump(his,outputfd,-1)
        outputfd.close()


        sendmail(text)


def check_input_data(time_slots):
    gcpt = 0
    incomplete_slots = 0
    his = []
    log = ""

    per_slot = 114
    uncomplete = 0
    for time_slot in time_slots:
        datestr = time_slot.strftime("%Y%m%d%H%M")

        fl = glob.glob("%s/H*%s*"%(HRIT_IN,datestr))

        his.append(per_slot - len(fl))


        if len(fl) != per_slot:
            gcpt = gcpt + per_slot - len(fl)
            uncomplete = uncomplete + 1
            log = log + ("At %s, we have %d files missing in %s.\n")%(time_slot,per_slot-len(fl),HRIT_IN)
            
    if(gcpt != 0):
        text = "*** Statistics for the previous day : Slot %s to slot %s ***\n"%(time_slots[0],time_slots[-1]) 
        text = "%s\t*** Testing HRIT (input data) ***\n"%(text)
        text = "%s\tTotal number of slots with missing HRIT data: %d\n"%(text,uncomplete)
        text = "%s\n%s"%(text,log)

        output_file = msgpp_config.APPLDIR + "/log/log_in"+ time_slots[-1].strftime("%Y%m%d%H%M")+".bin"

        msgwrite_log("INFO","pickling to %s."%(output_file),moduleid=MODULE_ID)

        outputfd = open(output_file, 'wb')
        pickle.dump(time_slots, outputfd,-1)
        pickle.dump(his,outputfd,-1)
        outputfd.close()

        sendmail(text)

if __name__ == "__main__":

    time_slots = time_utils.time_slots(24*4)
    check_input_data(time_slots)
    check_output_data(time_slots)
    
