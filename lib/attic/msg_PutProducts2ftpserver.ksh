#!/bin/ksh

APPLDIR=/local_disk/opt/NWCSAF_MSG_PP/0_10

# Set some basic environment:
. ${HOME}/.profile_msg_oper

# $1: N-slots back in time from now

if test -f ${MSG_PP_OPER_MODE_FILE}; then
    . ${APPLDIR}/cfg/.profile_msgpp
    # Check that no AAPP-session already active 
    if [ -n "`ps -edalf | grep "msg_PutProducts2ftpserver.py" | grep -v grep`" ]; then 
	{ echo "***msg_PutProducts2ftpserver already active, abort****"; exit ; } 
    fi
    # otherwise continue
else
    echo "host `uname -n` is not the current operational node..."
    echo "...don't run NWCSAF/MSG smhi post-processing."
    exit
fi

python ${APPLDIR}/scr/msg_PutProducts2ftpserver.py >> /local_disk/opt/NWCSAF_MSG_PP/current/log/msg_PutProducts2ftpserver.log 2>&1
