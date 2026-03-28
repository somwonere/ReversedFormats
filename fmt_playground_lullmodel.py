# Google's Playground .lullmodel (Lullaby)
# Written by Somwonere
# Based on plugin without rig support by Bigchillghost

from inc_noesis import *

#registerNoesisTypes is called by Noesis to allow the script to register formats.
#Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
    handle = noesis.register("Google's Playground Model (Lullaby)", ".lullmodel")
    noesis.setHandlerTypeCheck(handle, lullCheckType)
    noesis.setHandlerLoadModel(handle, lullLoadModel)
    handle = noesis.register("Google's Playground Model (Lullaby)", ".fplmesh") # sometimes renamed to this format
    noesis.setHandlerTypeCheck(handle, lullCheckType)
    noesis.setHandlerLoadModel(handle, lullLoadModel)
    
    noesis.logPopup()
    #print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
    return 1

def lullCheckType(data):
    bs = NoeBitStream(data)
    header_version = bs.readUInt()
    if header_version == 0x1C: return 1
    elif header_version == 0x20: return 1
    return 0

def lullLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    
    header_version = bs.readUInt()
    if header_version == 0x1C: bs.seek(0x20, NOESEEK_ABS)
    elif header_version == 0x20: bs.seek(0x28, NOESEEK_ABS)
    bs.seek(bs.readUInt(), NOESEEK_REL)
    bs.seek(bs.readUInt()-4, NOESEEK_REL)
    boneCount = bs.readUInt()
    print("Bone Count: " + str(boneCount))
    
    bone_mtrx = []
    for x in range(boneCount):
        a = bs.readFloat()
        b = bs.readFloat()
        c = bs.readFloat()
        d = bs.readFloat()
        e = bs.readFloat()
        f = bs.readFloat()
        g = bs.readFloat()
        h = bs.readFloat()
        i = bs.readFloat()
        j = bs.readFloat()
        k = bs.readFloat()
        l = bs.readFloat()
        bone_val = NoeMat44((NoeVec4((a,e,i,0)),NoeVec4((b,f,j,0)),NoeVec4((c,g,k,0)),NoeVec4((d,h,l,1.0)))).inverse()
        bone_val = bone_val.toMat43()
        
        #print(str(x))
        #print(bone_val)
        bone_mtrx.append(bone_val)
    
    parent_boneCount = bs.readUInt()
    bone_parent = []
    for x in range(boneCount):
        bone_parent.append(bs.readUByte())
    for x in range(len(bone_parent)):
        if bone_parent[x] == 0xFF:
            bone_parent[x] = -1
    bs.seek((4-parent_boneCount)%4, NOESEEK_REL)
    
    boneNameOffset = bs.readUInt()
    bs.seek(boneNameOffset*4, NOESEEK_REL) # skipped offsets to bone names, shouldn't be needed unless if u32 isn't going from great to less
    
    bone_names = []
    for x in range(boneCount):
        boneNameLength = bs.readUInt()
        boneName = noeAsciiFromBytes(bs.readBytes(boneNameLength))
        #print(boneName)
        bone_names.append(boneName)
        bs.seek(4-(boneNameLength%4), NOESEEK_REL)
    bone_names.reverse()
    
    bones = []
    for x in range(boneCount):
        bones.append(NoeBone(x, bone_names[x], bone_mtrx[x], None, bone_parent[x]))
    
    bs.seek(4, NOESEEK_REL)
    chunkOffset1 = bs.readUInt()
    #print(chunkOffset1)
    bs.seek(chunkOffset1+4, NOESEEK_REL)
    tell_MappingOffset = bs.tell()
    abs_MappingOffset = tell_MappingOffset + bs.readUInt()
    bs.seek(8, NOESEEK_REL)
    tell_ModelOffset = bs.tell()
    abs_ModelOffset = tell_ModelOffset + bs.readUInt()# - 4
    bs.seek(12, NOESEEK_REL)
    pos_count = bs.readUInt()
    print("Vertex Count: " + str(pos_count))
    
    bs.seek(abs_MappingOffset, NOESEEK_ABS)
    mapping_count = bs.readUInt()
    print("Mapping Count: " + str(mapping_count))
    mapping_data = []
    for x in range(mapping_count):
        mapping_data.append(bs.readUByte())
    #print(mapping_data)
    
    bs.seek(abs_ModelOffset, NOESEEK_ABS)
    material_count = bs.readUInt()
    print("Material Count: " + str(material_count))
    material_idx = []
    for x in range(material_count):
        material_idx.append(bs.readUInt())
        material_idx.append(bs.readUInt())
    #print(material_idx)
    idx_count = bs.readUInt()
    print("Face Count: " + str(int(idx_count/3)))
    
    if pos_count < 0x10000: idx_data = bs.readBytes(idx_count*2)
    else: idx_data = bs.readBytes(idx_count*4)
    bs.seek((4-bs.tell())%4, NOESEEK_REL)
    
    pos_allsize = bs.readUInt()
    print("Vertex Bytes Size: " + str(hex(pos_allsize)))
    pos_stride = int(pos_allsize/pos_count)
    print("Vertex Stride: " + str(pos_stride)) # posible vals: 56 (default) 60 (skip 4 bytes) 32 (remove uvs, tangs & unknown) 72 (skip 0x10 bytes) 76 (only used on japanese_phrases-thankyou)
    
    pos_data = bs.readBytes(pos_allsize)
    for x in range(material_count):
        rapi.rpgSetMaterial("mat"+str(x))
        rapi.rpgSetName("mesh"+str(x))
        if pos_stride == 56:
            rapi.rpgBindPositionBuffer(pos_data, noesis.RPGEODATA_FLOAT, pos_stride)
            rapi.rpgBindUV1BufferOfs(pos_data, noesis.RPGEODATA_FLOAT, pos_stride, 0xC)
            rapi.rpgBindNormalBufferOfs(pos_data, noesis.RPGEODATA_FLOAT, pos_stride, 0x14)
            rapi.rpgBindBoneIndexBufferOfs(pos_data, noesis.RPGEODATA_UBYTE, pos_stride, 0x30, 4)
            rapi.rpgBindBoneWeightBufferOfs(pos_data, noesis.RPGEODATA_UBYTE, pos_stride, 0x34, 4)
        elif pos_stride == 60:
            rapi.rpgBindPositionBuffer(pos_data, noesis.RPGEODATA_FLOAT, pos_stride)
            rapi.rpgBindUV1BufferOfs(pos_data, noesis.RPGEODATA_FLOAT, pos_stride, 0x10)
            rapi.rpgBindNormalBufferOfs(pos_data, noesis.RPGEODATA_FLOAT, pos_stride, 0x18)
            rapi.rpgBindBoneIndexBufferOfs(pos_data, noesis.RPGEODATA_UBYTE, pos_stride, 0x34, 4)
            rapi.rpgBindBoneWeightBufferOfs(pos_data, noesis.RPGEODATA_UBYTE, pos_stride, 0x38, 4)    
        elif pos_stride == 32:
            rapi.rpgBindPositionBuffer(pos_data, noesis.RPGEODATA_FLOAT, pos_stride)
            rapi.rpgBindNormalBufferOfs(pos_data, noesis.RPGEODATA_FLOAT, pos_stride, 0xC)
            rapi.rpgBindBoneIndexBufferOfs(pos_data, noesis.RPGEODATA_UBYTE, pos_stride, 0x18, 4)
            rapi.rpgBindBoneWeightBufferOfs(pos_data, noesis.RPGEODATA_UBYTE, pos_stride, 0x1C, 4)  
        elif pos_stride == 72:
            rapi.rpgBindPositionBuffer(pos_data, noesis.RPGEODATA_FLOAT, pos_stride)
            rapi.rpgBindUV1BufferOfs(pos_data, noesis.RPGEODATA_FLOAT, pos_stride, 0xC)
            rapi.rpgBindNormalBufferOfs(pos_data, noesis.RPGEODATA_FLOAT, pos_stride, 0x14)
            rapi.rpgBindBoneIndexBufferOfs(pos_data, noesis.RPGEODATA_UBYTE, pos_stride, 0x40, 4)
            rapi.rpgBindBoneWeightBufferOfs(pos_data, noesis.RPGEODATA_UBYTE, pos_stride, 0x44, 4)
        elif pos_stride == 76:
            rapi.rpgBindPositionBuffer(pos_data, noesis.RPGEODATA_FLOAT, pos_stride)
            rapi.rpgBindUV1BufferOfs(pos_data, noesis.RPGEODATA_FLOAT, pos_stride, 0x10)
            rapi.rpgBindNormalBufferOfs(pos_data, noesis.RPGEODATA_FLOAT, pos_stride, 0x18)
            rapi.rpgBindBoneIndexBufferOfs(pos_data, noesis.RPGEODATA_UBYTE, pos_stride, 0x44, 4)
            rapi.rpgBindBoneWeightBufferOfs(pos_data, noesis.RPGEODATA_UBYTE, pos_stride, 0x48, 4)
        else: return 0
        
        rapi.rpgSetBoneMap(mapping_data)
        if pos_count < 0x10000: rapi.rpgCommitTriangles(idx_data[material_idx[x*2]*2:material_idx[x*2+1]*2], noesis.RPGEODATA_USHORT, material_idx[x*2+1]-material_idx[x*2], noesis.RPGEO_TRIANGLE)
        else: rapi.rpgCommitTriangles(idx_data[material_idx[x*2]*4:material_idx[x*2+1]*4], noesis.RPGEODATA_UINT, material_idx[x*2+1]-material_idx[x*2], noesis.RPGEO_TRIANGLE)
        rapi.rpgClearBufferBinds()
    
    mdl = rapi.rpgConstructModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1