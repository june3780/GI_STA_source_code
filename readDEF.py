import json
import pandas as pd


def getDieArea(fileAddress):
    file = open(fileAddress)
    data = list()
    for idx, line in enumerate(file):
        if line.startswith("DIEAREA"):
           line = line.replace("DIEAREA","").strip().split(") (")
           leftDownCornerPos = [int(value) for value in line[0].replace("(", "").strip().split(" ")]
           rightUpCornerPos = [int(value) for value in line[1].replace(")", "").replace(";","").strip().split(" ")]
           width = rightUpCornerPos[0] - leftDownCornerPos[0]
           height = rightUpCornerPos[1] - leftDownCornerPos[1]
           return width, height 
           break

def getDistanceUnit(fileAddress):
    file = open(fileAddress)
    data = list()
    for idx, line in enumerate(file):
        if line.startswith("UNITS"):
           line = line.replace("UNITS","").replace("DISTANCE","").replace("MICRONS","").replace(";","").strip()
           distance = int(line)
           return distance 
           break


def getCellInfo(fileAddress):
    file = open(fileAddress)
    cellInfo = dict()
    for idx, line in enumerate(file):
        if line.startswith("COMPONENTS"):
            start_idx = idx+1
        elif line.startswith("END COMPONENTS"):
            end_idx = idx-1
            break
    file.close()
    file = open(fileAddress)
    data = list()
    for idx, line in enumerate(file):
        if idx >= start_idx and idx <= end_idx:
           if line.startswith("-"):
              line = line.replace("- ","").replace("\n","")
              cellID = line.split(" + ")[0].split(" ")[0]
              cellInfo[cellID] = dict()
              macroID = line.split(" + ")[0].split(" ")[1]
              pos = [float(value) for value in line.split(" + ")[1].split("PLACED")[1].strip().split('(')[1].split(')')[0].strip().split(" ")]
              orientation =  line.split(" + ")[1].split("PLACED")[1].strip().split('(')[1].split(')')[1].strip()
              cellInfo[cellID] = {"macro_id": macroID, "position": pos, "orientation": orientation}
    return cellInfo


def getExtPinInfo(fileAddress):
    extPinInfo = dict()
    file = open(fileAddress)
    for idx, line in enumerate(file):
        line = line.strip()
        if line.startswith("PINS"):
            pinNumb = line.split("PINS")[1].replace("\n", "").strip()
            startIdx = idx
        elif line.startswith("END PINS"):
            endIdx = idx
    file = open(fileAddress)
    for idx, line in enumerate(file):
        if idx > startIdx and idx < endIdx:
            line = line.strip()
            if line.startswith("-"):
                pinName = line.split("-")[1].split("+")[0].strip()
                netName = line.split("NET")[1].split("+")[0].strip()
                direction = line.split("DIRECTION")[1].split("+")[0].strip()
                use = line.split("USE")[1].replace("\n", "").strip()
                
            elif line.startswith("+ LAYER"):
                metalLayer = line.split("+ LAYER")[1].split("(")[0].strip()
                pinLeftCorner = line.split("+ LAYER")[1].split("(")[1].split(")")[0].strip().split(" ")
                pinRightCorner = line.split("+ LAYER")[1].split(")")[1].split("(")[1].replace(")", "").replace("\n", "").strip().split(" ")
                pinWidth, pinHeight = (float(pinRightCorner[0]) - float(pinLeftCorner[0])), (float(pinRightCorner[1])-float(pinLeftCorner[1]))
            
            elif line.startswith("+ PLACED"):
                pinPosLine = line.split("PLACED")[1].split("(")[1].split(")")[0].strip().split(" ")
                pinPos = list()
                #x, y 성분 
                for coord in pinPosLine:
                    pinPos.append(float(coord))
                #z 성분 (layer number)
                pinPos.append(int(metalLayer.replace("metal", "")))
                pinOrient = line.split(")")[1].replace("\n","").replace(";", "")
                extPinInfo[pinName] = {"net_name": netName, "direction": direction, "use": use, "metal_layer": metalLayer, "width": pinWidth, "height": pinHeight, "position": pinPos, "orientation": pinOrient}
    return extPinInfo
            

def getNetListInfo(fileAddress):
    file = open(fileAddress)
    netIdxRange = dict()
    for idx, line in enumerate(file):
        if line.startswith("NETS"):
            start_idx = idx+1
        elif line.startswith("END NETS"):
            end_idx = idx
            break
    file.close() 
    file = open(fileAddress)
    for idx, line in enumerate(file):
        line = line.replace("\n", "").strip()
        if idx >= start_idx and idx <= end_idx:
            if line.startswith("-"):
                netName = line.split(" ")[1]
                netIdxRange[netName] = dict()
                netIdxRange[netName]["start_idx"] = idx+1
            elif line.startswith(";"):
                netIdxRange[netName]["end_idx"] = idx-1
    file.close()
    file = open(fileAddress)
    for net in netIdxRange.keys():
        start_idx, end_idx = netIdxRange[net]['start_idx'], netIdxRange[net]['end_idx']
        netIdxRange[net]['data'] = list()
        netIdxRange[net]["cell_list"] = list()
        file = open(fileAddress)
        for idx, line in enumerate(file):
            if idx >= start_idx and idx <= end_idx:
                line = line.replace("\n", "").strip()
                if ( "ROUTED" in line ) or (  "NEW metal" in line ):
                    netIdxRange[net]['data'].append(line)
                else:
                    macro_list = [macro.replace("(","").replace(")","").replace("\\\\", "\\").strip() for macro in line.split(" ) (")]
                    netIdxRange[net]["cell_list"] = netIdxRange[net]["cell_list"] + macro_list
        file.close()
    return netIdxRange


    

if __name__ == "__main__":
    defdef="../data/deflef_to_graph_and_verilog/0. defs/gcd.def"

    netListInfo = getNetListInfo(defdef)
    width, height = getDieArea(defdef)
    extPinInfo = getExtPinInfo(defdef)
    print(json.dumps(netListInfo["req_msg[1]"], indent=4))

    
