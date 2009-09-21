#include <string.h>
#include <error.h>
#include <libnwc.h>
#include <sevext.h>
#include <hlhdf.h>
#include "libmsg_channel.h"

/*
 *
 * MSG_read_channel
 *
 * Uses the MSG library to read channels from METEOSAT (Seviri
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
		 int channel)
{
  int i,j;
  Band_mask bands;

  for(j=0;j<NUM_BANDS;j++)
    bands[j]=FALSE;
  bands[channel]=TRUE;
  
   /*
   **   Initialise 
   */   

   if(channel==HRVIS)
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
   if(channel == (HRVIS))
     {
       if ((i=SevReadHRV(region, seviri)) > (WARNING))
	 {
	   SevFree(*seviri);
	   return EXIT_FAILURE;
	 }
     }
   else
     {
       if ((i=SevRead(region, seviri,bands)) > (WARNING))
	 {
	   SevFree(*seviri);
	   return EXIT_FAILURE;
	 }
     }
   
   /*
   **   Convert into reflectances, radiances and bt
   */


   if(channel==HRVIS || channel==VIS06 || 
      channel==VIS08 || channel==IR16 ||
      channel==IR39 || channel==WV62 ||
      channel==WV73 || channel==IR87 || 
      channel==IR97 || channel==IR108 ||
      channel==IR120 || channel==IR134)
     SevCalibrate(seviri,channel);

   if(channel==HRVIS || channel==VIS06 || 
      channel==VIS08 || channel==IR16)
     SevCalRefl(seviri,channel);

   if(channel==IR39 || channel==WV62 ||
      channel==WV73 || channel==IR87 ||
      channel==IR97 || channel==IR108 ||
      channel==IR120 || channel==IR134)
     SevConvert(seviri,channel);

   return EXIT_SUCCESS;
}


/*
 *
 * HL_add_string_attribute
 *
 * Uses HLHDF library to write a string attribute to a hdf5 file.
 * 
 */

int 
HL_add_string_attribute(HL_NodeList* aList,char* attribute, char* value)
{
  HL_Node* aNode=NULL;
  int status;
  
  status=HLNodeList_addNode(aList, (aNode = HLNode_newAttribute(attribute)));

  if(status != 1)
    {
      HLNodeList_free(aList);
      exit(FAILURE);
    }
  
  status=HLNode_setScalarValue(aNode,strlen(value),(unsigned char*)value,"string",-1);
  
  if(status != 1)
    {
      HLNodeList_free(aList);
      exit(FAILURE);
    }
  
  return EXIT_SUCCESS;
}


/*
 *
 * save_valid_data_mask
 *
 * Stores a boolean mask discriminating invalid measurements in an
 * HDF5 file.
 * 
 */


int
save_valid_data_mask(HL_NodeList* aList, char * nodename,Float_32** msg_data, int nb_lines, int nb_cols)
{
  HL_Node* aNode=NULL;
  hsize_t dims[2];
  char nodestring[256];
  unsigned char *data;
  int i,j;
  
  if (msg_data == NULL) 
    {
      fprintf(stdout,"No %s to save for this channel... skipping\n",nodename);
      fflush(stdout);
      return EXIT_SUCCESS;
    } 
  else 
    {
      sprintf(nodestring,"/%s",nodename);
      HLNodeList_addNode(aList,(aNode = HLNode_newDataset(nodestring)));
                  
      if(!(data=calloc(nb_lines*nb_cols,sizeof(Float_32))))
	{
	  HLNodeList_free(aList);
	  error(0,0,"Could not allocate memory.\n");
	  return EXIT_FAILURE;
	}

    for(i=0; i<nb_lines; i++)
      {
	for (j=0; j<nb_cols; j++)
	  {
	    if(msg_data[i][j]==SEVIRI_MISSING_VALUE)
	      data[i*nb_cols+j]=0;
	    else
	      data[i*nb_cols+j]=1;
	  }
      }
    
    dims[0]=nb_lines;
    dims[1]=nb_cols;
    HLNode_setArrayValue(aNode,sizeof(unsigned char),2,dims,(unsigned char*)data,"uchar",-1);
    
    return EXIT_SUCCESS;
  }

}


/*
 *
 * save_data_as_image
 *
 * Stores data as an image in an HDF5 file.
 * 
 */

int
save_data_as_image(HL_NodeList* aList, char * nodename,Float_32** msg_data, int nb_lines, int nb_cols)
{
  HL_Node* aNode=NULL;
  hsize_t dims[2];
  char nodestring[256];
  Float_32 zero=0.0;
  Float_32 *data;
  Float_32 max=0.0;
  Float_32 minmaxrange[2];
  hsize_t minmaxdim[1]={2};
  int i,j;
  
  if (msg_data == NULL) 
    {
      fprintf(stdout,"No %s to save for this channel... skipping\n",nodename);
      fflush(stdout);
      return EXIT_SUCCESS;
    } 
  else 
    {
      sprintf(nodestring,"/%s",nodename);
      HLNodeList_addNode(aList,(aNode = HLNode_newDataset(nodestring)));
      
      if(!(data=(Float_32 *)malloc(nb_lines*nb_cols*sizeof(Float_32))))
	{
	  HLNodeList_free(aList);
	  error(0,0,"Could not allocate memory.\n");
	  return EXIT_FAILURE;
	}
      
      for(i=0; i<nb_lines; i++)
	{
	  for (j=0; j<nb_cols; j++)
	    {
	      data[i*nb_cols+j]=msg_data[i][j];
	      if(max<msg_data[i][j])
		max=msg_data[i][j];
	    }
	}
      
      dims[0]=nb_lines;
      dims[1]=nb_cols;
      HLNode_setArrayValue(aNode,sizeof(Float_32),2,dims,(unsigned char*)data,"float",-1);
      
      sprintf(nodestring,"/%s/CLASS",nodename);
      HL_add_string_attribute(aList, nodestring, "IMAGE");
      
      sprintf(nodestring,"/%s/IMAGE_VERSION",nodename);
      HL_add_string_attribute(aList, nodestring, "1.2");
      
      sprintf(nodestring,"/%s/IMAGE_SUBCLASS",nodename);
      HL_add_string_attribute(aList, nodestring, "IMAGE_GRAYSCALE");
      
      sprintf(nodestring,"/%s/IMAGE_WHITE_IS_ZERO",nodename);
      HLNodeList_addNode(aList,(aNode = HLNode_newAttribute(nodestring)));
      HLNode_setScalarValue(aNode, sizeof(Float_32),(unsigned char*)&zero,"uchar",-1);
      
      minmaxrange[0]=0.0;
      minmaxrange[1]=max*2+1;
      sprintf(nodestring,"/%s/IMAGE_MINMAXRANGE",nodename);
      HLNodeList_addNode(aList,(aNode = HLNode_newAttribute(nodestring)));
      HLNode_setArrayValue(aNode, sizeof(Float_32),1,minmaxdim,(unsigned char*)minmaxrange,"float",-1);
      
      return EXIT_SUCCESS;

    } 
}


/*
 *
 * save2h5
 *
 * Saves a MSG channel to hdf5 format.
 * 
 */

int
save2h5(Psing_region region,Seviri_struct *seviri,char* time_slot,int channel)
{
  HL_NodeList* aList=NULL;
  HL_Compression compression;
  char filename[256];

  /* Initialize the HL-HDF library */
  HL_init();  

  /* Activate debugging */
  HL_setDebugMode(2); 

  if(!(aList = HLNodeList_new())) {
    error(0,0,"Failed to allocate HL nodelist");
    goto fail;
  }

  save_valid_data_mask(aList,"MASK",SevBand(*seviri,channel,RAD),region.nb_lines,region.nb_cols);

  save_data_as_image(aList,"RAD",SevBand(*seviri,channel,RAD),region.nb_lines,region.nb_cols);
  save_data_as_image(aList,"REFL",SevBand(*seviri,channel,REFL),region.nb_lines,region.nb_cols);
  save_data_as_image(aList,"BT",SevBand(*seviri,channel,BT),region.nb_lines,region.nb_cols);

  sprintf(filename,"%s_%02d.h5",time_slot,channel);
  HLNodeList_setFileName(aList, filename);
  
  HLCompression_init(&compression, CT_ZLIB);
  compression.level = 6;
  HLNodeList_write(aList,NULL,&compression);

  HLNodeList_free(aList);
  return EXIT_SUCCESS; 
 fail:
  HLNodeList_free(aList);
  return EXIT_FAILURE;

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
	out[i][j] = (in[i][j] != SEVIRI_MISSING_VALUE);
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
 * brightness temperature depending on the channel. "is_ref" tells if
 * it is reflectance or not. "mask" is an array of booleans for the
 * validity of the values (typically false in space).
 * 
 */

void
get_channel(char* c_time_slot, char* region_file, char* channel_string, float** rad, float** ref_or_bt, int * is_ref, unsigned char ** mask)
{
  Psing_region region;
  Seviri_struct seviri;

  YYYYMMDDhhmm time_slot;
  int channel;

  /* Parse options */
  strcpy(time_slot,c_time_slot);

  channel = channel_number(channel_string);
  if(channel==-1)
    {
      SevFree(seviri);
      error(0,0,"Invalid channel.");
      exit(EXIT_FAILURE);
    }

  /* Initialize regions */
  
  if(channel==HRVIS)
    {
      if (SetRegion(&region,region_file,HRV) > WARNING ) 
	{
	  SevFree(seviri);
	  error(0,0,"Could not initialize HR region...");
	  exit(EXIT_FAILURE);
	}
    }
  else
    {
      if (SetRegion(&region,region_file,VIS_IR) > WARNING ) 
	{
	  SevFree(seviri);
	  error(0,0,"Could not initialize region...");
	  exit(EXIT_FAILURE);
	}
    }

  MSG_read_channel(time_slot,region,&seviri,channel);
  if(CheckSevBand(&seviri)!=pow(2,channel))
    {
      SevFree(seviri);
      error(0,0,"Unable to read channel");
      exit(EXIT_FAILURE);
    }
  copy_and_cast(SevBand(seviri,channel,RAD),rad,region.nb_lines,region.nb_cols);
  if(SevBand(seviri,channel,REFL)!=NULL)
    {
      copy_and_cast(SevBand(seviri,channel,REFL),ref_or_bt,region.nb_lines,region.nb_cols);
      *is_ref = 1;
    }
  else
    {
      copy_and_cast(SevBand(seviri,channel,BT),ref_or_bt,region.nb_lines,region.nb_cols);
      *is_ref = 0;
    }
  make_mask(SevBand(seviri,channel,RAD),mask,region.nb_lines,region.nb_cols);
  SevFree(seviri);
}


void
print_usage(char *prog_name)
{
  fprintf(stderr,"Usage: %s YYYYMMDDhhmm region_conf_file channel\nchannel should be one of HRVIS, VIS06, VIS08, IR16, IR39, WV62, WV73, IR87, IR97, IR108, IR120, IR134, or 1 to 12.\n",prog_name);
  fflush(stderr);
}


int
main(int argc, char* argv[])
{
  Psing_region region;
  Seviri_struct seviri;

  YYYYMMDDhhmm time_slot;
  char* region_file;
  char* channel_string;
  int channel;

  if (argc!=4) 
    {
      print_usage(argv[0]);
      exit(FAILURE);
    }


  /* Parse options */
  strcpy(time_slot,argv[1]);

  region_file = (char *)malloc((strlen(argv[2])+1)*sizeof(char));
  strcpy(region_file,argv[2]);

  channel_string = (char *)malloc((strlen(argv[3])+1)*sizeof(char));
  strcpy(channel_string,argv[3]);
  
  channel = channel_number(channel_string);
  if(channel==-1)
    {
      SevFree(seviri);
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

  MSG_read_channel(time_slot,region,&seviri,channel);
  if(CheckSevBand(&seviri)==pow(2,channel))
    save2h5(region,&seviri,time_slot,channel);
  SevFree(seviri);
  if(CheckSevBand(&seviri)!=pow(2,channel))
    {
      error(0,0,"Unable to read channel");
      exit(EXIT_FAILURE);
    }

  return EXIT_SUCCESS;
}
