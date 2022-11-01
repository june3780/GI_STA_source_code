import sys


cellList = dict()
cellData = dict()
lineData = list()
orientType = ['N', 'S', 'E', 'W', 'FN', 'FS', 'FE', 'FW']

def LoadPlaceData(fileName):
    global cellData
    with open(fileName, 'r') as f:
        rdr = f.readlines()
        for line in rdr:
            data = line.split()
            try:
                cellData[int(data[0])] = {'xpos': float(data[1]), 'ypos': float(data[2]), 'radius': float(data[3]), 'width': float(data[4]), 'height': float(data[5]), 'orient': orientType[int(data[6])]}
            except:
                return

def LoadCellID(fileName):
    global cellList
    with open(fileName, 'r') as f:
        rdr = f.readlines()
        for line in rdr:
            data = line.split()
            cellList[data[1]] = cellData[int(data[0])]

def LoadDef(defPath):
    global lineData
    inComp = False
    with open(defPath, 'r') as f:
        rdr = f.readlines()
        for line in rdr:
            data = line.split()
            if len(data) == 0:
                pass
            elif data[0] == 'COMPONENTS':
                inComp = True
            elif inComp and data[0] == 'END':
                inComp = False
            elif inComp and data[0] != ';':
                cellName = data[1]
                cellList[cellName]['xpos'] = str(float(data[6]) + cellList[cellName]['width']/2)
                cellList[cellName]['ypos'] = str(float(data[7]) + cellList[cellName]['height']/2)
                cellList[cellName]['orient'] = orientType.index(data[9])

def WriteTxt(newTxtPath):
    with open(newTxtPath, 'w') as f:
        for cellID in range(1, len(cellData)+1):
            data = cellData[int(cellID)]
            line = str(cellID) + ' ' + str(data['xpos']) + ' ' + str(data['ypos']) + ' ' + str(data['radius']) + ' ' + str(data['width']) + ' ' + str(data['height']) + ' ' + str(data['orient']) + '\n' 
            f.write(line)

if __name__ == "__main__":
    LoadPlaceData("/home/june/Documents/PNR/timing/source/7809_place.txt")
    LoadCellID("/home/june/Documents/PNR/timing/source/cell_7809_macro_index.txt")
    LoadDef(sys.argv[1])  # change file name
    WriteTxt(sys.argv[2])                          # change file name
