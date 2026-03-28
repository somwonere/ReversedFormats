// Google's Playground .lullmodel (Lullaby) (also sometimes .fplmesh)
// Original importer by Bigchillghost


#pragma array_limit 3000000
#pragma pattern_limit 3000000
// these models are usually very high poly

struct Faces{
    u16 Tri1;
    u16 Tri2;
    u16 Tri3;
};

struct Faces_u32{
    u32 Tri1;
    u32 Tri2;
    u32 Tri3;
};

struct Verts{
    float VertX;
    float VertY;
    float VertZ;
    if (var_VertSize == 60 || var_VertSize == 76) // some avengers
        $ += 4;
    if (var_VertSize > 32){ // "> 32" fixes for avengers-captainmarvelglow_fire_03
        float VertU;
        float VertV;
    }
    float NormX;
    float NormY;
    float NormZ;
    if (var_VertSize > 32){
        float TangX; // don't know what tangents are yet
        float TangY;
        float TangZ;
        float Unknown; // we are number 1, probably can be skipped
    }
    if (var_VertSize == 72 || var_VertSize == 76) // __default_mesh.lullmodel and japanese_phrases fix
        $ += 0x10;
    u8 Idx1; // i now take back what i said about cellfish's model format (8 bytes per skinning)
    u8 Idx2;
    u8 Idx3;
    u8 Idx4;
    u8 Wgt1;
    u8 Wgt2;
    u8 Wgt3;
    u8 Wgt4;
};


struct BoneMtrx{
    float Mtrx01;
    float Mtrx02;
    float Mtrx03;
    float Mtrx04;
    float Mtrx05;
    float Mtrx06;
    float Mtrx07;
    float Mtrx08;
    float Mtrx09;
    float Mtrx10;
    float Mtrx11;
    float Mtrx12;
    // still don't know how matrixes work but used inverse transform on amateur skeleton hunter
};

struct BoneParent{
    u8 bnparent[0];
};

struct BoneNames{
    u32 nameLen;
    char name[nameLen];
    $ += 4-(nameLen%4);
};


struct MatSep{
    u32 Srt;
    u32 End;
};

u32 var_VertSize = 0;

struct Lullmodel{
    u32 headerVersion; // is 0x20 in foodmoji models
    
    // Bones
    if (headerVersion == 0x1C) $ += 0x1C;
    else if (headerVersion == 0x20) $ += 0x24;
    u32 boneOffset1;
    $ += boneOffset1; // don't know what the skipped bytes are for
    u32 boneOffset2;
    $ += boneOffset2-4;
    u32 boneCount;
    BoneMtrx boneMtrx[boneCount];
    u32 Parent_boneCount;
    u8 boneParent[Parent_boneCount];
    $ += (4-Parent_boneCount)%4;
    u32 Unknown1_boneCount;
    u32 Unknown1[Unknown1_boneCount];
    BoneNames boneNames[boneCount]; // the order is reversed when applied onto bones
    $ += 4;
    u32 chunkOffset1;
    $ += chunkOffset1 + 4;
    u32 chunkOffset2;
    
    u32 Abs_MappingOffset = $+chunkOffset2-4;
    $ += 0x8;
    u32 ModelOffset;
    u32 Abs_ModelOffset = $+ModelOffset-4;
    $ += 0xC;
    u32 VertCount;
    
    
    $ = Abs_MappingOffset;
    u32 mapping_boneCount;
    u8 mapping[mapping_boneCount];
    $ += 4-(mapping_boneCount%4);
    
    $ = Abs_ModelOffset;
    
    // Material Separator
    u32 MatCount;
    MatSep matSep[MatCount];
    
    u32 VertSize = 0;
    
    // Mesh
    u32 faceCount;
    if (VertCount < 0x10000)
        Faces faces[faceCount/3];
    else
        Faces_u32 faces[faceCount/3];
    $ += (4-$)%4;
    u32 allVertSize;
    var_VertSize = allVertSize / VertCount;
    Verts verts[VertCount];
    
};

Lullmodel lullmodel @ 0x0;
