# Cellfish's .model (Header: BMDL)
# Note: If there is no bones, then that means there's animation data in the model
# Written by Somwonere
# Recommended to export as .dae/.smd, Blender screws up importing .fbx because the rigging data has no parenting. (decompiled the apk, it reads floats in that section)

from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Cellfish Binary MoDeL", ".model")
	noesis.setHandlerTypeCheck(handle, bmdlCheckType)
	noesis.setHandlerLoadModel(handle, bmdlLoadModel)
	noesis.logPopup()
	print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
	return 1

def bmdlCheckType(data):
    bs = NoeBitStream(data)
    
    header = bs.readBytes(4)
    print(header)
    
    if header == b'BMDL': return 1
    return 0

def bmdlLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    bs.setEndian(NOE_BIGENDIAN)
    rapi.rpgSetEndian(1)
    
    bs.seek(0x8, NOESEEK_ABS)
    header_vert_count = bs.readUInt()
    print(header_vert_count)
    
    bs.seek(0x20, NOESEEK_ABS)
    wind_header = bs.readBytes(4) # Indices
    print(wind_header)
    wind_count = bs.readUInt()
    if wind_count == 0: return 0
    print(wind_count)
    bs.seek(0x8, NOESEEK_REL)
    wind_data = bs.readBytes(wind_count*6)
    
    bs.seek(0x4, NOESEEK_REL)
    text_header = bs.readBytes(4) # UVs
    print(text_header)
    text_count = bs.readUInt()
    print(text_count)
    bs.seek(0x8, NOESEEK_REL)
    text_data = bs.readBytes(text_count*8)
    bs.seek(0x4, NOESEEK_REL)
    rapi.rpgBindUV1Buffer(text_data, noesis.RPGEODATA_FLOAT, 8)
    
    skin_vert_header = bs.readBytes(4)
    print(skin_vert_header)
    if skin_vert_header == b'SKIN': # Weights or Positions check
        skin_count = bs.readUInt() # Weights
        bs.seek(0x8, NOESEEK_REL)
        #bs.seek(0x8*skin_count, NOESEEK_REL) # skipping skin, do later
        skin_data = bs.readBytes(skin_count*8)
        
        bs.seek(0x4, NOESEEK_REL)
        rapi.rpgBindBoneIndexBuffer(skin_data, noesis.RPGEODATA_UBYTE, 8, 4)
        rapi.rpgBindBoneWeightBufferOfs(skin_data, noesis.RPGEODATA_UBYTE, 8, 4, 4)
        vert_header = bs.readBytes(4)
        print(vert_header)
    
    vert_count = bs.readUInt() # Positions
    print(vert_count)
    vert_scale = bs.readFloat()
    vert_data = bs.readBytes(vert_count*6)
    rapi.rpgBindPositionBuffer(vert_data, noesis.RPGEODATA_SHORT, 6)
    rapi.rpgSetPosScaleBias(NoeVec3((32768/vert_scale,32768/vert_scale,32768/vert_scale)),NoeVec3((0,0,0)))
    
    bs.seek(0x4, NOESEEK_REL)
    norm_header = bs.readBytes(4) # Normals
    if norm_header == b'NORM':
        print(norm_header)
        norm_count = bs.readUInt()
        print(norm_count)
        bs.seek(0x8, NOESEEK_REL)
        norm_data = bs.readBytes(norm_count*3)
        rapi.rpgBindNormalBuffer(norm_data, noesis.RPGEODATA_BYTE, 3)
        
        bs.seek(0x4, NOESEEK_REL)
        tags_header = bs.readBytes(4) # Bones (Absolutely no parenting)
        print(tags_header)
        tags_count = bs.readUInt()
        print(tags_count)
        bs.seek(0x8, NOESEEK_REL)
        tags_data = []
        for i in range(0, tags_count):
            tags_name_bytes = noeAsciiFromBytes(bs.readBytes(0x10))
            tags_name = tags_name_bytes.replace(" ", "")
            pos = NoeVec3((bs.readFloat(),bs.readFloat(),bs.readFloat()))#.toMat43()
            mtrx = NoeMat43()
            mtrx[3] = pos
            #print(mtrx)
            bs.seek(0x18, NOESEEK_REL)
            tags_data.append(NoeBone(i,tags_name,mtrx))
        
    rapi.rpgCommitTriangles(wind_data, noesis.RPGEODATA_USHORT, wind_count*3, noesis.RPGEO_TRIANGLE)
    mdl = rapi.rpgConstructModel()
    if norm_header == b'NORM': mdl.setBones(tags_data)
    mdlList.append(mdl)
    return 1