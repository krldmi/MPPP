#!/bin/sh
# Script for starting/controling the NWCSAF/MSG PostProc application from init.d
#
# Author: Adam Dybbroe
# Date 2005 December 07
# Revised:
#     
#
# Set some basic environment variables
. ${HOME}/.profile_msg_oper

# Check if environment variables have been set (in case .profile is gone...)
if [ "x$MSG_PP_OPER_MODE_FILE" == "x" ]; then
    echo "ERROR: Can't fins environment variable MSG_PP_OPER_MODE_FILE."
    echo "   .profile is gone or there is something seriously wrong in the system!!!"
    exit
fi

case "$1" in
start)
   touch ${MSG_PP_OPER_MODE_FILE} >> /dev/null 2>&1
   ;;
stop)
   \rm -f ${MSG_PP_OPER_MODE_FILE}
   ;;
status)
   omode=Test
   if test -f ${MSG_PP_OPER_MODE_FILE}; then
      omode=Operational
   fi
   if test -f ${MSG_PP_OPER_MODE_FILE}; then
      echo "NWCSAF/MSG-PP running or is beeing started. ${omode}"
   else
      echo "NWCSAF/MSG-PP stopped or is beeing stopped. ${omode}"
   fi
   ;;
esac
