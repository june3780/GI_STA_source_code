import json



def getMetalLayerID(fileAddress):
    file = open(fileAddress, 'r')
    layerID_list = list()
    for line in file.readlines():
        if line.startswith("LAYER metal"):
            layerID = line.replace("LAYER metal", "")
            layerID = layerID.replace("\n", "")
            layerID_list.append(layerID)
    file.close() 
    return layerID_list

def getMacroInfo(fileAddress):
    file = open(fileAddress, 'r')
    macroInfo = dict()
    macroID = None
    for idx, line in enumerate(file):
        line = line.strip()
        
        if line.startswith("MACRO"):
            macroID = line.replace("MACRO", "").replace("\n", "").strip()
            macroInfo[macroID] = dict()
            startIdx = idx
        if macroID != None:
            if line.startswith("END" +" " + macroID):
                endIdx = idx
                macroInfo[macroID]["idx_range"] = [startIdx, endIdx]
      
    for macroID in macroInfo.keys():
        startIdx, endIdx = macroInfo[macroID]["idx_range"][0], macroInfo[macroID]["idx_range"][1]
        file = open(fileAddress, 'r')
        for idx, line in enumerate(file):
            if idx > startIdx and idx < endIdx:
                line = line.strip()
                if line.startswith("CLASS"):
                    classMacro = line.replace("CLASS", "").replace("\n", "").replace(";","").strip()
                    macroInfo[macroID]["class"] = classMacro
                
                elif line.startswith("SIZE"):
                    size = line.replace("SIZE", "").replace("\n", "").replace(";","").strip()
                    width, height = float(size.split("BY")[0].strip()), float(size.split("BY")[1].strip())
                    macroInfo[macroID]["width"] = width
                    macroInfo[macroID]["height"] = height
                
                elif line.startswith("SYMMETRY"):
                    symmetry = line.replace("SYMMETRY", "").replace("\n", "").replace(";","").strip()
                    macroInfo[macroID]["symmetry"] = symmetry
                
                elif line.startswith("SITE"):
                    site = line.replace("SITE", "").replace("\n", "").replace(";","").strip()
                    macroInfo[macroID]["site"] = site
                
                elif line.startswith("PIN"):
                    pinID = line.replace("PIN", "").replace("\n", "").replace(";","").strip()
                    if "pin" not in macroInfo[macroID].keys():
                        macroInfo[macroID]["pin"] = dict()
                        macroInfo[macroID]["pin"][pinID] = dict()
                    else:
                        macroInfo[macroID]["pin"][pinID] = dict()
                
                elif line.startswith("DIRECTION"):
                    direction = line.replace("DIRECTION", "").replace("\n", "").replace(";","").strip()
                    macroInfo[macroID]["pin"][pinID]["direction"] = direction
                
                elif line.startswith("USE"):
                    use = line.replace("USE", "").replace("\n", "").replace(";","").strip()
                    macroInfo[macroID]["pin"][pinID]["use"] = use
                
                elif line.startswith("LAYER"):
                    metalLayer = line.replace("LAYER", "").replace("\n", "").replace(";","").strip()
                    macroInfo[macroID]["pin"][pinID]["LAYER"] = metalLayer
                
                elif line.startswith("RECT"):
                    rect = line.replace("RECT", "").replace("\n", "").replace(";","").strip().split(" ")
                    rect = [float(coord) for coord in rect]
                    if "RECT" not in macroInfo[macroID]["pin"][pinID].keys():
                        macroInfo[macroID]["pin"][pinID]["RECT"] = list()
                        macroInfo[macroID]["pin"][pinID]["RECT"].append(rect)
                    else:
                        macroInfo[macroID]["pin"][pinID]["RECT"].append(rect)
    return macroInfo
        
        
    

    



def getMetalLayerIndex(fileAddress):
    layer_list = getMetalLayerID(fileAddress)
    layerInfo = dict()
    for layerID in layer_list: 
        file = open(fileAddress, 'r')
        for idx, line in enumerate(file):
            if line == "LAYER metal" + layerID +'\n':
                layerInfo["LAYER metal" +layerID] = dict()
                layerInfo["LAYER metal" + layerID]['start_idx'] = idx+1
            if line == "END metal" +layerID + '\n':
                layerInfo["LAYER metal"+layerID]['end_idx'] = idx-1
        file.close()
    return layerInfo

def getDistanceUnit(fileAddress):
    file = open(fileAddress, 'r')
    for idx, line in enumerate(file):
        if line.startswith("UNITS"):
           start_idx = idx+1
           break
    file.close()
    file = open(fileAddress, 'r')
    data = list()
    for idx, line in enumerate(file):
        if idx == start_idx:
           line = line.replace("DATABASE","").replace("MICRONS","").replace(";","").strip()
           distance = int(line)
           return distance 
           break



def getMetalLayerInfo(fileAddress):
    layer_index_info = getMetalLayerIndex(fileAddress)
    layerID_list = getMetalLayerID(fileAddress)
    info_list = ["TYPE", "PITCH", "WIDTH", "OFFSET", 'RESISTANCE', 'HEIGHT', 'THICKNESS']
    for layerID in layerID_list:
        file = open(fileAddress, 'r')
        startIdx = layer_index_info["LAYER metal" + layerID]["start_idx"]
        endIdx = layer_index_info["LAYER metal" + layerID]["end_idx"]
        for idx, line in enumerate(file):
            if idx >= startIdx and idx <= endIdx:
                line = line.strip().replace("\n", "")
                if  line.startswith("TYPE"):
                    line = line.split("TYPE")
                    type = line[1].replace(";","").strip()
                    layer_index_info["LAYER metal" + layerID]["TYPE"] = type
                elif line.startswith("DIRECTION"):
                    direction = line.replace("DIRECTION", "").replace(";","").strip()
                    layer_index_info["LAYER metal" + layerID]["DIRECTION"] = direction
                elif line.startswith("PITCH"):
                    line = line.split("PITCH")
                    pitch = [float(value) for value in line[1].replace(";","").strip().split(" ")]
                    layer_index_info["LAYER metal" + layerID]["PITCH"] = pitch
                elif line.startswith("WIDTH"):
                    line = line.replace("WIDTH", "").replace(";","").strip() 
                    widthInfo = line.split(" ")
                    if len(widthInfo) == 1:
                        width = float(widthInfo[0])
                        layer_index_info["LAYER metal" + layerID]["WIDTH"] = width 
                elif line.startswith("OFFSET"):
                    line = line.split("OFFSET")
                    offset = [float(value) for value in line[1].strip().replace(";","").strip().split(" ")]
                    layer_index_info["LAYER metal" + layerID]["OFFSET"] = offset 
                elif line.startswith("RESISTANCE"):
                    line = line.split("RESISTANCE")
                    res = line[1].replace(";","").strip()
                    layer_index_info["LAYER metal" + layerID]["RESISTANCE"] = res

        file.close()
    return layer_index_info

if __name__ == "__main__":
    leflef="../data/deflef_to_graph_and_verilog/1. lefs/NangateOpenCellLibrary.mod.lef"
    macroInfo = getMacroInfo(leflef)
    with open("test_leffile_read.json", "w") as w: json.dump(macroInfo, w, indent=4)
    print(json.dumps(macroInfo, indent=4))
