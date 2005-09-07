#!/bin/ksh

APPLDIR=/local_disk/opt/MSG_PostProc

. ${APPLDIR}/cfg/.profile_msgpp

# $1: start-date (yyyymmddhhmm)
# $2: end-date (yyyymmddhhmm)

python ${APPLDIR}/scr/msg_remap_all.py $1 $2
python ${APPLDIR}/scr/msg_rgb_remap_all.py $1 $2
