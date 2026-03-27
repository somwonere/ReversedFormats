# Effekseer .efkmodel (also used in My Singing Monsters)
# Written by Somwonere
# If a model is not working, post an issue and send a sample.

from inc_noesis import *

def registerNoesisTypes():
	handle = noesis.register("Effekseer Model", ".efkmodel")
	noesis.setHandlerTypeCheck(handle, efkCheckType)
	noesis.setHandlerLoadModel(handle, efkLoadModel)

	noesis.logPopup()
	print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
	return 1

def efkCheckType(data):
    bs = NoeBitStream(data)
    if bs.readUInt() <= 6: return 1
    return 0

def efkLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    rapi.rpgSetPosScaleBias(NoeVec3((-1,1,1)),NoeVec3((0,0,0)))
    
    version = bs.readUInt()
    print(version)
    if version == 0:
        bs.seek(0x8, NOESEEK_ABS)
        stride = 56
    else:
        bs.seek(0x10, NOESEEK_ABS)
        stride = 60
    
    pos_count = bs.readUInt()
    print(pos_count)
    pos_data = bs.readBytes(pos_count*stride)
    rapi.rpgBindPositionBuffer(pos_data, noesis.RPGEODATA_FLOAT, stride)
    rapi.rpgBindNormalBufferOfs(pos_data, noesis.RPGEODATA_FLOAT, stride, 0xC)
    rapi.rpgBindUV1BufferOfs(pos_data, noesis.RPGEODATA_FLOAT, stride, 0x30)
    
    idx_count = bs.readUInt()
    print(idx_count)
    idx_data = bs.readBytes(idx_count*12)
    rapi.rpgCommitTriangles(idx_data, noesis.RPGEODATA_UINT, idx_count*3, noesis.RPGEO_TRIANGLE)
    
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    
    return 1