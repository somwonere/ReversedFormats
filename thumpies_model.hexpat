// thumpies .bin model
// written by somwonere
// acknowledgment: https://github.com/iestyn129/Thumpie2Obj/blob/master/thumpie2obj.py

struct VtxData{
    float VtxX; // x is inverted in-game
    float VtxY;
    float VtxZ;
    float VtxU;
    float VtxV;
    u8 ClrR; // another assumed unused feature that is all FFFFFF00
    u8 ClrG;
    u8 ClrB;
    $ += 0x1;
};

struct FceData{
    u32 Fce1;
    u32 Fce2;
    u32 Fce3;
};

struct Model{
    u32 Header; // why i think it's always 1 is because bbb was planning submeshes but never did
    u32 texNamesize; // has one null byte
    char texName[texNamesize-1];
    $ += 4-((texNamesize-1)%4);
    u32 Header2; // another 1 bytes the dust
    u32 VtxCount;
    VtxData vtxdata [VtxCount];
    u32 FceCount;
    FceData fcedata [FceCount];
    u32 MiscCount; // the butterflies models don't have it all 0's, i feel like they are morphs
};

Model model @ 0x0;