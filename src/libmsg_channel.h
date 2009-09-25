extern float ** allocate_float_array(int lines, int cols);
extern unsigned char ** allocate_uchar_array(int lines, int cols);

extern float ***allocate_3D_float_array(int lines, int cols);
extern unsigned char ***allocate_3D_uchar_array(int lines, int cols);

extern void free_2D_float_array(float ** array, int lines);
extern void free_2D_uchar_array(unsigned char ** array, int lines);

extern void free_3D_float_array(float *** array, int lines);
extern void free_3D_uchar_array(unsigned char *** array, int lines);

extern int get_channel(char* c_time_slot, char* region_file, char* channel_string, float** rad, float** ref_or_bt, unsigned char ** mask);
extern int get_all_channels(char* c_time_slot, char* region_file, float*** rad, float*** ref_or_bt, unsigned char *** mask);

extern int get_channel_dims(char * region_file, char * channel_string, int * dims);


extern void lat_lon_from_region(char * region_file, char * channel_string, float ** lat, float ** lon);

extern float missing_value();
