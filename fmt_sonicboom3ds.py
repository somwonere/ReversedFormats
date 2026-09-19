# Sonic Boom: Shattered Crystal / Fire & Ice "MESH" & "GEOB"
# Written by Somwonere
# Special thanks to killercracker / SleepyZay on the old VG Resource fourms for some documentation.

from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Sonic Boom 3DS \"MESH\"", ".mesh")
    noesis.setHandlerTypeCheck(handle, BoomMESHCheckType)
    noesis.setHandlerLoadModel(handle, BoomMESHLoadModel)
    handle = noesis.register("Sonic Boom 3DS \"GEOB\" (Skeleton)", ".geob")
    noesis.setHandlerTypeCheck(handle, BoomGEOBCheckType)
    noesis.setHandlerLoadModel(handle, BoomGEOBLoadModel)
    
    #noesis.logPopup()
    #print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
    return 1

def readSMSH(bs, chunkNum, nextChunk): #"SubMeSH"
    smshSkinning = False
    while bs.tell() < nextChunk:
        subchunkName = noeAsciiFromBytes(bs.readBytes(4))
        subchunkSize = bs.readUInt()
        #print("Subchunk", subchunkName, bs.tell())
        
        if subchunkName == "MHDR": #Mesh HeaDeR
            smshUnk1 = bs.readUByte() 
            smshVTXCount = bs.readUShort()
            smshIDXCount = bs.readUShort()
            bs.seek(1, NOESEEK_REL) #null?
            smshMatId = bs.readUInt()
            bs.seek(4, NOESEEK_REL)
            smshScale = bs.readFloat()
            rapi.rpgSetPosScaleBias(NoeVec3((smshScale,smshScale,smshScale)), None) #Toys fix
            bs.seek(subchunkSize - 22, NOESEEK_REL)
        elif subchunkName == "MVTX": #Mesh VerTeX
            vtxBuffer = bs.readBytes(subchunkSize - 4)
        elif subchunkName == "MIDX": #Mesh InDeX
            idxBuffer = bs.readBytes(subchunkSize - 4)
        elif subchunkName == "MPAL": #Mesh ??? (bone mapping)
            palList = []
            for i in range((subchunkSize - 4) // 2): palList.append(bs.readUShort())
            smshSkinning = True
        else:
            print("Unknown subchunk:", subchunkName)
            bs.seek(subchunkSize - 4, NOESEEK_REL)
    
    rapi.rpgSetName("SMSH_" + str(chunkNum))
    rapi.rpgSetMaterial("mat_" + str(smshMatId))
    vtxStride = 36
    if smshSkinning:
        rapi.rpgSetBoneMap(palList)
        vtxStride = 44
        rapi.rpgBindBoneIndexBufferOfs(vtxBuffer, noesis.RPGEODATA_UBYTE, vtxStride, 36, 4)
        rapi.rpgBindBoneWeightBufferOfs(vtxBuffer, noesis.RPGEODATA_UBYTE, vtxStride, 40, 4)
    rapi.rpgBindPositionBuffer(vtxBuffer, noesis.RPGEODATA_FLOAT, vtxStride)
    rapi.rpgBindUV1BufferOfs(vtxBuffer, noesis.RPGEODATA_FLOAT, vtxStride, 16)
    rapi.rpgBindNormalBufferOfs(vtxBuffer, noesis.RPGEODATA_FLOAT, vtxStride, 24)
    
    rapi.rpgCommitTriangles(idxBuffer, noesis.RPGEODATA_USHORT, smshIDXCount, noesis.RPGEO_TRIANGLE, 1)
    rapi.rpgClearBufferBinds()
    return smshSkinning

def geobBonsCheck(bs): #Checking if it has bones
    bonesCheck = False
    chunkName = ""
    while not bs.checkEOF():
        chunkName = noeAsciiFromBytes(bs.readBytes(4))
        chunkSize = bs.readUInt()
        nextChunk = bs.tell() + chunkSize - 4
        if chunkName == "SKEL": break
        bs.seek(nextChunk)
    while not bs.checkEOF():
        chunkName = noeAsciiFromBytes(bs.readBytes(4))
        chunkSize = bs.readUInt()
        nextChunk = bs.tell() + chunkSize - 4
        if chunkName == "BONS":
            bonesCheck = True
            break
        bs.seek(nextChunk)
    if not bonesCheck:
        return 0
    return 1

def readBONS(bs, chunkSize):
    bones = []
    boneCount = (chunkSize - 4) // 76
    #print("Bone Count:", boneCount)
    boneIds = []
    boneParentIds = []
    bonePositions = []
    boneNames = []
    for i in range(boneCount):
        boneIds.append(bs.readUInt())
        boneParentIds.append(bs.readUInt())
        bs.seek(24, NOESEEK_REL) #I don't get how those bytes work, possibly rotations?
        bonePositions.append(NoeVec3.fromBytes(bs.readBytes(12)))
        boneNames.append(noeAsciiFromBytes(bs.readBytes(32)))
    boneParentsNew = [-1] * boneCount
    for i in range(boneCount):
        for j in range(boneCount):
            if boneIds[j] == boneParentIds[i]:
                boneParentsNew[i] = j
    for i in range(boneCount):
        boneMatrix = NoeMat43()
        boneMatrix[3] = bonePositions[i]
        bones.append(NoeBone(i, boneNames[i], boneMatrix, parentIndex = boneParentsNew[i]))
    return bones

def BoomMESHCheckType(data):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(4)) != "MESH": return 0
    fileSize = bs.readUInt()
    bs.seek(fileSize + 4)
    if not bs.checkEOF(): return 0
    return 1

def BoomMESHLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()
    bs.seek(8)
    
    meshSkinned = False
    chunkNum = 0
    while not bs.checkEOF():
        chunkName = noeAsciiFromBytes(bs.readBytes(4))
        chunkSize = bs.readUInt()
        #print(chunkName, chunkSize, chunkNum)
        nextChunk = bs.tell() + chunkSize - 4
        if chunkName == "SMSH":
            meshSkinned = readSMSH(bs, chunkNum, nextChunk)
        bs.seek(nextChunk)
        chunkNum += 1
    mdl = rapi.rpgConstructModel()
    
    if meshSkinned:
        geobDir = rapi.getDirForFilePath(rapi.getInputName())
        geobList = []
        for f in os.listdir(geobDir):
            if f.endswith(".GEOB"): geobList.append(f)
        if len(geobList) == 1:
            geobPath = os.path.join(geobDir, geobList[0])
            geobBS = NoeBitStream(rapi.loadIntoByteArray(geobPath))
            geobBS.seek(8)
            if geobBonsCheck(geobBS):
                geobBS.seek(-4, NOESEEK_REL)
                chunkSize = geobBS.readUInt()
                mdl.setBones(readBONS(geobBS, chunkSize))
            else:
               noesis.messagePrompt("GEOB doesn't have bones, find the correct file if you can.")
        elif len(geobList) > 1: noesis.messagePrompt("MESH is skinned, but is more than one GEOB file.\nMove the MESH and the correct GEOB to one folder.\nBut anyway here's the unrigged model.")
        else: noesis.messagePrompt("MESH is skinned, but there isn't a GEOB file.")
    mdlList.append(mdl)
    return 1

def BoomGEOBCheckType(data):
    bs = NoeBitStream(data)
    if noeAsciiFromBytes(bs.readBytes(4)) != "GEOB": return 0
    fileSize = bs.readUInt()
    bs.seek(8)
    
    if not geobBonsCheck(bs):
        print("GEOB doesn't have bones.")
        return 0
    bs.seek(fileSize + 4)
    if not bs.checkEOF(): return 0
    return 1

def BoomGEOBLoadModel(data, mdlList):
    bs = NoeBitStream(data)
    bs.seek(8)
    bones = []
    if not geobBonsCheck(bs):
        print("GEOB doesn't have bones.")
        return 0
    bs.seek(-4, NOESEEK_REL)
    chunkSize = bs.readUInt()
    mdl = NoeModel()
    mdl.setBones(readBONS(bs, chunkSize))
    mdlList.append(mdl)
    return 1