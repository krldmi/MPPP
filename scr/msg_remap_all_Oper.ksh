#!/bin/ksh

APPLDIR=/local_disk/opt/MSG_PostProc

# Set some basic environment:
. ${HOME}/.profile_msg_oper

# $1: N-slots back in time from now

if test -f ${MSG_PP_OPER_MODE_FILE}; then
    . ${APPLDIR}/cfg/.profile_msgpp
    # Check that no AAPP-session already active 
    if [ -n "`ps -edalf | grep "msg_remap_all_Oper.py" | grep -v grep`" ]; then 
	{ echo "***msg_remap_all_Oper already active, abort****"; exit ; } 
    fi
    if [ -n "`ps -edalf | grep "msg_rgb_remap_all_Oper.py" | grep -v grep`" ]; then 
	{ echo "***msg_remap_all_Oper already active, abort****"; exit ; } 
    fi
    # otherwise continue
else
    echo "host `uname -n` is not the current operational node..."
    echo "...don't run NWCSAF/MSG smhi post-processing."
    exit
fi

python ${APPLDIR}/scr/msg_remap_all_Oper.py $1
python ${APPLDIR}/scr/msg_rgb_remap_all_Oper.py $1
python ${APPLDIR}/scr/smhiPutProducts2ftpserver.py
