extern float ** allocate_float_array(int lines, int cols);
extern unsigned char ** allocate_uchar_array(int lines, int cols);

extern void get_channel(char* c_time_slot, char* region_file, char* channel_string, float** rad, float** ref_or_bt, int * is_ref, unsigned char ** mask);

extern int get_channel_dims(char * region_file, char * channel_string, int * dims);
