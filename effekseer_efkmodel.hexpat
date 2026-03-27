// Effekseer .efkmodel, used in my singing monsters
// Written by Somwonere

u32 var_version = 0;

struct Position{
    float PosX; // inverted x
    float PosY;
    float PosZ;
    float NrmX;
    float NrmY;
    float NrmZ;
    float BinrmX;
    float BinrmY;
    float BinrmZ;
    float TngX;
    float TngY;
    float TngZ;
    float PosU;
    float PosV;
    if (var_version != 0){
        u8 ClrR;
        u8 ClrG;
        u8 ClrB;
        u8 ClrA;
    }
};

struct Index{
    u32 Idx1;
    u32 Idx2;
    u32 Idx3;
};

struct Efkmodel{
    u32 version;
    var_version = version;
    if (var_version == 0) $ = 0x8;
    else $ = 0x10;
    u32 pos_count;
    Position pos_data[pos_count];
    u32 idx_count;
    Index index[idx_count];
};

Efkmodel efkmodel @ 0x0;