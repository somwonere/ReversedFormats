// cellfish's .model file for their wallpaper apps, spoiler... it doesn't have bone parenting
// written by somwonere



struct Header {
    char header[4];
    be u32 version; // version maybe?
    be u32 vert_count;
    be u32 tags_frames; // will not look into animation files
    be u32 tags_frames2;
};



struct Wind_data {
    be u16 wind1;
    be u16 wind2;
    be u16 wind3;
};

struct Text_data {
    be float textU;
    be float textV;
};

struct Skin_data {
    be u8 skinIDX1;
    be u8 skinIDX2;
    be u8 skinIDX3;
    be u8 skinIDX4;
    //weights must add up to 256, but i guess their own converter was very janky causing it to not and be close
    be u8 skinWGT1;
    be u8 skinWGT2;
    be u8 skinWGT3;
    be u8 skinWGT4;
};

struct Vert_data{ // divide it by the scale var
    be s16 vertX;
    be s16 vertY;
    be s16 vertZ;
};

struct Norm_data{
    be s8 normX;
    be s8 normY;
    be s8 normZ;
};

struct Tags_data{
    char tags_name[16];
    be float tags_x;
    be float tags_y;
    be float tags_z;
    be float tags_unknown1; // don't know about matrixes yet, also code from decompiling the apk says that these are all floats and no parenting
    be float tags_unknown2;
    be float tags_unknown3;
    be float tags_unknown4;
    be float tags_unknown5;
    be float tags_unknown6;
};

struct bmdl_data {
    
    char wind_header[4]; // never heard someone call faces "wind" (why)
    be u32 wind_count;
    $ += 0x8;
    Wind_data wind_data[wind_count];
    $ += 0x4;
    
    char text_header[4]; // now we're getting to uvs now
    be u32 text_vert_count; 
    $ += 0x8;
    Text_data text_data[text_vert_count];
    $ += 0x4;
    
    char skin_header[4]; // skinning... but it's now 8 bytes per vertex, cheap but effective
    if (skin_header == "SKIN") {
        be u32 skin_vert_count; 
        $ += 0x8;
        Skin_data skin_data[skin_vert_count];
        $ += 0x4;
    } else {
        $ -= 0x4;
    }
    
    char vert_header[4]; // vertecies finally
    be u32 vert_count; 
    be float scale; // weird that you must divide by it to make it correct.
    Vert_data vert_data[vert_count];
    $ += 0x4;
    
    char norm_header[4]; // on to the normals
    be u32 norm_vert_count; 
    $ += 0x8;
    Norm_data norm_data[norm_vert_count];
    $ += 0x4;
    
    char tags_header[4]; // who calls bones tags?
    be u32 tags_count; 
    $ += 0x8;
    Tags_data tags_data[tags_count];
    $ += 0x4;
};

Header header @ 0x0;

bmdl_data bmdl_data @ 0x20;