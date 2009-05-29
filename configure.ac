dnl	This file is an input file used by the GNU "autoconf" program to
dnl	generate the file "configure", which is run during ImageViewer
dnl	installation to configure the system for the local environment.

AC_INIT(Makefile)

if test "${prefix}" = "NONE"; then
  prefix=/usr/local/MSG_PostProc
fi

AC_ARG_WITH(acpg,[ --with-acpg=INSTALLROOT Need to specify the root of the acpg installation to be able to configure],
	,withval=no)

ACPG_INSTALL_OK=no
ACPG_INSTALL_ROOT=
case $witval in
  no)
    ACPG_INSTALL_OK=no
    ;;
  *)
    tm_root="`echo $withval`"
    if test "X" != "$tm_root"; then
      THIS_CWD=`pwd`
      cd $tm_root
      if [[ ! -f ./mkf/def.mk ]]; then
        AC_MSG_ERROR("Could not successfully find the def.mk file")
      fi
      ACPG_INSTALL_ROOT=`pwd`
      ACPG_INSTALL_OK=yes
      cd $THIS_CWD
    fi
    ;;
esac

if [[ "x$ACPG_INSTALL_OK" != "xyes" ]]; then
  AC_MSG_ERROR("You must run configure with --with-acpg=<acpg install root dir>")
fi


AC_ARG_WITH(n2,[ --with-n2=INSTALLROOT Need to specify the root of the N2 installation to be able to configure],
	,withval=no)

N2_INSTALL_OK=no
N2_INSTALL_ROOT=
case $witval in
  no)
    N2_INSTALL_OK=no
    ;;
  *)
    tm_root="`echo $withval`"
    if test "X" != "$tm_root"; then
      THIS_CWD=`pwd`
      cd $tm_root
      N2_INSTALL_ROOT=`pwd`
      N2_INSTALL_OK=yes
      cd $THIS_CWD
    fi
    ;;
esac

if [[ "x$N2_INSTALL_OK" != "xyes" ]]; then
  AC_MSG_ERROR("You must run configure with --with-n2=<n2 install root dir>")
fi


dnl Time to extract a lot of information from the training manager installation

ACPG_INSTALL_MKF=$ACPG_INSTALL_ROOT/mkf/def.mk
if [[ "x$ACPG_INSTALL_MKF" == "x" ]]; then
  AC_MSG_ERROR("Could not identify ACPG installation mk file")
fi
echo "ACPG_INSTALL_MKF=$ACPG_INSTALL_MKF"

ACPG_INSTALL_ROOT=`echo $ACPG_INSTALL_MKF | sed -e "s/\/mkf\/def.mk//g"`
echo "ACPG_INSTALL_ROOT=$ACPG_INSTALL_ROOT"

HLHDF_ROOTDIR=`cat $ACPG_INSTALL_MKF | sed -n "/^HLHDF_ROOTDIR/p" | sed -e "s/HLHDF_ROOTDIR=//g" | awk '{print $1}'`
echo "HLHDF_LIB_DIR=$HLHDF_LIB_DIR"

HLHDF_MK_FILE=`cat $ACPG_INSTALL_MKF | sed -n "/^HLHDF_HLDEF_MK_FILE/p" | sed -e "s/HLHDF_HLDEF_MK_FILE=//g" | awk '{print $1}'`
echo "HLHDF_MK_FILE=$HLHDF_MK_FILE"

HDF5_LIBDIR=`cat $HLHDF_MK_FILE | sed -n "/^HDF5_LIBDIR/p" | sed -e "s/HDF5_LIBDIR=//g" | awk '{print $1}'`
echo "HDF5_LIBDIR=$HDF5_LIBDIR"

HDF5_LD_PATH=`echo $HDF5_LIBDIR | sed -e "s/^\-L//g"`
echo "HDF5_LD_PATH=$HDF5_LD_PATH"

ZLIB_LIBDIR=`cat $HLHDF_MK_FILE | sed -n "/^ZLIB_LIBDIR/p" | sed -e "s/ZLIB_LIBDIR=//g" | awk '{print $1}'`
ZLIB_LD_PATH=`echo $ZLIB_LIBDIR | sed -e "s/^\-L//g"`
echo "ZLIB_LD_PATH=$ZLIB_LD_PATH"

SZLIB_LIBDIR=`cat $HLHDF_MK_FILE | sed -n "/^SZLIB_LIBDIR/p" | sed -e "s/SZLIB_LIBDIR=//g" | awk '{print $1}'`
SZLIB_LD_PATH=`echo $SZLIB_LIBDIR | sed -e "s/^\-L//g"`
echo "SZLIB_LD_PATH=$SZLIB_LD_PATH"

# Python root:
PYLIB_SITEPACK=`cat $HLHDF_MK_FILE | sed -n "/^SITEPACK_PYTHON/p" | sed -e "s/SITEPACK_PYTHON=//g" | awk '{print $1}'`
PYLIBROOT=`echo $PYLIB_SITEPACK | sed -e "s/\/site-packages//g"`


AC_SUBST(ACPG_INSTALL_ROOT)
AC_SUBST(ACPG_INSTALL_MKF)
AC_SUBST(N2_INSTALL_ROOT)
AC_SUBST(ZLIB_LD_PATH)
AC_SUBST(SZLIB_LD_PATH)
AC_SUBST(HDF5_LD_PATH)
AC_SUBST(HLHDF_ROOTDIR)
AC_SUBST(PYLIBROOT)

AC_CONFIG_FILES([./scr/Makefile ./scr/msg_remap_all.ksh ./scr/msg_remap_all_Oper.ksh ./scr/tm_msg_postproc.ksh ./scr/msg_n2inject.ksh ./cfg/Makefile ./cfg/.profile_msgpp ./cfg/msgpp_config.py ./setup.env ./def.mk])
AC_OUTPUT()

