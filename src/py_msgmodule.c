/*
 * This is the python module interface to the get_channel utility,
 * which allows to grab a Seviri channel from MSG data (using the MSG
 * library).
 * 
 */

#include <stdbool.h>
#include <Python.h>
#include <numpy/arrayobject.h>
#include <string.h>
#include <error.h>
#include <libnwc.h>
#include <sevext.h>

int
channel_number(char * channel_string)
{
  int channel=-1;

  if(strcmp(channel_string,"VIS06")==0 || atoi(channel_string)==1)
    channel=VIS06;
  if(strcmp(channel_string,"VIS08")==0 || atoi(channel_string)==2)
    channel=VIS08;
  if(strcmp(channel_string,"IR16")==0 || atoi(channel_string)==3)
    channel=IR16;
  if(strcmp(channel_string,"IR39")==0 || atoi(channel_string)==4)
    channel=IR39;
  if(strcmp(channel_string,"WV62")==0 || atoi(channel_string)==5)
    channel=WV62;
  if(strcmp(channel_string,"WV73")==0 || atoi(channel_string)==6)
    channel=WV73;
  if(strcmp(channel_string,"IR87")==0 || atoi(channel_string)==7)
    channel=IR87;
  if(strcmp(channel_string,"IR97")==0 || atoi(channel_string)==8)
    channel=IR97;
  if(strcmp(channel_string,"IR108")==0 || atoi(channel_string)==9)
    channel=IR108;
  if(strcmp(channel_string,"IR120")==0 || atoi(channel_string)==10)
    channel=IR120;
  if(strcmp(channel_string,"IR134")==0 || atoi(channel_string)==11)
    channel=IR134;
  if(strcmp(channel_string,"HRVIS")==0 || atoi(channel_string)==12)
    channel=HRVIS;

  return channel;

}

/*
 * channel_name_string
 *
 * Sets a channel name (string) from its number.
 * 
 */

void
channel_name_string(int channel, char * channel_string)
{
  if(channel == VIS06)
    sprintf(channel_string,"VIS06");
  if(channel == VIS08)
    sprintf(channel_string,"VIS08");
  if(channel == IR16)
    sprintf(channel_string,"IR16");
  if(channel == IR39)
    sprintf(channel_string,"IR39");
  if(channel == WV62)
    sprintf(channel_string,"WV62");
  if(channel == WV73)
    sprintf(channel_string,"WV73");
  if(channel == IR87)
    sprintf(channel_string,"IR87");
  if(channel == IR97)
    sprintf(channel_string,"IR97");
  if(channel == IR108)
    sprintf(channel_string,"IR108");
  if(channel == IR120)
    sprintf(channel_string,"IR120");
  if(channel == IR134)
    sprintf(channel_string,"IR134");
  if(channel == HRVIS)
    sprintf(channel_string,"HRVIS");

}

void
make_mask(PyArrayObject * in, PyArrayObject * out, npy_intp * dims)
{
  Py_ssize_t i,j;
  for(i=0;i<dims[0];i++)
    for(j=0;j<dims[1];j++)
      {
	*((npy_bool *)PyArray_GETPTR2(out,i,j))=
          (npy_bool)(*((npy_float *)PyArray_GETPTR2(in,i,j)) == 
                     SEVIRI_MISSING_VALUE);
      }
  
}


static PyObject *
msg_get_channels(PyObject *dummy, PyObject *args)
{

  YYYYMMDDhhmm time_slot;
  char * c_time_slot;
  char * region_name;
  char region_file[128];
  unsigned char read_rad = true;
  PyObject * channels;
  int i;
  int ch;
  int channel;
  char channel_name[128];
  Band_mask bands;

  unsigned char got_hr = false;
  unsigned char got_nonhr = false;

  Psing_region region;
  Psing_region hr_region;

  Seviri_struct seviri;
  Seviri_struct hr_seviri;

  npy_intp dims[2];
  npy_intp hr_dims[2];

  PyArrayObject *rad;
  PyArrayObject *cal;
  PyArrayObject *mask;

  PyObject * band;
  PyObject * chan_dict;

  // Parse args
  
  if (!PyArg_ParseTuple(args, "ssO|b", &c_time_slot, &region_name, &channels, &read_rad))
    {
      fprintf(stderr,"Impossible to parse arguments.");
      fflush(stderr);
      Py_RETURN_NONE;
    }
  strcpy(time_slot,c_time_slot);
  sprintf(region_file,"safnwc_%s.cfg",region_name);

  if(!PyList_Check(channels))
    {
      fprintf(stderr,"Channels is not a list.");
      fflush(stderr);
      Py_RETURN_NONE;
    }

  
  for(i = 0; i < NUM_BANDS; i++)
    {
      bands[i] = false;
    }

  for(i = 0; i < PyList_Size(channels); i++)
    {
      ch = channel_number(PyString_AsString(PyList_GetItem(channels,i)));
      bands[ch] = true;

      if(ch == HRVIS)
        got_hr = true;
      else
        got_nonhr = true;
    }

  // Init region

  if(got_hr)
    {
      if (SetRegion(&hr_region,region_file,HRV) > WARNING ) 
	{
	  error(0,0,"Could not initialize HR region...");
	  exit(EXIT_FAILURE);
	}     
      hr_dims[0] = hr_region.nb_lines;
      hr_dims[1] = hr_region.nb_cols;
    }
  if(got_nonhr)
    {
      if (SetRegion(&region,region_file,VIS_IR) > WARNING ) 
	{
	  error(0,0,"Could not initialize region...");
	  exit(EXIT_FAILURE);
	}
      dims[0] = region.nb_lines;
      dims[1] = region.nb_cols;
    }

  // Init seviri struct, hr_seviri if needed

  if(got_hr && (SevHRVInit(time_slot,hr_region,&hr_seviri)!=OK))
    {
      error(0,0,"SevHVRInit failed");
      SevFree(hr_seviri);
    }
 
  if(got_nonhr && (SevInit(time_slot,region,bands,&seviri)!=OK))
    {
      error(0,0,"SevInit failed");
      SevFree(seviri);
      Py_RETURN_NONE;
    }

  // Read channels from msg

  if(got_hr && (SevReadHRV(hr_region, &hr_seviri) > WARNING))
    {
      error(0,0,"SevReadHRV failed");
      SevFree(hr_seviri);
      Py_RETURN_NONE;
    }
    
    if(got_nonhr && (SevRead(region, &seviri, bands) > WARNING))
      {
        error(0,0,"SevRead failed");
        SevFree(seviri);
        Py_RETURN_NONE;
      }

  // Convert to radiances, reflectances, and bts.

  for(channel = 0; channel < NUM_BANDS; channel++)
     {
       if(bands[channel])
	 {
           if(channel == HRVIS)
             {
               if(read_rad)
                 SevCalibrate(&hr_seviri,channel);
               
               SevCalRefl(&hr_seviri,channel);
             }
           else
             {
               if(read_rad)
                 SevCalibrate(&seviri,channel);
               
               if(channel == VIS06 || channel == VIS08 || channel == IR16)
                 SevCalRefl(&seviri,channel);
               else
                 SevConvert(&seviri,channel);
             }
	 }
     }

  // Check the channels

  // Append channels to a python dict

  if(!(chan_dict = PyDict_New()))
    {
      fprintf(stderr,"Can't create a dict.");
      fflush(stderr);
      Py_RETURN_NONE;
    }
  
  for(channel = 0; channel < NUM_BANDS; channel++)
    if(bands[channel])
      {
        if(channel == HRVIS)
          {
            if(read_rad)
              rad = (PyArrayObject *)PyArray_SimpleNewFromData(2,hr_dims,NPY_FLOAT,
                                                               SevBand(hr_seviri,channel,RAD));
            else
              rad = (PyArrayObject *)PyArray_EMPTY(2, hr_dims, NPY_FLOAT,0);
            if(SevBand(hr_seviri,channel,REFL)!=NULL)
              {
                cal = (PyArrayObject *)PyArray_SimpleNewFromData(2,hr_dims,NPY_FLOAT,
                                                                 SevBand(hr_seviri,channel,REFL));
              }
            else
              {
                cal = (PyArrayObject *)PyArray_SimpleNewFromData(2,hr_dims,NPY_FLOAT,
                                                                 SevBand(hr_seviri,channel,BT));
              }
            mask = (PyArrayObject *)PyArray_SimpleNew(2, hr_dims, NPY_BOOL);
            make_mask(cal, mask, hr_dims);
          }
        else
          {
            if(read_rad)
              rad = (PyArrayObject *)PyArray_SimpleNewFromData(2,dims,NPY_FLOAT,
                                                               SevBand(seviri,channel,RAD));
            else
              rad = (PyArrayObject *)PyArray_EMPTY(2, dims, NPY_FLOAT,0);
            if(SevBand(seviri,channel,REFL)!=NULL)
              {
                cal = (PyArrayObject *)PyArray_SimpleNewFromData(2,dims,NPY_FLOAT,
                                                                 SevBand(seviri,channel,REFL));
              }
            else
              {
                cal = (PyArrayObject *)PyArray_SimpleNewFromData(2,dims,NPY_FLOAT,
                                                                 SevBand(seviri,channel,BT));
              }
            mask = (PyArrayObject *)PyArray_SimpleNew(2, dims, NPY_BOOL);
            make_mask(cal, mask, dims);
          }
        band = Py_BuildValue("{s:N,s:N,s:N}",
                             "RAD", PyArray_Return(rad),
                             "CAL", PyArray_Return(cal),
                             "MASK",PyArray_Return(mask));
        channel_name_string(channel,channel_name);
        PyDict_SetItemString(chan_dict,channel_name,band);
      }

  // Return the dict
  
  return chan_dict;
  
}

/*
static PyObject *
msg_lat_lon_from_region(PyObject *dummy, PyObject *args)
{
  
  PyArrayObject *lat;
  PyArrayObject *lon;

  char * region_name;
  char region_file[128];
  char * channel;

  float **alat;
  float **alon;

  int dimensions[2];
  npy_intp dims[2];
  int rank;
  
  if (!PyArg_ParseTuple(args, "ss", &region_name, &channel))
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
*/



static PyObject *
msg_missing_value()
{
  return Py_BuildValue("f",(float)SEVIRI_MISSING_VALUE);
}

static PyMethodDef MsgMethods[] = {
    {"get_channels",  msg_get_channels, METH_VARARGS,
     "Gets a list of Seviri channels from MSG."},
    /*{"lat_lon_from_region",  msg_lat_lon_from_region, METH_VARARGS,
     "Gets latitudes and longitudes for a given region file."},*/
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

