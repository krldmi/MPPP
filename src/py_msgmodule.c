/*
 * This is the python module interface to the get_channel utility,
 * which allows to grab a Seviri channel from MSG data (using the MSG
 * library).
 * 
 */

#include <stdbool.h>
#include <Python.h>
#include <numpy/arrayobject.h>
#include "libmsg_channel.h"


void
copy_to_2Dbool_pyarray(unsigned char ** in, PyArrayObject * out, int * dims)
{
  Py_ssize_t i,j;
  for(i=0;i<dims[0];i++)
    for(j=0;j<dims[1];j++)
      {
	*((npy_bool *)PyArray_GETPTR2(out,i,j))=(npy_bool)in[i][j];
      }
  
}

void
copy_to_2Dfloat_pyarray(float ** in, PyArrayObject * out, int * dims)
{
  Py_ssize_t i,j;
  for(i=0;i<dims[0];i++)
    for(j=0;j<dims[1];j++)
      {
	*((npy_float *)PyArray_GETPTR2(out,i,j))=(npy_float)in[i][j];
      }
  
}


void
copy_to_3Dbool_pyarray(unsigned char *** in, PyArrayObject * out, int * dims)
{
  Py_ssize_t i, j, k;

  for(i = 0; i < dims[0]; i++)
    for(j = 0; j < dims[1]; j++)
      for(k = 0; k < dims[2]; k++)
	{
	  *((npy_bool *)PyArray_GETPTR3(out,i,j,k))=(npy_bool)in[i][j][k];
	}
  
}

void
copy_to_3Dfloat_pyarray(float *** in, PyArrayObject * out, int * dims)
{
  Py_ssize_t i, j, k;
  for(i = 0; i < dims[0]; i++)
    for( j = 0; j < dims[1]; j++)
      for( k = 0; k < dims[2]; k++)
	{
	  *((npy_float *)PyArray_GETPTR3(out,i,j,k))=(npy_float)in[i][j][k];
	}
  
}


/*
 * Interface function between get_channel and python. Builds numpy
 * arrays for the given channels (radiance, reflectance or brightness
 * temperature, and mask).
 * 
 */

static PyObject *
msg_get_channel(PyObject *dummy, PyObject *args)
{


  PyArrayObject *rad;
  PyArrayObject *ref_or_bt;
  PyArrayObject *mask;
    
  float ** arad;
  float ** aref_or_abt;
  unsigned char ** amask;

  char *time_slot;
  char *channel;
  char *region_file;

  char read_rad = true;

  int dimensions[2];
  npy_intp dims[2];
  int rank;
  int ok;

  if (!PyArg_ParseTuple(args, "sss|b", &time_slot, &region_file, &channel, &read_rad))
    return NULL;
    

  rank = get_channel_dims(region_file, channel, dimensions);
  
  if(read_rad)
    arad = allocate_float_array(dimensions[0],dimensions[1]);
  else
    arad = NULL;

  aref_or_abt = allocate_float_array(dimensions[0],dimensions[1]);
  amask = allocate_uchar_array(dimensions[0],dimensions[1]);
    
  ok = get_channel(time_slot,region_file,channel,arad,aref_or_abt,amask);

  if(ok != EXIT_SUCCESS)
    {
      if(read_rad)
	free_2D_float_array(arad, dimensions[0]);

      free_2D_float_array(aref_or_abt, dimensions[0]);
      free_2D_uchar_array(amask, dimensions[0]);

      return Py_BuildValue("{s:N,s:N,s:N}","RAD",Py_None,"CAL",Py_None,"MASK",Py_None);
    }


  dims[0]=dimensions[0];
  dims[1]=dimensions[1];

  if(read_rad)
    {
      rad = (PyArrayObject *)PyArray_SimpleNew(rank, dims, NPY_FLOAT);
      copy_to_2Dfloat_pyarray(arad,rad,dimensions);
    }
    
  ref_or_bt = (PyArrayObject *)PyArray_SimpleNew(rank, dims, NPY_FLOAT);
  copy_to_2Dfloat_pyarray(aref_or_abt,ref_or_bt,dimensions);

  mask = (PyArrayObject *)PyArray_SimpleNew(rank, dims, NPY_BOOL);
  copy_to_2Dbool_pyarray(amask,mask,dimensions);
    
  if(read_rad)
    free_2D_float_array(arad, dimensions[0]);

  free_2D_float_array(aref_or_abt, dimensions[0]);
  free_2D_uchar_array(amask, dimensions[0]);
    
  if(read_rad)
    return Py_BuildValue("{s:N,s:N,s:N}","RAD",PyArray_Return(rad),"CAL",PyArray_Return(ref_or_bt),"MASK",PyArray_Return(mask));
  else
    return Py_BuildValue("{s:N,s:N,s:N}","RAD",Py_None,"CAL",PyArray_Return(ref_or_bt),"MASK",PyArray_Return(mask));
    
}

static PyObject *
msg_get_all_channels(PyObject *dummy, PyObject *args)
{


  PyArrayObject *rad;
  PyArrayObject *ref_or_bt;
  PyArrayObject *mask;
  
  float *** arad;
  float *** aref_or_abt;
  unsigned char *** amask;
  
  char *time_slot;
  char *region_file;
  
  char read_rad = true;
  int dimensions[3];
  npy_intp dims[3];
  int rank;
  int i;

  if (!PyArg_ParseTuple(args, "ss|b", &time_slot, &region_file, &read_rad))
    return NULL;
  
  
  get_channel_dims(region_file, "VIS06", dimensions);
  if(read_rad)
    arad = allocate_3D_float_array(dimensions[0],dimensions[1]);
  else
    arad = NULL;

  aref_or_abt = allocate_3D_float_array(dimensions[0],dimensions[1]);
  amask = allocate_3D_uchar_array(dimensions[0],dimensions[1]);
    
  dimensions[2] = dimensions[1];
  dimensions[1] = dimensions[0];
  dimensions[0] = get_all_channels(time_slot,region_file,arad,aref_or_abt,amask);
  
  dims[0] = dimensions[0];
  dims[1] = dimensions[1];
  dims[2] = dimensions[2];
  
  rank = 3;
  
  if(read_rad)
    {
      rad = (PyArrayObject *)PyArray_SimpleNew(rank, dims, NPY_FLOAT);
      copy_to_3Dfloat_pyarray(arad,rad,dimensions);
    }
  else
    {
      rad = (PyArrayObject *)PyArray_EMPTY(1, dims, PyArray_OBJECT,0);
    }
  
  ref_or_bt = (PyArrayObject *)PyArray_SimpleNew(rank, dims, NPY_FLOAT);
  copy_to_3Dfloat_pyarray(aref_or_abt,ref_or_bt,dimensions);
  
  mask = (PyArrayObject *)PyArray_SimpleNew(rank, dims, NPY_BOOL);
  copy_to_3Dbool_pyarray(amask,mask,dimensions);
  
  if(read_rad)
    free_3D_float_array(arad, dimensions[1]);

  free_3D_float_array(aref_or_abt, dimensions[1]);
  free_3D_uchar_array(amask, dimensions[1]);
  
  return Py_BuildValue("{s:N,s:N,s:N}","RAD",PyArray_Return(rad),"CAL",PyArray_Return(ref_or_bt),"MASK",PyArray_Return(mask));
  
}

static PyObject *
msg_lat_lon_from_region(PyObject *dummy, PyObject *args)
{
  
  PyArrayObject *lat;
  PyArrayObject *lon;

  char * region_file;
  char * channel;

  float **alat;
  float **alon;

  int dimensions[2];
  npy_intp dims[2];
  int rank;
  
  if (!PyArg_ParseTuple(args, "ss", &region_file, &channel))
    return NULL;
  
  
  rank = get_channel_dims(region_file, channel, dimensions);
  
  alat = allocate_float_array(dimensions[0],dimensions[1]);
  alon = allocate_float_array(dimensions[0],dimensions[1]);

  lat_lon_from_region(region_file,channel, alat, alon);

  dims[0]=dimensions[0];
  dims[1]=dimensions[1];

  lat = (PyArrayObject *)PyArray_SimpleNew(rank, dims, NPY_FLOAT);
  lon = (PyArrayObject *)PyArray_SimpleNew(rank, dims, NPY_FLOAT);

  copy_to_2Dfloat_pyarray(alat,lat,dimensions);
  copy_to_2Dfloat_pyarray(alon,lon,dimensions);

  free_2D_float_array(alat,dimensions[0]);
  free_2D_float_array(alon,dimensions[0]);
  
  return Py_BuildValue("(N,N)",PyArray_Return(lat),PyArray_Return(lon));
}

static PyObject *
msg_missing_value()
{
  return Py_BuildValue("f",missing_value());
}

static PyMethodDef MsgMethods[] = {
    {"get_channel",  msg_get_channel, METH_VARARGS,
     "Gets a Seviri channel from MSG."},
    {"get_all_channels",  msg_get_all_channels, METH_VARARGS,
     "Gets all Seviri channels except HRVIS from MSG."},
    {"lat_lon_from_region",  msg_lat_lon_from_region, METH_VARARGS,
     "Gets latitudes and longitudes for a given region file."},
    {"missing_value",  msg_missing_value, METH_VARARGS,
     "Gets the fill value for missing data."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initpy_msg(void)
{
    (void) Py_InitModule("py_msg", MsgMethods);
    import_array();
    Py_Initialize();
}

