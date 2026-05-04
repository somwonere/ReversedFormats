# Thumpies .bin (Model) Importer/Exporter Noesis plugin
# Written by Somwonere
# Acknowledgment by iestyn129: https://github.com/iestyn129/Thumpie2Obj/blob/master/thumpie2obj.py
# Before exporting a model, name your material like "game/data/images/textures/models/balls/noobie_bigger01" and make a .png texture in that directory so the game loads it correctly
# You can notice some models have inverted culling, the renderer from in-game doesn't use any culling at all

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Thumpies Binary Model", ".bin")
    noesis.setHandlerTypeCheck(handle, ThumpBINCheckType)
    noesis.setHandlerLoadModel(handle, ThumpBINLoadModel)
    noesis.setHandlerWriteModel(handle, ThumpBINWriteModel)

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
    rapi.rpgSetUVScaleBias(NoeVec3((1,-1,1)),NoeVec3((0,1,0)))
    
    bs.seek(0x4, NOESEEK_ABS)
    textureNameSize = bs.readUInt()
    print(textureNameSize)
    textureName = noeAsciiFromBytes(bs.readBytes(textureNameSize-1))
    bs.seek(4-((textureNameSize-1)%4), NOESEEK_REL)
    rapi.rpgSetMaterial(textureName)
    
    bs.seek(0x4, NOESEEK_REL)
    pos_count = bs.readUInt()
    if pos_count == 0: return 0
    print("Positions: " + str(pos_count))
    pos_data = bs.readBytes(pos_count*0x18)
    rapi.rpgBindPositionBuffer(pos_data, noesis.RPGEODATA_FLOAT, 0x18)
    rapi.rpgBindUV1BufferOfs(pos_data, noesis.RPGEODATA_FLOAT, 0x18, 0xC)
    
    idx_count = bs.readUInt()
    if idx_count == 0: return 0
    print("Indexes: " + str(idx_count))
    idx_data = bs.readBytes(idx_count*0xC)
    rapi.rpgCommitTriangles(idx_data, noesis.RPGEODATA_UINT, idx_count*3, noesis.RPGEO_TRIANGLE)
    
    mdl = rapi.rpgConstructModel()
    mdlList.append(mdl)
    print("Texture Path: " + textureName)
    return 1

def ThumpBINWriteModel(mdl, bs):
    #Model Checkers
    ModelError = 0
    if len(mdl.meshes) == 0:
        print("THUMPIES MODEL ERROR: Model has no Meshes")
        ModelError = 1
    if len(mdl.meshes) > 1:
        print("THUMPIES MODEL ERROR: Model has more than one Mesh")
        ModelError = 1
    if ModelError == 1:
        return 0
    #When there is only one mesh
    if len(mdl.meshes[0].positions) == 0:
        print("THUMPIES MODEL ERROR: Mesh doesn't have Vertexes/Positions")
        ModelError = 1
    if len(mdl.meshes[0].uvs) == 0: #Noesis doesn't seem to detect this and puts them in a corner
        print("THUMPIES MODEL ERROR: Mesh doesn't have UVs")
        ModelError = 1
    if len(mdl.meshes[0].indices) == 0:
        print("THUMPIES MODEL ERROR: Mesh doesn't have Faces/Indexes")
        ModelError = 1
    if mdl.modelMats == None:
        print("THUMPIES MODEL ERROR: Mesh doesn't have a Material/Texture Path")
        ModelError = 1
    if ModelError == 1:
        return 0
    
    bs.writeUInt(1)
    #Material/Texture Path
    textureName = mdl.meshes[0].matName
    textureNameSize = len(textureName)
    print("Material Name as Texture Path: " + textureName)
    bs.writeUInt(textureNameSize+1)
    bs.writeBytes(textureName.encode(encoding="ascii"))
    for x in range(4-((textureNameSize)%4)): bs.writeByte(0)
    bs.writeUInt(1) #Unknown
    
    #Positions
    positionsCount = len(mdl.meshes[0].positions)
    print("Positions: " + str(positionsCount))
    bs.writeUInt(positionsCount)
    for x in range(positionsCount):
        bs.writeFloat(mdl.meshes[0].positions[x][0]*-1)
        bs.writeFloat(mdl.meshes[0].positions[x][1])
        bs.writeFloat(mdl.meshes[0].positions[x][2])
        bs.writeFloat(mdl.meshes[0].uvs[x][0])
        bs.writeFloat(mdl.meshes[0].uvs[x][1]*-1+1)
        bs.writeUInt(0x00FFFFFF)
    
    #Indexes
    indexesCount = int(len(mdl.meshes[0].indices)/3)
    print("Indexes: " + str(indexesCount))
    bs.writeUInt(indexesCount)
    for x in range(indexesCount*3):
        bs.writeUInt(mdl.meshes[0].indices[x])
    
    bs.writeUInt(0)
    return 1
