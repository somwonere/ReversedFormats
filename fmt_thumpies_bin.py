# Thumpies .bin (Model)
# This is my first noesis plugin, i don't know how to use stuff like "rpgBind..."
# you can notice some models have weird culling, the models in-game doesn't use any culling at all
# acknowledgment: https://github.com/iestyn129/Thumpie2Obj/blob/master/thumpie2obj.py


from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Thumpies Binary Model", ".bin")
    noesis.setHandlerTypeCheck(handle, ThumpBINCheckType)
    noesis.setHandlerLoadModel(handle, ThumpBINLoadModel)

    #noesis.logPopup()
    print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
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
    
    VCount=0
    FCount=0
    
    bs.seek(0x4, NOESEEK_ABS)
    textureNameSize = bs.readUInt()
    print(textureNameSize)
    bs.seek(textureNameSize-1, NOESEEK_REL)
    bs.seek(4-((textureNameSize-1)%4), NOESEEK_REL)
    
    bs.seek(0x4, NOESEEK_REL)
    VCount=bs.readUInt()
    VertArray=[NoeVec3()]*VCount
    UVArray=[NoeVec3()]*VCount
    print(VCount)
    for i in range(0, VCount):
        VertArray[i] = NoeVec3((bs.readFloat()*-1,bs.readFloat(),bs.readFloat()))
        UVArray[i] = NoeVec3((bs.readFloat(),bs.readFloat(),0))
        bs.seek(4, NOESEEK_REL)
    
    FCount = bs.readUInt()
    print(FCount)
    FaceArray = [0] * (FCount * 3)
    for i in range(0, FCount * 3):
        FaceArray[i] = bs.readUInt()

    mesh=NoeMesh([], [])
    mesh.setIndices(FaceArray)
    mesh.setPositions(VertArray)
    mesh.setUVs(UVArray)
    
    mdlList.append(NoeModel([mesh], [], []))
    
    return 1
