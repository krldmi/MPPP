#!/bin/ksh

APPLDIR=/local_disk/opt/MSG_PostProc

. ${APPLDIR}/cfg/.profile_msgpp

# $1: N-slots back in time from now

# Check that no AAPP-session already active 
if [ -n "`ps -edalf | grep "msg_remap_all_Oper.py" | grep -v grep`" ]; then 
  { echo "***msg_remap_all_Oper already active, abort****"; exit ; } 
fi
if [ -n "`ps -edalf | grep "msg_rgb_remap_all_Oper.py" | grep -v grep`" ]; then 
  { echo "***msg_remap_all_Oper already active, abort****"; exit ; } 
fi
# otherwise continue

python ${APPLDIR}/scr/msg_remap_all_Oper.py $1
python ${APPLDIR}/scr/msg_rgb_remap_all_Oper.py $1
