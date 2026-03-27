# Thumpies .bin (Model)
# Written by Somwonere
# you can notice some models have inverted culling, the models in-game doesn't use any culling at all
# acknowledgment: https://github.com/iestyn129/Thumpie2Obj/blob/master/thumpie2obj.py


from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Thumpies Binary Model", ".bin")
    noesis.setHandlerTypeCheck(handle, ThumpBINCheckType)
    noesis.setHandlerLoadModel(handle, ThumpBINLoadModel)

    #noesis.logPopup()
    #print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
    return 1

def ThumpBINCheckType(data):
    if len(data) < 8: return 0
    bs = NoeBitStream(data)
    if bs.readUInt() != 1: return 0
    if bs.readUInt() == 0: return 0
    return 1

def ThumpBINLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetPosScaleBias(NoeVec3((-1,1,1)),NoeVec3())
    
    bs.seek(0x4, NOESEEK_ABS)
    textureNameSize = bs.readUInt()
    print(textureNameSize)
    textureName = noeAsciiFromBytes(bs.readBytes(textureNameSize-1))
    bs.seek(4-((textureNameSize-1)%4), NOESEEK_REL)
    
    bs.seek(0x4, NOESEEK_REL)
    pos_count = bs.readUInt()
    print("Positions: " + str(pos_count))
    pos_data = bs.readBytes(pos_count*0x18)
    rapi.rpgBindPositionBuffer(pos_data, noesis.RPGEODATA_FLOAT, 0x18)
    rapi.rpgBindUV1BufferOfs(pos_data, noesis.RPGEODATA_FLOAT, 0x18, 0xC)
    
    idx_count = bs.readUInt()
    print("Indexes: " + str(idx_count))
    idx_data = bs.readBytes(idx_count*0xC)
    rapi.rpgCommitTriangles(idx_data, noesis.RPGEODATA_UINT, idx_count*3, noesis.RPGEO_TRIANGLE)
    
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    print("Texture Path: " + textureName)
    return 1
