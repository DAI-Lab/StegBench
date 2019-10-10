/***************************************************************
Title: Crypture 2.0
Author: Jerramy Gipson

Features:
 Encrypts and stores a file into a bitmap image file.
 Command line interface, with small executable footprint.
 Header information is encrypted as well.
 Randomizes low order bits of image with non-determinable seed, 
   to prevent detection of steganography.
 Interlaces bit writes by password determined seperation distance, 
   to hinder brute force encryption cracking.
 Uses 1024 bit encryption key.  
 Passwords up to 128 characters long are supported.

Requirements:
 32 bit Windows OS.
 The bitmap file must be a standard Windows bitmap, 24 bits per pixel, uncompressed.
 The bitmap file must be more than 8 times larger than the file to encrypt.

License:
 This software is open source and freeware.  
 You may do whatever you want with this software, except for holding me 
 liable for any damage which arises from your usage of it.
 If it eats your hard-disk, cracks into NASA, and starts a nuclear war,
 don't come crying to me!

Build Tools:
 This was built on Windows XP, with the Tiny C Compiler, version 0.9.23,
 using the following command:

 C:\tcc-0.9.23\tcc> tcc -o crypture.exe -L..\lib -I..\include crypture.c

Usage:
 C:\> crypture source.bmp
 Password: ?

   This will use the provided password to attempt a decryption on source.bmp.
   The encrypted file will be extracted and written to the current directory.

 C:\> crypture dest.bmp source.any
 Password: ?

   This will encrypt and inject source.any into dest.bmp, using the provided password.
   The source file will remain untouched.

 The password may be redirected from a text file, for ease of use.
 It should be terminated by a newline.

 C:\> crypture dest.bmp source.any < key.txt
 C:\> crypture source.bmp < key.txt

****************************************************************/

#include <malloc.h>
#include <io.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/timeb.h>
#include <stdio.h>

typedef unsigned char  UInt8;
typedef unsigned short UInt16;
typedef unsigned       UInt32;

typedef struct
{
    int handle;
    char* name;
    UInt32 size;
    UInt8* data;
} File_Info;


File_Info hidden_file = {-1,0,0,0};
File_Info bitmap_file = {-1,0,0,0};

#define BITMAP_DATA_OFFSET 54

void EXIT(int val)
{
    if (bitmap_file.handle != -1) _close(bitmap_file.handle); else printf("Bitmap file not openned.\n");
    if (hidden_file.handle != -1) _close(hidden_file.handle); else printf("Data file not openned.\n");
    if (bitmap_file.data != 0) free(bitmap_file.data); else printf("Failed to allocate bitmap memory.\n");
    if (hidden_file.data != 0) free(hidden_file.data); else printf("Failed to allocate data memory.\n");

    exit(val);
}


#define NUM_SEEDS 32 /* a power of 2 please */
UInt32  rand_seeds[NUM_SEEDS];
int rand_index = 0;
char password[1024];
UInt8 skip_distance;

//For this to work right, create_seed() must have been previously called.
UInt16 my_rand()
{
     rand_seeds[rand_index % NUM_SEEDS] 
         = rand_seeds[rand_index % NUM_SEEDS] * 1103515245 + 12345;
     return (rand_seeds[rand_index++ % NUM_SEEDS] >> 16);
}

void create_seed(char* string)
{
    int i;
    for (i = 0; i < NUM_SEEDS; ++i)
    {
        rand_seeds[i] = 0x538F3EA1 * (i+1);

        char* seed_string = string;
        while(*seed_string != 0)
        {
            rand_seeds[i] = rand_seeds[i] * (UInt8)(*seed_string) 
                          + ~(UInt8)(*seed_string);
            seed_string++;
        }
    }

    rand_index = 0;  //to reset rand().

    skip_distance = 0;
    while (skip_distance == 0)
        skip_distance = my_rand() % 256;
}


UInt8* index_raw_data(UInt32 index)
{
    UInt32 raw_size = (bitmap_file.size - BITMAP_DATA_OFFSET);
    UInt32 skips_per_cycle = raw_size / skip_distance;
    if (skips_per_cycle == 0) return 0;

    UInt32 skip_cycle = index / skips_per_cycle;
    if (skip_cycle >= skip_distance) return 0;        //the entire skip space has been filled.

    UInt32 skip_offset = index % skips_per_cycle; //which skip in the cycle?
    return bitmap_file.data + BITMAP_DATA_OFFSET + skip_cycle + (skip_offset*skip_distance);
}


UInt32 get_max_bytes()
{
    UInt32 raw_size = bitmap_file.size - BITMAP_DATA_OFFSET;
    return (raw_size - raw_size % skip_distance) / 8;
}


void randomize_image()
{
    char chaos_key[1024];
    struct _timeb timestruct;

    strcpy(chaos_key, password);
    _ftime(&timestruct);
    *(UInt16*)chaos_key = timestruct.millitm;
    if (strlen(password) < 2) chaos_key[2] = 0;

    create_seed(chaos_key);

    UInt32 num_bits = bitmap_file.size - BITMAP_DATA_OFFSET;
    UInt8* raw_data = bitmap_file.data + BITMAP_DATA_OFFSET;

    while (num_bits-- > 0)
    {
        *raw_data &= 0xFE;
        *raw_data |= ((my_rand()>>2) & 0x0001);
        ++raw_data;
    }
}


void load_file(char* filename, File_Info* file_info, UInt32 header_size)
{
    if (filename == 0)
    {
        printf("Bad filename.\n");
        EXIT(-1);
    }
    file_info->name = filename;

    if ((file_info->handle = _open(filename, (_O_BINARY | _O_RDWR))) == -1)
    {
        printf("Error openning file: %s\n", filename);
        EXIT(-1);
    }
 
    if ((file_info->size = _filelength(file_info->handle)) < 1)
    {
        printf("Unable to determine the file size: %s\n", filename);
        EXIT(-1);
    }

    if ((file_info->data = (UInt8*)malloc(header_size + file_info->size)) == 0)
    {
        printf("Unable to allocate memory to store file: %s\n", filename);
        EXIT(-1);
    }

    _read(file_info->handle, file_info->data + header_size, file_info->size);
}


void load_bitmap(char* filename)
{
    load_file(filename, &bitmap_file, 0);

    UInt32 file_size  = *(UInt32*)(bitmap_file.data +  2);
    UInt32 data_start = *(UInt32*)(bitmap_file.data + 10);
    UInt16 numbits    = *(UInt16*)(bitmap_file.data + 28);
    UInt32 compress   = *(UInt32*)(bitmap_file.data + 30);

    if ((*(UInt16*)(bitmap_file.data)!= 19778)  // signature check
     || (data_start != BITMAP_DATA_OFFSET) //uses a color table.
     || (numbits != 24)    //Currently use only 24 bit bitmaps.
     || (compress != 0)    //Absolutely don't support compression.
     || (file_size != bitmap_file.size))  //size consistancy
    {
        printf("Not a bitmap, or unsupported bitmap format: %s\n", filename);
        EXIT(-1);
    }
}


void load_hidden_file(char* filename)
{
    UInt32 header_size = 4/*signature*/ + 4/*size*/ + strlen(filename) + 1/*NULL*/;

    load_file(filename, &hidden_file, header_size);

    *(UInt32*)hidden_file.data = 0x12345678;
    *(UInt32*)(hidden_file.data + 4) = hidden_file.size;
    strcpy(&hidden_file.data[8], hidden_file.name);
}


void extract_data(char* bitmap_filename)
{
    load_bitmap(bitmap_filename);

    create_seed(password);

    UInt32 num_bytes = get_max_bytes();

    hidden_file.data = malloc(num_bytes);
    if (hidden_file.data == 0)
    {
        printf("Unable to allocate memory to store hidden file.\n");
        EXIT(-1);
    }

    int i; int j;
    for (i = 0; i < num_bytes; ++i)
    {
        hidden_file.data[i] = 0;
        for (j = 0; j < 8; ++j)
        {
            UInt8* raw = index_raw_data(i*8+j);
            hidden_file.data[i] <<= 1;
            hidden_file.data[i] |= (*raw & 0x01);
        }

        hidden_file.data[i] = (UInt8)(hidden_file.data[i] ^ my_rand());
    }

    if (*(UInt32*)hidden_file.data != 0x12345678)
    {
        printf("Invalid password.\n");
        EXIT(-1);
    }
    
    hidden_file.size = *(UInt32*)(&hidden_file.data[4]);
    hidden_file.name = &hidden_file.data[8];

    hidden_file.handle = _open(hidden_file.name, (_O_BINARY | _O_CREAT | _O_WRONLY), (_S_IREAD | _S_IWRITE));
    if (hidden_file.handle == -1)
    {
        printf("Unable to create data file.\n");
        EXIT(-1);
    }

    UInt32 header_size = 4/*signature*/ + 4/*size*/ + strlen(hidden_file.name) + 1/*NULL*/;
    _write(hidden_file.handle, hidden_file.data + header_size, hidden_file.size);

    printf("Created %d byte file: %s\n", hidden_file.size, hidden_file.name);
}


//Modding to move bitmap over to universal file struct endded here.
void insert_data(char* bitmap_filename, char* hidden_filename)
{
    load_bitmap(bitmap_filename);
    load_hidden_file(hidden_filename);

    randomize_image();
    create_seed(password);

    UInt32 num_bytes = hidden_file.size + 8/*header*/ + strlen(hidden_file.name) + 1/*NULL*/;
    if (get_max_bytes() < num_bytes)
    {
        printf("Bitmap file not large enough to contain hidden file.\n");
        EXIT(-1);
    }

    int i; int j;
    for (i = 0; i < num_bytes; ++i)
    {
        hidden_file.data[i] = (hidden_file.data[i] ^ my_rand());

        for (j = 0; j < 8; ++j)
        {
            UInt8* raw = index_raw_data(i*8+j);

            *raw &= 0xFE;
            *raw |= ((char)hidden_file.data[i] < 0); //checks the high order bit.
            hidden_file.data[i] <<= 1;
        }
    }

    _lseek(bitmap_file.handle, 0, SEEK_SET); //back to the beginning.
    _write(bitmap_file.handle, bitmap_file.data, bitmap_file.size);
}


void main(int argc, char* argv[])
{
    int i;

    if ((argc <= 1) || (argc >= 4))
    {
        printf("\n");
        printf("----------------------------------------------------------------------\n");
        printf("Crypture 2.0 - by Jerramy Gipson\n\n");
        printf("License: This software is open source freeware.\n");
        printf("         No liability assumed by author.\n\n");
        printf("Usage: crypture <dst_file.bmp> <src_file.any>   (inserts)\n");
        printf("       crypture <src_file.bmp>                  (extracts)\n\n");
        printf("You will be prompted for a password.\n");
        printf("You may also use a keyfile for long passwords:\n");
        printf("       crypture <dst_file.bmp> <src_file.any>  < <keyfile.txt>\n");
        printf("\nThe bitmap file must be more than 8 times larger than the data file.\n");
        printf("----------------------------------------------------------------------\n");
        exit(-1);
    }

    printf("Password: ");
    if (fgets(password, 1024, stdin) == 0) 
    {
        printf("Error getting password.\n");
        exit(-1);
    }

    if (argc == 2)
    {
        //decrypting hidden file from bitmap.
        extract_data(argv[1]);
    }
    else if (argc == 3)
    {
        //encrypting hidden file into bitmap.
        insert_data(argv[1], argv[2]);
    }

    printf("Done.\n");
    EXIT(0);
}



