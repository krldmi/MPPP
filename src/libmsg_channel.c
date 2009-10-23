#include <string.h>
#include <error.h>
#include <libnwc.h>
#include <sevext.h>
#include "libmsg_channel.h"

/*
 *
 * MSG_read_channels
 *
 * Uses the MSG library to read channels from METEOSAT (Seviri
 * instrument).
 *
 * The user should provide a date, region and seviri struct in MSG
 * formats, and a channel bitmask describing the required channels.
 *
 */


int
MSG_read_channels(YYYYMMDDhhmm sev_date,
		  Psing_region region, 
		  Seviri_struct *seviri,
		  Band_mask bands,
		  int with_radiance)
{
  int i;
  int channel;

   /*
   **   Initialise 
   */   

   if(bands[HRVIS])
     {
       if (SevHRVInit(sev_date,region,seviri)!=OK)
	 {
	   error(0,0,"SevHVRInit failed");
	   SevFree(*seviri);
	   return EXIT_FAILURE;
	 }
     }
   else
     {
       if (SevInit(sev_date,region,bands,seviri)!=OK)
	 {
	   error(0,0,"SevInit failed");
	   SevFree(*seviri);
	   return EXIT_FAILURE;
	 }
     }
   
   /*
   **   Read
   */
   if(bands[HRVIS])
     {
       if ((i=SevReadHRV(region, seviri)) > (WARNING))
	 {
	   error(0,0,"SevReadHRV failed");
	   SevFree(*seviri);
	   return EXIT_FAILURE;
	 }
     }
   else
     {
       if ((i=SevRead(region, seviri,bands)) > (WARNING))
	 {
	   error(0,0,"SevRead failed");
	   SevFree(*seviri);
	   return EXIT_FAILURE;
	 }
     }
   
   /*
   **   Convert into reflectances, radiances and bt
   */

   for(channel = 0; channel < NUM_BANDS; channel++)
     {
       if(bands[channel])
	 {
	   if(with_radiance)
	     SevCalibrate(seviri,channel);
	   
	   if(channel==HRVIS || channel==VIS06 || 
	      channel==VIS08 || channel==IR16)
	     SevCalRefl(seviri,channel);
	   else
	     SevConvert(seviri,channel);
	 }
     }

   return EXIT_SUCCESS;
}

/*
 *
 * MSG_read_channel
 *
 * Uses the MSG library to read a channel from METEOSAT (Seviri
 * instrument).
 *
 * The user should provide a date, region and seviri struct in MSG
 * formats, and a channel.
 *
 */

int
MSG_read_channel(YYYYMMDDhhmm sev_date,
		 Psing_region region, 
		 Seviri_struct *seviri,
		 int channel,
		 int with_radiance)
{
  Band_mask bands;
  int j = 0;
  
  for(j = 0; j < NUM_BANDS; j++)
    bands[j]=FALSE;
  bands[channel]=TRUE;
  
  return MSG_read_channels(sev_date, region, seviri, bands, with_radiance);
}


/*
 *
 * allocate_float_array
 *
 * Allocates memory for a 2D array of floats.
 * 
 */

float **
allocate_float_array(int lines, int cols)
{
  float ** out;
  int i = 0;

  out = (float**)malloc(sizeof(float*)*lines);
  for(i = 0; i < lines; i++)
    {
      out[i] = (float*)malloc(sizeof(float)*cols);
    }
  return out;
}

/*
 *
 * allocate_uchar_array
 *
 * Allocates memory for a 2D array of unsigned chars.
 * 
 */

unsigned char **
allocate_uchar_array(int lines, int cols)
{
  unsigned char ** out;
  int i = 0;

  out = (unsigned char**)malloc(sizeof(unsigned char*)*lines);
  for(i = 0; i < lines; i++)
    {
      out[i] = (unsigned char*)malloc(sizeof(unsigned char)*cols);
    }
  return out;
}

/*
 *
 * allocate_3D_float_array
 *
 * Allocates memory for a 3D array of floats.
 * 
 */

float ***
allocate_3D_float_array(int lines, int cols)
{
  float *** out;
  int i = 0;
  int j = 0;

  out = (float***)malloc(sizeof(float**)*(NUM_BANDS-1));
  for(j = 0; j < NUM_BANDS - 1; j++)
    {
        out[j] = (float**)malloc(sizeof(float*)*lines);
	
	for(i = 0; i < lines; i++)
	  {
	    out[j][i] = (float*)malloc(sizeof(float)*cols);
	  }
    }
  return out;
}

/*
 *
 * allocate_3D_uchar_array
 *
 * Allocates memory for a 3D array of unsigned chars.
 * 
 */

unsigned char ***
allocate_3D_uchar_array(int lines, int cols)
{
  unsigned char *** out;
  int i = 0;
  int j = 0;

  out = (unsigned char***)malloc(sizeof(unsigned char**)*(NUM_BANDS-1));
  for(j = 0; j < NUM_BANDS - 1; j++)
    {
      out[j] = (unsigned char**)malloc(sizeof(unsigned char*)*lines);
      for(i = 0; i < lines; i++)
	{
	  out[j][i] = (unsigned char*)malloc(sizeof(unsigned char)*cols);
	}
    }
  return out;
}

void
free_2D_float_array(float ** array, int lines)
{
  int i = 0;
  for(i = 0; i < lines; i++)
    free(array[i]);
  free(array);
}

void
free_2D_uchar_array(unsigned char ** array, int lines)
{
  int i = 0;
  for(i = 0; i < lines; i++)
    free(array[i]);
  free(array);
}

void
free_3D_float_array(float *** array, int lines)
{
  int i = 0;
  int j = 0;

  for(j = 0; j < NUM_BANDS - 1; j++)
    {
      for(i = 0; i < lines; i++)
	free(array[j][i]);
      free(array[j]);
    }
  free(array);
}

void
free_3D_uchar_array(unsigned char *** array, int lines)
{
  int i = 0;
  int j = 0;

  for(j = 0; j < NUM_BANDS - 1; j++)
    {
      for(i = 0; i < lines; i++)
	free(array[j][i]);
      free(array[j]);
    }
  free(array);
}

/*
 * copy_and_cast
 *
 * Copies and casts a array from MSG’s Float_32 to regular floats.
 * 
 */

void
copy_and_cast(Float_32 ** in, float ** out, int lines,int cols)
{
  int i = 0;
  int j = 0;

  for(i=0; i<lines; i++)
    for(j=0; j<cols; j++)
      {
	out[i][j] = (float)in[i][j];
      }
}

/*
 * make_mask
 *
 * Creates a boolean mask discriminating a channel’s invalid
 * measurements.
 * 
 */

void
make_mask(Float_32 ** in, unsigned char ** out, int lines, int cols)
{
  int i = 0;
  int j = 0;

  for(i=0; i<lines; i++)
    for(j=0; j<cols; j++)
      {
	out[i][j] = (in[i][j] == SEVIRI_MISSING_VALUE);
      }
  
  
}

/*
 * make_blank_mask
 *
 * Creates a boolean mask discriminating an entire channel.
 * 
 */

void
make_blank_mask(unsigned char ** out, int lines, int cols)
{
  int i = 0;
  int j = 0;

  for(i=0; i<lines; i++)
    for(j=0; j<cols; j++)
      {
	out[i][j] = TRUE;
      }
  
  
}

/*
 * channel_number
 *
 * Returns a channel number from its string representation, for
 * example:
 * "HRVIS" or "12"
 * 
 */

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

/*
 *
 * missing_value
 *
 * Gets the fill value for missing data. 
 * 
 */



float
missing_value()
{
  return (float)SEVIRI_MISSING_VALUE;
}

/*
 * get_channel_dims
 *
 * Fills a "dims" array of ints with the dimensions of a channel
 * computed from an MSG region file.
 * 
 */

int
get_channel_dims(char * region_file, char * channel_string, int * dims)
{
  int rank = 2;
  int channel;
  Psing_region region;

  channel = channel_number(channel_string);
  if(channel==-1)
    {
      return 0;
    }


  if(channel == HRVIS)
    {
      if (SetRegion(&region,region_file,HRV) > WARNING ) 
	{
	  error(0,0,"Could not initialize HR region...");
	  exit(EXIT_FAILURE);
	}
    }
  else
    {
      if (SetRegion(&region,region_file,VIS_IR) > WARNING ) 
	{
	  error(0,0,"Could not initialize region...");
	  exit(EXIT_FAILURE);
	}
    }

  dims[0] = region.nb_lines;
  dims[1] = region.nb_cols;
  return rank;
}

/*
 * get_channel
 *
 * Gets a channel from MSG data. It fills in the radiance "rad" and
 * the other array of values "ref_or_bt", which is reflectance or
 * brightness temperature depending on the channel. "mask" is an array
 * of booleans for the validity of the values (typically false in
 * space).
 * 
 */

int
get_channel(char* c_time_slot, char* region_file, char* channel_string, float** rad, float** ref_or_bt, unsigned char ** mask)
{
  Psing_region region;
  Seviri_struct seviri;

  YYYYMMDDhhmm time_slot;
  int channel;
  int status;

  /* Parse options */
  strcpy(time_slot,c_time_slot);

  channel = channel_number(channel_string);
  if(channel==-1)
    {
      error(0,0,"Invalid channel.");
      exit(EXIT_FAILURE);
    }

  /* Initialize regions */
  
  if(channel==HRVIS)
    {
      if (SetRegion(&region,region_file,HRV) > WARNING ) 
	{
	  error(0,0,"Could not initialize HR region...");
	  exit(EXIT_FAILURE);
	}
    }
  else
    {
      if (SetRegion(&region,region_file,VIS_IR) > WARNING ) 
	{
	  error(0,0,"Could not initialize region...");
	  exit(EXIT_FAILURE);
	}
    }
  if(rad != NULL)
    status = MSG_read_channel(time_slot,region,&seviri,channel,TRUE);
  else
    status = MSG_read_channel(time_slot,region,&seviri,channel,FALSE);
  if(status == EXIT_FAILURE)
    return EXIT_FAILURE;

  if(CheckSevBand(&seviri)!=pow(2,channel))
    {
      SevFree(seviri);
      fprintf(stderr, 
	      "Unable to read channel %s for %s at %s\n", 
	      channel_string, 
	      region_file, 
	      c_time_slot);
      return EXIT_FAILURE;
    }

  if(rad != NULL)
    copy_and_cast(SevBand(seviri,channel,RAD),rad,region.nb_lines,region.nb_cols);
  if(SevBand(seviri,channel,REFL)!=NULL)
    {
      copy_and_cast(SevBand(seviri,channel,REFL),ref_or_bt,region.nb_lines,region.nb_cols);
      make_mask(SevBand(seviri,channel,REFL),mask,region.nb_lines,region.nb_cols);
    }
  else
    {
      copy_and_cast(SevBand(seviri,channel,BT),ref_or_bt,region.nb_lines,region.nb_cols);
      make_mask(SevBand(seviri,channel,BT),mask,region.nb_lines,region.nb_cols);
    }
  
  SevFree(seviri);
  return EXIT_SUCCESS;
}


/*
 * get_channels
 *
 * Gets all non HR channels from MSG data defined in the bandmask. It fills in
 * the radiance "rad" and the other array of values "ref_or_bt", which is
 * reflectance or brightness temperature depending on the channel. "mask" is an
 * array of booleans for the validity of the values (true for invalid values,
 * typically in space).
 * 
 */

int
get_channels(char* c_time_slot, char* region_file, int bandmask, float*** rad, float*** ref_or_bt, unsigned char *** mask)
{
  Band_mask bands;
  Psing_region region;
  Seviri_struct seviri;

  YYYYMMDDhhmm time_slot;
  int channel;
  int channel_id;
  int band_res;
  char channel_string[10];

  int ch_count = 0;
  int status;

  printf("will prepare band mask.\n");
  fflush(stdout);


  for(channel = 0; channel < NUM_BANDS; channel++)
    if((int)pow(2,channel) & bandmask)
      bands[channel]=TRUE;
    else
      bands[channel]=FALSE;
  bands[HRVIS]=FALSE;
  
  /* Parse options */
  strcpy(time_slot,c_time_slot);

  /* Initialize regions */
  

  printf("will now set region.\n");
  fflush(stdout);

  if (SetRegion(&region,region_file,VIS_IR) > WARNING ) 
    {
      error(0,0,"Could not initialize region...");
      exit(EXIT_FAILURE);
    }
  
  printf("will now MSGread.\n");
  fflush(stdout);


  if(rad != NULL)
    status = MSG_read_channels(time_slot,region,&seviri,bands,TRUE);
  else
    status = MSG_read_channels(time_slot,region,&seviri,bands,FALSE);
  if(status == EXIT_FAILURE)
    {
      error(0,0,"Could not read channel...");
      exit(EXIT_FAILURE);
    }
    
  printf("will now check.\n");
  fflush(stdout);


  band_res = CheckSevBand(&seviri) ^ bandmask;
  
  for(channel = 0; channel < NUM_BANDS; channel++)
    {

      if(band_res & (int)(pow(2,channel)))
	{
	  channel_name_string(channel,channel_string);
	  fprintf(stderr,
		  "Unable to read channel %s for %s at %s\n",
		  channel_string,
		  region_file,
		  c_time_slot);
	}
      else if(bands[channel])
	{
	  if(rad != NULL)
	    copy_and_cast(SevBand(seviri,channel,RAD),rad[ch_count],region.nb_lines,region.nb_cols);
	  if(SevBand(seviri,channel,REFL)!=NULL)
	    {
	      copy_and_cast(SevBand(seviri,channel,REFL),ref_or_bt[ch_count],region.nb_lines,region.nb_cols);
	      make_mask(SevBand(seviri,channel,REFL),mask[ch_count],region.nb_lines,region.nb_cols);
	    }
	  else
	    {
	      copy_and_cast(SevBand(seviri,channel,BT),ref_or_bt[ch_count],region.nb_lines,region.nb_cols);
	      make_mask(SevBand(seviri,channel,BT),mask[ch_count],region.nb_lines,region.nb_cols);
	    }
          ch_count++;
	}
    }
  SevFree(seviri);

  return band_res;
}

/*
 * get_all_channels
 *
 * Gets all non HR channels from MSG data. It fills in the radiance
 * "rad" and the other array of values "ref_or_bt", which is
 * reflectance or brightness temperature depending on the
 * channel. "mask" is an array of booleans for the validity of the
 * values (true for invalid values, typically in space).
 * 
 */

int
get_all_channels(char* c_time_slot, char* region_file, float*** rad, float*** ref_or_bt, unsigned char *** mask)
{
  Band_mask bands;
  Psing_region region;
  Seviri_struct seviri;

  YYYYMMDDhhmm time_slot;
  int channel;
  int channel_id;
  int band_check;
  int band_res;
  char channel_string[10];
  int status;

  for(channel = 0; channel < NUM_BANDS; channel++)
    bands[channel]=TRUE;
  bands[HRVIS]=FALSE;
  
  band_check = pow(2,NUM_BANDS) - 1 - pow(2,HRVIS);

  /* Parse options */
  strcpy(time_slot,c_time_slot);

  /* Initialize regions */
  
  if (SetRegion(&region,region_file,VIS_IR) > WARNING ) 
    {
      error(0,0,"Could not initialize region...");
      exit(EXIT_FAILURE);
    }
  
  if(rad != NULL)
    status = MSG_read_channels(time_slot,region,&seviri,bands,TRUE);
  else
    status = MSG_read_channels(time_slot,region,&seviri,bands,FALSE);
  if(status == EXIT_FAILURE)
    return EXIT_FAILURE;


  band_res = CheckSevBand(&seviri) ^ band_check;
  
  for(channel = 0; channel < NUM_BANDS - 1; channel++)
    {
      switch(channel)
	{
	case 0:
	  channel_id = VIS06;
	  break;
	case 1:
	  channel_id = VIS08;
	  break;
	case 2:
	  channel_id = IR16;
	  break;
	case 3:
	  channel_id = IR39;
	  break;
	case 4:
	  channel_id = WV62;
	  break;
	case 5:
	  channel_id = WV73;
	  break;
	case 6:
	  channel_id = IR87;
	  break;
	case 7:
	  channel_id = IR97;
	  break;
	case 8:
	  channel_id = IR108;
	  break;
	case 9:
	  channel_id = IR120;
	  break;
	case 10:
	  channel_id = IR134;
	  break;
	}


      if(band_res & (int)(pow(2,channel)))
	{
	  channel_name_string(channel,channel_string);
	  fprintf(stderr,
		  "Unable to read channel %s for %s at %s\n",
		  channel_string,
		  region_file,
		  c_time_slot);
	  make_blank_mask(mask[channel],region.nb_lines,region.nb_cols);
	}
      else
	{
	  if(rad != NULL)
	    copy_and_cast(SevBand(seviri,channel_id,RAD),rad[channel],region.nb_lines,region.nb_cols);
	  if(SevBand(seviri,channel_id,REFL)!=NULL)
	    {
	      copy_and_cast(SevBand(seviri,channel_id,REFL),ref_or_bt[channel],region.nb_lines,region.nb_cols);
	      make_mask(SevBand(seviri,channel_id,REFL),mask[channel],region.nb_lines,region.nb_cols);
	    }
	  else
	    {
	      copy_and_cast(SevBand(seviri,channel_id,BT),ref_or_bt[channel],region.nb_lines,region.nb_cols);
	      make_mask(SevBand(seviri,channel_id,BT),mask[channel],region.nb_lines,region.nb_cols);
	    }
	}
    }
  SevFree(seviri);

  return band_res;
}


/*
 *
 * lat_lon_from_region
 *
 */

void
lat_lon_from_region(char * region_file, char * channel_string, float ** lat, float ** lon)
{

  Float_32 ** MSG_lat;
  Float_32 ** MSG_lon;
  
  Psing_region region;

  int channel;

  channel = channel_number(channel_string);
  if(channel==-1)
    {
      error(0,0,"Invalid channel.");
      exit(EXIT_FAILURE);
    }

  if(channel==HRVIS)
    {
      if (SetRegion(&region,region_file,HRV) > WARNING ) 
	{
	  error(0,0,"Could not initialize HR region...");
	  exit(EXIT_FAILURE);
	}
      GetLatLon(region, HRVIS, &MSG_lat, &MSG_lon);
    }
  else
    {
      if (SetRegion(&region,region_file,VIS_IR) > WARNING ) 
	{
	  error(0,0,"Could not initialize region...");
	  exit(EXIT_FAILURE);
	}
      GetLatLon(region, VIS_IR, &MSG_lat, &MSG_lon);
    }

  copy_and_cast(MSG_lat, lat, region.nb_lines, region.nb_cols);
  copy_and_cast(MSG_lon, lon, region.nb_lines, region.nb_cols);

  FreeLatLon(region, MSG_lat, MSG_lon);

}
