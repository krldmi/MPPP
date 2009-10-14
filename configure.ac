dnl	This file is an input file used by the GNU "autoconf" program to
dnl	generate the file "configure", which is run during ImageViewer
dnl	installation to configure the system for the local environment.

AC_INIT(Makefile)

if test "${prefix}" = "NONE"; then
  prefix=/usr/local/MSG_PostProc
fi


################################################################################
#                           Python & Numpy
################################################################################

AC_ARG_VAR([PYTHON],[Python interpretper])
AC_CHECK_PROG([PYTHON],[python],[python])

# Check if python interpreter works
AC_MSG_CHECKING([if python works])
py_command="from math import *; aTuple = ('robots', 77, 93, 'try'); \
  sqrt(aTuple[[1]])"
if ${PYTHON} -c "$py_command" >/dev/null 2>&1; then
  AC_MSG_RESULT([yes])
else
  AC_MSG_RESULT([NO])
  PYTHON=
fi



if test "x$PYTHON" != "x"; then
   # Checking python version
   AC_MSG_CHECKING([python version])
   py_command="import sys; print '%d.%d'%(sys.version_info[[0]], \
               sys.version_info[[1]])"
   PYVERSION=`$PYTHON -c "$py_command"`
   AC_MSG_RESULT(${PYVERSION})
   AS_VERSION_COMPARE("2.4",$PYVERSION,
     [],
     [],
     [AC_MSG_ERROR("python >= 2.4 is needed.")])

   
 
    # Allow user to specify location of python includes
  AC_ARG_WITH(python-includes,[AC_HELP_STRING([--with-python-includes=DIR],
          [Specify directory containing Python headers])],
          [PYTHON_DIR="$withval"],[PYTHON_DIR=])

    # Get the default Python include dir containing pyconfig.h
    # Note: Python does this automatically via distutils
  AC_MSG_CHECKING([for location of python headers])
  py_command="import sys; print '%s/include/python%d.%d' % (sys.prefix, \
    sys.version_info[[0]],sys.version_info[[1]])"
  if pydir_out=`$PYTHON -c "$py_command"`; then
    PYCONFIG_DIR="$pydir_out"
  else
    AC_MSG_ERROR("python interpreter is broken?")
  fi

    # If user did not specify an include dir, use the default
  if test "x" = "x$PYTHON_DIR"; then
    PYTHON_DIR=PYCONFIG_DIR
  fi
  AC_MSG_RESULT($PYTHON_DIR)

    # Determine location for python libraries
  py_command="import sys; print '$libdir/python%d.%d/site-packages' % (\
    sys.version_info[[0]],sys.version_info[[1]])"
  pylibdir=`$PYTHON -c "$py_command"`
  AC_SUBST(pylibdir)

    # Check for expected header in python include dir
  old_CPPFLAGS="$CPPFLAGS"
  CPPFLAGS="$CPPFLAGS -I$PYTHON_DIR -I$PYCONFIG_DIR"
  AC_CHECK_HEADER([pyconfig.h],[],[PYTHON_DIR=; AC_MSG_WARN([mis-detected python include dir])],[])
  AC_CHECK_HEADER([Python.h],[],[PYTHON_DIR=; AC_MSG_WARN([mis-detected python include dir])],[])
  CPPFLAGS="$old_CPPFLAGS"
 
    # Check that NumPy module is installed
  HAVE_NUMPY=no
  AC_MSG_CHECKING([for NumPy module])
  if "${PYTHON}" -c "import numpy.core" >/dev/null 2>&1; then
    HAVE_NUMPY=yes
  fi
  AC_MSG_RESULT($HAVE_NUMPY)
 
  if test yes = $HAVE_NUMPY; then
 
      # Allow user to specify location of NumPy includes
    AC_ARG_WITH(numpy,[AC_HELP_STRING([--with-numpy=DIR],
            [Specify directory containing Numpy include directory])],
            [NUMPY_DIR="$withval"],[NUMPY_DIR=])

      # If numpy directory was not specified, guess
    if test "x" = "x$NUMPY_DIR"; then
      AC_MSG_CHECKING([for location of NumPy includes])
      if test -d "${PYTHON_DIR}/numpy"; then
        NUMPY_DIR="${PYTHON_DIR}"
      else
        py_command="import numpy; print numpy.__path__[[0]]"
        NUMPY_DIR=`$PYTHON -c "$py_command"`/..
      fi
    else
      AC_MSG_CHECKING([for location of NumPy includes])
      AC_MSG_RESULT([$NUMPY_DIR])
    fi
    
    NUMPY_INC=$NUMPY_DIR/numpy/core/include
   
   # Check numpy version

   AC_MSG_CHECKING([numpy version])
   py_command="import numpy; print numpy.__version__"
   NUMPYVERSION=`PYTHONPATH=$NUMPY_DIR:$PYTHONPATH $PYTHON -c "$py_command"`
   AC_MSG_RESULT([$NUMPYVERSION])
   AS_VERSION_COMPARE("1.2.0",$NUMPYVERSION,
     [],
     [],
     [AC_MSG_ERROR("numpy >= 1.2.0 is needed.")])

   

    # Check for expected headers in NUMPY_DIR
   
    old_CPPFLAGS="$CPPFLAGS"
    CPPFLAGS="$CPPFLAGS -I$NUMPY_INC -I$PYTHON_DIR -I$PYCONFIG_DIR"
    AC_CHECK_HEADER([numpy/arrayobject.h],[],[NUMPY_DIR=; AC_MSG_WARN([mis-detected NumPy include dir])],[#include "Python.h"])
    CPPFLAGS="$old_CPPFLAGS"
  fi
fi

AC_SUBST(PYTHON)
AC_SUBST(PYTHON_DIR)
AC_SUBST(NUMPY_DIR)
AC_SUBST(NUMPY_INC)

################################################################################
#                           HLHDF
################################################################################

AC_ARG_WITH(hlhdf,[ --with-hlhdf=INSTALLROOT Need to specify the root of the hlhdf installation to be able to configure],
	,withval=no)

HLHDF_INSTALL_OK=no
HLHDF_INSTALL_ROOT=
case $withval in
  no)
    HLHDF_INSTALL_OK=no
    ;;
  *)
    tm_root="`echo ${withval}`"
    if test "X" != "$tm_root"; then
      THIS_CWD=`pwd`
      cd $tm_root
      if [[ ! -f ./mkf/hldef.mk ]]; then
        AC_MSG_ERROR("Could not successfully find the def.mk file")
      fi
      HLHDF_INSTALL_ROOT=`pwd`
      HLHDF_INSTALL_OK=yes
      cd $THIS_CWD
    fi
    ;;
esac

if [[ "x$HLHDF_INSTALL_OK" != "xyes" ]]; then
  AC_MSG_ERROR("You must run configure with --with-hlhdf=<hlhdf install root dir>")
fi


################################################################################
#                           Acpg
################################################################################

AC_ARG_WITH(acpg,[ --with-acpg=INSTALLROOT Need to specify the root of the acpg installation to be able to configure],
	,withval=no)

ACPG_INSTALL_OK=no
ACPG_INSTALL_ROOT=
case $withval in
  no)
    ACPG_INSTALL_OK=no
    ;;
  *)
    tm_root="`echo ${withval}`"
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

################################################################################
#                           MSG
################################################################################

AC_ARG_WITH(msg,[ --with-msg=INSTALLROOT Need to specify the root of the msg installation to be able to configure],
	,withval=no)

MSG_INSTALL_OK=no
MSG_INSTALL_ROOT=
case $withval in
  no)
    MSG_INSTALL_OK=no
    ;;
  yes)
    MSG_INSTALL_OK=no
    ;;
  *)
    MSG_INSTALL_ROOT="`echo ${withval}`"
    MSG_INSTALL_OK=yes
    ;;
esac

if [[ "x$MSG_INSTALL_OK" != "xyes" ]]; then
  AC_MSG_ERROR("You must run configure with --with-msg=<msg install root dir>")
fi

################################################################################
#                           Export dir
################################################################################

AC_ARG_WITH(export_dir,[ --with-export-dir=EXPORT_DIR Specify the data export directory],
	,withval=no)

EXPORT_DIR_OK=no
EXPORT_DIR="${prefix}/share"
case $withval in
  no)
    EXPORT_DIR_OK=no
    ;;
  yes)
    EXPORT_DIR_OK=no
    ;;
  *)
    EXPORT_DIR="`echo ${withval}`"
    EXPORT_DIR_OK=yes
    ;;
esac


################################################################################
#                           N2INJECT
################################################################################
dnl This seems to be uneeded - 20090925, Martin

AC_ARG_WITH(n2,[ --with-n2=INSTALLROOT Need to specify the root of the N2 installation to be able to configure],
	,withval=yes)

N2_INSTALL_OK=no
N2_INSTALL_ROOT=
case $withval in
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
      AC_SUBST(N2_INSTALL_ROOT)
    fi
    ;;
esac

if [[ "x$withval" == "xyes" ]]; then
  AC_MSG_ERROR("You must run configure with --with-n2=<n2 install root dir>")
fi


################################################################################
#                           Misc
################################################################################
dnl Time to extract a lot of information from the training manager installation

ACPG_INSTALL_MKF=$ACPG_INSTALL_ROOT/mkf/def.mk
if [[ "x$ACPG_INSTALL_MKF" == "x" ]]; then
  AC_MSG_ERROR("Could not identify ACPG installation mk file")
fi
echo "ACPG_INSTALL_MKF=$ACPG_INSTALL_MKF"

ACPG_INSTALL_ROOT=`echo $ACPG_INSTALL_MKF | sed -e "s/\/mkf\/def.mk//g"`
echo "ACPG_INSTALL_ROOT=$ACPG_INSTALL_ROOT"

ACPG_DATA_DIR=`cat $ACPG_INSTALL_MKF | sed -n "/^ACPG_DATA_DIR/p" | sed -e "s/ACPG_DATA_DIR=//g" | awk '{print $1}'`
echo "ACPG_DATA_DIR=$ACPG_DATA_DIR"

HLHDF_ROOTDIR=$HLHDF_INSTALL_ROOT
#HLHDF_ROOTDIR=`cat $ACPG_INSTALL_MKF | sed -n "/^HLHDF_ROOTDIR/p" | sed -e "s/HLHDF_ROOTDIR=//g" | awk '{print $1}'`
#echo "HLHDF_LIB_DIR=$HLHDF_LIB_DIR"

#HLHDF_MK_FILE=`cat $ACPG_INSTALL_MKF | sed -n "/^HLHDF_HLDEF_MK_FILE/p" | sed -e "s/HLHDF_HLDEF_MK_FILE=//g" | awk '{print $1}'`
#echo "HLHDF_MK_FILE=$HLHDF_MK_FILE"

#HDF5_LIBDIR=`cat $HLHDF_MK_FILE | sed -n "/^HDF5_LIBDIR/p" | sed -e "s/HDF5_LIBDIR=//g" | awk '{print $1}'`
#echo "HDF5_LIBDIR=$HDF5_LIBDIR"

#HDF5_LD_PATH=`echo $HDF5_LIBDIR | sed -e "s/^\-L//g"`
#echo "HDF5_LD_PATH=$HDF5_LD_PATH"

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
AC_SUBST(ACPG_DATA_DIR)
AC_SUBST(MSG_INSTALL_ROOT)
AC_SUBST(EXPORT_DIR)
AC_SUBST(ZLIB_LD_PATH)
AC_SUBST(SZLIB_LD_PATH)
#AC_SUBST(HDF5_LD_PATH)
AC_SUBST(HLHDF_ROOTDIR)
AC_SUBST(PYLIBROOT)

AC_CONFIG_FILES([./src/Makefile ./lib/Makefile ./lib/tm_msg_postproc.ksh ./lib/msg_n2inject.ksh ./etc/Makefile ./etc/.profile_msgpp ./etc/msgpp_config.py ./setup.env ./def.mk])
AC_OUTPUT()

