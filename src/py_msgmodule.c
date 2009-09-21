/*
 * This is the python module interface to the get_channel utility,
 * which allows to grab a Seviri channel from MSG data (using the MSG
 * library).
 * 
 */

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

    int dimensions[4];
    npy_intp dims[4];
    int rank;
    int is_ref;
    

    if (!PyArg_ParseTuple(args, "sss", &time_slot, &region_file, &channel))
        return NULL;
    

    rank = get_channel_dims(region_file, channel, dimensions);

    arad = allocate_float_array(dimensions[0],dimensions[1]);
    aref_or_abt = allocate_float_array(dimensions[0],dimensions[1]);
    amask = allocate_uchar_array(dimensions[0],dimensions[1]);
    
    get_channel(time_slot,region_file,channel,arad,aref_or_abt,&is_ref,amask);

    dims[0]=dimensions[0];
    dims[1]=dimensions[1];

    rad = (PyArrayObject *)PyArray_SimpleNew(rank, dims, NPY_FLOAT);
    copy_to_2Dfloat_pyarray(arad,rad,dimensions);
    
    ref_or_bt = (PyArrayObject *)PyArray_SimpleNew(rank, dims, NPY_FLOAT);
    copy_to_2Dfloat_pyarray(aref_or_abt,ref_or_bt,dimensions);

    mask = (PyArrayObject *)PyArray_SimpleNew(rank, dims, NPY_BOOL);
    copy_to_2Dbool_pyarray(amask,mask,dimensions);
    
    free(arad);
    free(aref_or_abt);
    free(amask);

    if(is_ref == 1)
      return Py_BuildValue("{s:O,s:O,s:O}","RAD",PyArray_Return(rad),"REFL",PyArray_Return(ref_or_bt),"MASK",PyArray_Return(mask));
    else
      return Py_BuildValue("{s:O,s:O,s:O}","RAD",PyArray_Return(rad),"BT",PyArray_Return(ref_or_bt),"MASK",PyArray_Return(mask));
}

static PyMethodDef MsgMethods[] = {
    {"getChannel",  msg_get_channel, METH_VARARGS,
     "Gets a Seviri channel from MSG."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initmsg(void)
{
    (void) Py_InitModule("msg", MsgMethods);
    import_array();
    Py_Initialize();
}

