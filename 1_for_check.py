
import json
import copy
import os
import numpy as np
import sys
import shutil





### NangateOpenCellLibrary.mod.lef파일에서 macro_id 읽기
def getMacroInfo(fileAddress):                              
    file = open(fileAddress, 'r')
    macroInfo = dict()
    macroID = None
    range_macro=list()
    for idx, line in enumerate(file):
        line = line.strip()

### 각 MACRO의 정보에 대한 index 범위 지정 {'idx_range':각MACRO의 정보의 범위}
        if line.startswith("MACRO"):                                   
            macroID = line.replace("MACRO", "").replace("\n", "").strip()
            macroInfo[macroID] = dict()
            startIdx = idx
        if macroID != None:
            if line.startswith("END" +" " + macroID):
                endIdx = idx
                macroInfo[macroID]["idx_range"] = [startIdx, endIdx]

### 각 MACRO가 사용하는 소자의 PIN의 PORT_name과 DIRECTION 전처리
    for macroID in macroInfo.keys():
        startIdx, endIdx = macroInfo[macroID]["idx_range"][0], macroInfo[macroID]["idx_range"][1]
        file = open(fileAddress, 'r')
        for idx, line in enumerate(file):
            if idx > startIdx and idx < endIdx:
                line = line.strip()

### 각 MACRO가 사용하는 소자의 PIN의 PORT_name 전처리
                if line.startswith("PIN"):
                    pinID = line.replace("PIN", "").replace("\n", "").replace(";","").strip()
    ###PIN의 PORT_name이 VDD 혹은 VSS 인 경우 처리하지 않는다.
                    if pinID == "VDD" or pinID == "VSS":
                        break

                    else:    
                        macroInfo[macroID][pinID] = list()
                        
### 각 MACRO가 사용하는 소자의 PIN의 DIRECTION 전처리
                elif line.startswith("DIRECTION"):
                        direction = line.replace("DIRECTION", "").replace("\n", "").replace(";","").strip()
                        macroInfo[macroID][pinID] = direction

### MACRO정보의 index범위는 필요없는 데이터이므로 지워준다
        del macroInfo[macroID]["idx_range"]
### 각 MACRO의 정보{'MACRO_ID':{'PIN1':'PIN1의 direction', 'PIN2':'PIN2의 direction',...},'MACRO_ID2':{'PIN1':'PIN1의 direction',...},...}
    return macroInfo






def getAreaInfo(fileAddress):                              
    file = open(fileAddress, 'r')
    macroInfo = dict()
    macroID = None
    range_macro=list()
    area_line=str()
    for idx, line in enumerate(file):
        line = line.strip()

        if line.startswith("DIEAREA"):                                   
            area_line=line
    file.close()

    range_macro.append(area_line.split(") (")[0].split('( ')[1].strip().split(' '))
    range_macro.append(area_line.split(") (")[1].split(' )')[0].strip().split(' '))

    for idx in range(len(range_macro)):
        for kdx in range(len(range_macro[idx])):
            range_macro[idx][kdx]=float(range_macro[idx][kdx])

    return range_macro






def Getportpos(fileAddress):
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
                if line.startswith("PIN"):
                    pinID = line.replace("PIN", "").replace("\n", "").replace(";","").strip()
                    if "pin" not in macroInfo[macroID].keys():
                        macroInfo[macroID]["pin"] = dict()
                        macroInfo[macroID]["pin"][pinID] = dict()
                    else:
                        macroInfo[macroID]["pin"][pinID] = dict()
                
                elif line.startswith("RECT"):
                    rect = line.replace("RECT", "").replace("\n", "").replace(";","").strip().split(" ")
                    rect = [float(coord) for coord in rect]
                    if "RECT" not in macroInfo[macroID]["pin"][pinID].keys():
                        macroInfo[macroID]["pin"][pinID]["RECT"] = list()
                        macroInfo[macroID]["pin"][pinID]["RECT"].append(rect)
                    else:
                        macroInfo[macroID]["pin"][pinID]["RECT"].append(rect)

        if "VSS" in macroInfo[macroID]["pin"]:
            del macroInfo[macroID]["pin"]["VSS"]
        if "VDD" in macroInfo[macroID]["pin"]:
            del macroInfo[macroID]["pin"]["VDD"]
        if "idx_range" in macroInfo[macroID]:
            del macroInfo[macroID]['idx_range']
        
        if "pin" in macroInfo[macroID]:
            aaa=macroInfo[macroID]["pin"]
            macroInfo[macroID]=aaa
    return macroInfo







def Get_RECT_macro(dict1):
    RECT_macro=copy.deepcopy(dict1)

    for macroid in RECT_macro:
        for port in RECT_macro[macroid]:
                
                aaa=RECT_macro[macroid][port]['RECT']
                (RECT_macro[macroid][port])=aaa
    return RECT_macro







def Get_firstRECT_macro(leflef):
    port = Getportpos(leflef)########################@@@@@
    port_RECT = Get_RECT_macro(port)

    firstRECT_macro=copy.deepcopy(port_RECT)

    for macroid in firstRECT_macro:
        for port in firstRECT_macro[macroid]:
                aaa=firstRECT_macro[macroid][port][0]
                firstRECT_macro[macroid][port]=aaa
    return firstRECT_macro



def get_lef_data_unit(leflef):
    data_unit=None
    file = open(leflef, 'r')

    for idx, line in enumerate(file):
        line = line.strip()
        if line.startswith("DATABASE MICRONS"):
            data_unit=float(line.split(' ')[2])
            break

    if data_unit==None:
        print('Error : lef_data_unit doesn\'t exist')
        return 'Error : lef_data_unit doesn\'t exist : '+str(data_unit)

    return data_unit




### gcd.def파일에서 각 NET의 cell들과 cell에서 사용하는 PIN 읽기
def getNetListInfo(fileAddress):
    file = open(fileAddress)
    netIdxRange = dict()

### NETS 목록의 index 범위 지정
    for idx, line in enumerate(file):
        if line.startswith("NETS"):
            start_idx = idx+1
        elif line.startswith("END NETS"):
            end_idx = idx
            break
    file.close() 

### 하나의 NET의 index 범위 지정 
    file = open(fileAddress)
    for idx, line in enumerate(file):
        line = line.replace("\n", "").strip()
        if idx >= start_idx and idx <= end_idx:
            if line.startswith("-"):
                netName = line.split(" ")[1]
                netIdxRange[netName] = dict()
                netIdxRange[netName]["start_idx"] = idx+1
            elif line.endswith(";"):
                netIdxRange[netName]["end_idx"] = idx
    file.close()

### 하나의 NET을 구성하는 cell name과 연결된 PIN의 port name읽기
    file = open(fileAddress)
    for netName in netIdxRange.keys():

        start_idx = netIdxRange[netName]['start_idx']
        end_idx =netIdxRange[netName]['end_idx']
        netIdxRange[netName]["cell_list"] = list()
        file = open(fileAddress)
        for idx, line in enumerate(file):

            ### NET의 내용 중, ROUTED와 NEW matal을 제거
            if idx >= start_idx and idx <= end_idx:
                line = line.replace("\n", "").strip()
                if ( "ROUTED" in line ) or (  "NEW metal" in line ):
                    break
                else:
                    macro_list = [macro.replace("(","").replace(")","").replace("\\\\", "\\").strip() for macro in line.split(" ) (")]
                    netIdxRange[netName]["cell_list"] = netIdxRange[netName]["cell_list"] + macro_list

        ### 하나의 NET의 index 범위와 전체 NETS의 index 범위에 대한 데이터 삭제
        del netIdxRange[netName]['start_idx'], netIdxRange[netName]['end_idx']
        netIdxRange[netName] = netIdxRange[netName]["cell_list"]
        
        file.close()
    for idx,ivalue in enumerate(netIdxRange):
        while ';' in netIdxRange[ivalue]:
            netIdxRange[ivalue].remove(';')

    return netIdxRange




def getCell(fileAddress):
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
    for idx, line in enumerate(file):
        if idx >= start_idx and idx <= end_idx:
           if line.startswith("-"):
              line = line.replace("- ","").replace("\n","")
              cellID = line.split(" + ")[0].split(" ")[0]
              cellInfo[cellID] = dict()
              macroID = line.split(" + ")[0].split(" ")[1]
              pos = [float(value) for value in line.split(" + ")[1].split("PLACED")[1].strip().split('(')[1].split(')')[0].strip().split(" ")]
              orientation =  line.split(" + ")[1].split("PLACED")[1].strip().split('(')[1].split(')')[1].strip()
              cellInfo[cellID] = {'type':'cell','macroID':macroID,"position": pos, "orientation": orientation}
    return cellInfo





def getExtPinInfo(fileAddress):
    expin=dict()
    startIdx=int()
    endIdx=int()
    file =open(fileAddress)
    for idx, line in enumerate(file):
        line = line.strip()
        if line.startswith("PINS"):
            pinNumb = line.split("PINS")[1].replace("\n", "").strip()
            startIdx = idx
        elif line.startswith("END PINS") or line.startswith("- VDD") or line.startswith("- VSS"):
            endIdx = idx
            break
    file.close()


    whereisit=list()
    file =open(fileAddress)
    for idx, line in enumerate(file):
        if idx >startIdx and idx < endIdx:
            line=line.strip()
            if line.startswith("-") and 'VDD' not in line and 'VSS' not in line:
                pinName = line.split("-")[1].split("+")[0].strip()
                expin[pinName]=dict()
                direction = line.split("DIRECTION")[1].split("+")[0].strip()
                expin[pinName]['direction']=direction
                expin[pinName]['type']='PIN'
                whereisit.append(idx)
            if line.startswith("-") and ('VDD'  in line or 'VSS' in line):
                whereisit.append(idx)
                break
    file.close()

    for qidx in range(len(whereisit)):
        file=open(fileAddress)
        for kdx,kline in enumerate(file):

            kline=kline.strip()
            pinPos=list()
            pinOrient=str()
            if qidx !=len(whereisit)-1:
                if kdx >=whereisit[qidx] and kdx <whereisit[qidx+1]:
                    if kdx ==whereisit[qidx]:

                        if kline.split("-")[1].split("+")[0].strip()=='VSS' or kline.split("-")[1].split("+")[0].strip()=='VDD':
                            continue
                        pinName = kline.split("-")[1].split("+")[0].strip()
                    elif kline.startswith("+ LAYER"):
                        metalLayer = kline.split("+ LAYER")[1].split("(")[0].strip()
                    elif kline.startswith("+ PLACED"):
                        pinPosLine = kline.split("PLACED")[1].split("(")[1].split(")")[0].strip().split(" ")
                        for coord in pinPosLine:
                            pinPos.append(float(coord))
                        #z 성분 (layer number)
                        pinPos.append(int(metalLayer.replace("metal", "")))
                        pinOrient = kline.split(")")[1].replace("\n","").replace(";", "")
                    elif kline.startswith("+ FIXED"):
                        pinPosLine = kline.split("FIXED")[1].split("(")[1].split(")")[0].strip().split(" ")
                        for coord in pinPosLine:
                            pinPos.append(float(coord))
                        #z 성분 (layer number)
                        pinPos.append(int(metalLayer.replace("metal", "")))
                        pinOrient = kline.split(")")[1].replace("\n","").replace(";", "")
                    expin[pinName]['position']=pinPos
                    expin[pinName]['orientation']=pinOrient


            elif qidx ==len(whereisit)-1:
                if kdx >=whereisit[qidx] and kdx <endIdx:
                    if kdx ==whereisit[qidx]:

                        if kline.split("-")[1].split("+")[0].strip()=='VSS' or kline.split("-")[1].split("+")[0].strip()=='VDD':
                            continue
                        pinName = kline.split("-")[1].split("+")[0].strip()

                    elif kline.startswith("+ LAYER"):
                        metalLayer = kline.split("+ LAYER")[1].split("(")[0].strip()
                    elif kline.startswith("+ PLACED"):
                        pinPosLine = kline.split("PLACED")[1].split("(")[1].split(")")[0].strip().split(" ")
                        for coord in pinPosLine:
                            pinPos.append(float(coord))
                        #z 성분 (layer number)
                        pinPos.append(int(metalLayer.replace("metal", "")))
                        pinOrient = kline.split(")")[1].replace("\n","").replace(";", "")
                    elif kline.startswith("+ FIXED"):
                        pinPosLine = kline.split("FIXED")[1].split("(")[1].split(")")[0].strip().split(" ")
                        for coord in pinPosLine:
                            pinPos.append(float(coord))
                        #z 성분 (layer number)
                        pinPos.append(int(metalLayer.replace("metal", "")))
                        pinOrient = kline.split(")")[1].replace("\n","").replace(";", "")
                    expin[pinName]['position']=pinPos
                    expin[pinName]['orientation']=pinOrient

        file.close()
    return expin



def get_def_data_unit(defdef):
    data_unit=None
    file = open(defdef, 'r')
    for idx, line in enumerate(file):
        line = line.strip()
        if line.startswith("UNITS DISTANCE MICRONS"):
            data_unit=float(line.split(' ')[3])
            break

    if data_unit==None:
        print('Error : def_data_unit doesn\'t exist')
        return 'Error : def_data_unit doesn\'t exist : '+str(data_unit)

    return data_unit







def getpinport(netListInfo,macroInfo,cell,port_first_RECT,extPinInfo,defunit,lefunit):
    pinport=dict()
    start_idx=0
    start_kdx=0
    idx=int()
    eachcell=list()
    end_idx=len(netListInfo.keys())
    start_kdx=0
    proportion=lefunit/defunit

    for idx in range (start_idx, end_idx):
            netname =(list(netListInfo.keys())[idx])
            eachcell =(list(netListInfo.values())[idx])
            end_kdx=len(eachcell)
            netcellname=list()
            cellpos = list()
            port_position = list()
            xpos=float()
            ypos=float()
            pinpos=list()
            direct=str()
            for kdx in range (start_kdx, end_kdx):

                eachcellname=str()

                if eachcell[kdx].split(" ")[0] == 'PIN':
                    eachcellname=eachcell[kdx]
                    eachcellport=eachcell[kdx].split(" ")[1]
                    macroID='PIN'

                    if eachcellport in extPinInfo:
                        pinpos=extPinInfo[eachcellport]['position']
                        direct=extPinInfo[eachcellport]['direction']

                        netcellname.append({"net_name" : eachcellport,"pin_pos":pinpos, "direction" : direct})

                    else:
                        print('Error : the PIN in the net doesn\'t have information in EXTERNAL PINS')
                        return 'Error : the PIN in the net doesn\'t have information in EXTERNAL PINS : '+eachcell[kdx]
                else:

                    eachcellname=eachcell[kdx].split(" ")[0]
                    eachcellport=eachcell[kdx].split(" ")[1]

                    if eachcellname in cell:

                        macroID=cell[eachcellname]['macroID']
                        cellpos=cell[eachcellname]['position']

                        if macroID in macroInfo:
                            if eachcellport in macroInfo[macroID]:
                                port_position=port_first_RECT[macroID][eachcellport]
                                xpos=(port_position[2]+port_position[0])/(2*proportion) ############## 중간점/2 ####### /2를 한 이유는 lef와 def의 scailing을 맞추기 위해서
                                ypos=(port_position[3]+port_position[1])/(2*proportion) ############## 중간점/2 ####### /2를 한 이유는 lef와 def의 scailing을 맞추기 위해서

                                port_position=[xpos+cellpos[0],ypos+cellpos[1]]
                                rection=macroInfo[macroID][eachcellport]
                                    
                                netcellname.append({"cell_name":eachcellname, "macroID" : macroID,"cell_pos":cellpos,"used_port" : eachcellport,"port_pos": port_position,"direction" : rection})

                            else:
                                print('Error : the port of the cell doesn\'t exist in macro\'s information')
                                return 'Error : the port of the cell doesn\'t exist in macro\'s information : '+eachcell[kdx]
                        
                        else:
                            print('Error : the macroID of the cell doesn\'t exist in lef file')
                            return 'Error : the macroID of the cell doesn\'t exist in lef file : '+eachcell[kdx]

                    else:
                        print('Error : the cell in the net doesn\'t have information in COMPONENTS : net : ' +netname+' cell_and_port : '+eachcell[kdx])
                        return 'Error : the cell in the net doesn\'t have information in COMPONENTS : net : '+netname+' cell_and_port : '+eachcell[kdx]

            pinport.update({netname:netcellname})

    return pinport








'''Error : the PIN in the net doesn\'t have information in EXTERNAL PINS : '+eachcell[kdx]
Error : the port of the cell doesn\'t exist in macro\'s information : '+eachcell[kdx]
Error : the macroID of the cell doesn\'t exist in lef file : '+eachcell[kdx]
Error : the cell in the net doesn\'t have information in COMPONENTS : '+eachcell[kdx]'''

def get_temporary1_defdef(netinfo,defdef):
    ###  defdef 를 수정해서 (temp)def에 저장 하자
    return 0






def get_graph(pinport,mac,def_unit):
    graph_nodes=dict()

    checking_inputs_of_cell=list()
    candidtate_inputs_of_cell=list()
    checking_outputs_of_cell=list()
    candidtate_outputs_of_cell=list()


    for idx, ivalue in enumerate(pinport):
        candidtate_outputs_of_cell_list=list()
        checking_outputs_of_cell_str=str()
        position_list=list()
        OUTNODE_kdx=None
        list_to_list=list()
        name_of_OUTNODE=str()



        for kdx in range(len(pinport[ivalue])):
            if ('net_name' in pinport[ivalue][kdx] and pinport[ivalue][kdx]['direction']=='INPUT'):
                OUTNODE_kdx=kdx
                name_of_OUTNODE='PIN '+pinport[ivalue][kdx]['net_name']
                position_list.append(pinport[ivalue][kdx]['pin_pos'][0:2])

            elif ('cell_name' in pinport[ivalue][kdx] and pinport[ivalue][kdx]['direction']=='OUTPUT'):
                OUTNODE_kdx=kdx
                name_of_OUTNODE=pinport[ivalue][kdx]['cell_name']+' '+pinport[ivalue][kdx]['used_port']
                position_list.append(pinport[ivalue][kdx]['port_pos'])
                checking_outputs_of_cell_str=(pinport[ivalue][kdx]['cell_name']+' '+pinport[ivalue][kdx]['used_port']+' '+pinport[ivalue][kdx]['macroID'])

                checking_outputs_of_cell.append(pinport[ivalue][kdx]['cell_name']+' '+pinport[ivalue][kdx]['used_port'])

            elif 'net_name' in pinport[ivalue][kdx]:
                list_to_list.append('PIN '+pinport[ivalue][kdx]['net_name'])

            elif 'cell_name' in pinport[ivalue][kdx]:
                list_to_list.append(pinport[ivalue][kdx]['cell_name']+' '+pinport[ivalue][kdx]['used_port'])
                checking_inputs_of_cell.append(pinport[ivalue][kdx]['cell_name']+' '+pinport[ivalue][kdx]['used_port'])

                candidtate_outputs_of_cell_list.append(pinport[ivalue][kdx]['cell_name']+' '+pinport[ivalue][kdx]['used_port']+' '+pinport[ivalue][kdx]['macroID'])

        if OUTNODE_kdx==None:
            print('Error : There is no OUTNODE in this net, net')
            return 'Error : There is no OUTNODE in this net, net : '+ivalue
            

        for kdx in range(len(pinport[ivalue])):
            pinport[ivalue][kdx]['to']=list()
            pinport[ivalue][kdx]['from']=list()

            if kdx == OUTNODE_kdx:
                pinport[ivalue][kdx]['to']=list_to_list
                continue

            elif 'net_name' in pinport[ivalue][kdx]:
                pinport[ivalue][kdx]['from']=[name_of_OUTNODE]
                position_list.append(pinport[ivalue][kdx]['pin_pos'][0:2])

            elif 'cell_name' in pinport[ivalue][kdx]:
                pinport[ivalue][kdx]['from']=[name_of_OUTNODE]
                position_list.append(pinport[ivalue][kdx]['port_pos'])
        
        '''if len(position_list) == 1:############################################################ 나중에 다시 실행
            print('Warning : There is no connection in the net, net : '+ivalue)'''

        pinport[ivalue][OUTNODE_kdx]['wire_length_hpwl']=float()
        pinport[ivalue][OUTNODE_kdx]['wire_length_clique']=float()
        pinport[ivalue][OUTNODE_kdx]['wire_length_star']=float()
        pinport[ivalue][OUTNODE_kdx]['wire_length_hpwl']=get_new_wirelength_hpwl(position_list)
        pinport[ivalue][OUTNODE_kdx]['wire_length_clique']=get_new_wirelength_clique(position_list)
        pinport[ivalue][OUTNODE_kdx]['wire_length_star']=get_new_wirelength_star(position_list)

    
        if checking_outputs_of_cell_str != str():
            for kdx,kvalue in enumerate(mac):
                if kvalue==checking_outputs_of_cell_str.split(' ')[2]:
                    for tdx,tvalue in enumerate(mac[kvalue]):
                        if mac[kvalue][tvalue]=='OUTPUT':
                            continue
                        else:
                            candidtate_inputs_of_cell.append(checking_outputs_of_cell_str.split(' ')[0]+' '+tvalue)
    
        if candidtate_outputs_of_cell_list != []:
            for kdx in range(len(candidtate_outputs_of_cell_list)):
                for tdx,tvalue in enumerate(mac):
                    if tvalue == candidtate_outputs_of_cell_list[kdx].split(' ')[2]:
                        for qdx,qvalue in enumerate(mac[tvalue]):
                            if mac[tvalue][qvalue]=='INPUT':
                                continue
                            else:
                                candidtate_outputs_of_cell.append(candidtate_outputs_of_cell_list[kdx].split(' ')[0]+' '+qvalue)

    temp3=list(set(candidtate_inputs_of_cell)-set(checking_inputs_of_cell))
    if len(temp3)!=0:
        print('Error : Some cells don\'t have enough inputs, not used cell_port'+str(temp3))
        return 'Error : Some cells don\'t have enough inputs, not used cell_port : '+ str(temp3)

    else:
        for idx,ivalue in enumerate(pinport):
            for kdx in range(len(pinport[ivalue])):
                if 'cell_name' in pinport[ivalue][kdx] and pinport[ivalue][kdx]['direction']=='OUTPUT':

                    for tdx,tvalue in enumerate(mac):
                        if tvalue == pinport[ivalue][kdx]['macroID']:

                            for qdx,qvalue in enumerate(mac[tvalue]):
                                if mac[tvalue][qvalue]=='INPUT':

                                    pinport[ivalue][kdx]['from'].append(pinport[ivalue][kdx]['cell_name']+' '+qvalue)
                
                elif 'cell_name' in pinport[ivalue][kdx] and pinport[ivalue][kdx]['direction']=='INPUT':

                    for tdx,tvalue in enumerate(mac):
                        if tvalue == pinport[ivalue][kdx]['macroID']:

                            for qdx,qvalue in enumerate(mac[tvalue]):
                                if mac[tvalue][qvalue]=='OUTPUT':

                                    pinport[ivalue][kdx]['to'].append(pinport[ivalue][kdx]['cell_name']+' '+qvalue)


    temp4=list(set(candidtate_outputs_of_cell)-set(checking_outputs_of_cell))
    if len(temp4)!=0:
        print('Error : Some cells\' outputs are not used , verilog file couldn\'t be created because of them')
        return 'Error : Some cells\' outputs are not used , verilog file couldn\'t be created because of them : '+str(temp4)

    for idx,ivalue in enumerate(pinport):
        for kdx in range(len(pinport[ivalue])):

            if 'cell_name' in pinport[ivalue][kdx]:
                if pinport[ivalue][kdx]['direction']=='OUTPUT':

                    graph_nodes.update({pinport[ivalue][kdx]['cell_name']+' '+pinport[ivalue][kdx]['used_port']:{'type':'cell','direction':pinport[ivalue][kdx]['direction'],\
                        'to':pinport[ivalue][kdx]['to'],'from':pinport[ivalue][kdx]['from'],'macroID':pinport[ivalue][kdx]['macroID'],'wire_length_hpwl': float(pinport[ivalue][kdx]['wire_length_hpwl'])/def_unit,\
                        'wire_length_clique': float(pinport[ivalue][kdx]['wire_length_clique'])/def_unit, 'wire_length_star':float(pinport[ivalue][kdx]['wire_length_star'])/def_unit}})
                
                else:
                    graph_nodes.update({pinport[ivalue][kdx]['cell_name']+' '+pinport[ivalue][kdx]['used_port']:{'type':'cell','direction':pinport[ivalue][kdx]['direction'],\
                        'to':pinport[ivalue][kdx]['to'],'from':pinport[ivalue][kdx]['from'],'macroID':pinport[ivalue][kdx]['macroID']}})
            
            else:
                if pinport[ivalue][kdx]['direction']=='INPUT':
                    graph_nodes.update({'PIN '+pinport[ivalue][kdx]['net_name']:{'type':'PIN','direction':pinport[ivalue][kdx]['direction'],\
                        'to':pinport[ivalue][kdx]['to'],'from':pinport[ivalue][kdx]['from'],'wire_length_hpwl': float(pinport[ivalue][kdx]['wire_length_hpwl'])/def_unit,\
                        'wire_length_clique': float(pinport[ivalue][kdx]['wire_length_clique'])/def_unit, 'wire_length_star':float(pinport[ivalue][kdx]['wire_length_star'])/def_unit}})
                else:
                    graph_nodes.update({'PIN '+pinport[ivalue][kdx]['net_name']:{'type':'PIN','direction':pinport[ivalue][kdx]['direction'],\
                        'to':pinport[ivalue][kdx]['to'],'from':pinport[ivalue][kdx]['from']}})                    



    return graph_nodes





'''
' : Some cells don\'t have enough inputs, not used cell_port : '+ str(temp3)
' : Some cells\' outputs are not used , verilog file couldn\'t be created because of them : '+str(temp4)'''

def get_temporary2_defdef(graph,name_of_temp_defdef,macroInfo,def_data_unit,if_testing):
    defdef='../data/deflef_to_graph_and_verilog/0. defs/'+name_of_temp_defdef.replace('_revised(temp).def','')+'/'

    if name_of_temp_defdef not in os.listdir(defdef.replace('_revised/','/')):
        shutil.copy2(defdef+name_of_temp_defdef.split('(temp)')[0]+'.def',defdef+name_of_temp_defdef)

    else:
        netinfo=get_net_summary(defdef+name_of_temp_defdef,leflef,if_testing)
        will_be_graph=get_graph(netinfo,macroInfo,def_data_unit)
        if type(will_be_graph) !=type(' '):
            return will_be_graph

    will_be_net=str()
    will_be_change=defdef+name_of_temp_defdef

    error1=str()
    error2=str()
    error3=str()

    ##if  ' There is no OUTNODE in this net' in graph:
        ####### 새로운 external pin (direction은 input)을 만든 후
            #### PINS 수 갱신
            #### PINS 안에 새로 만든 pin 갱신
            #### 새로 만든 pin을 해당 net에 갱신
    
    ##if 'Some cells don\'t have enough inputs, not used cell_port :' in graph:
        ###### 새로운 external pin (direction은 input)을 만든 후
            #### PINS 수 갱신
            #### PINS 안에 새로 만든 pin 갱신
            #### 새로 만든 pin을 사용하지 않는 cell의 port와 연결하는 새로운 net 만든 후
            #### NETS 수 갱신
            #### NETS 안에 새로 만든 net 갱신

    if 'Some cells\' outputs are not used , verilog file couldn\'t be created because of them :' in graph:

        conversion_lines=list()
        f= open(will_be_change,'r')
        while True:
            line=f.readline()
            if not line or 'END NETS' in line:
                break
            else:
                conversion_lines.append(line)
        f.close()

        add_lines=str()
        if conversion_lines[len(conversion_lines)-1]==conversion_lines[len(conversion_lines)-2]:
            conversion_lines.pop()
        if conversion_lines[len(conversion_lines)-1]==';\n':
            conversion_lines[len(conversion_lines)-1]=';'


        for idx in range(len(conversion_lines)):
            add_lines=add_lines+conversion_lines[idx]
        

        neccessary_unconnected_net=(graph.split(': [')[1].split(']')[0].replace("'",'').split(', '))

        for idx in range(len(neccessary_unconnected_net)):
            will_be_net=will_be_net+'- UNCONNECTED_TEMP_'+str(idx)+'\n  ( '+neccessary_unconnected_net[idx]+' )\n ;'

            if idx != len(neccessary_unconnected_net)-1:
                will_be_net=will_be_net+'\n'
        
        add_lines=add_lines+will_be_net+'\nEND NETS'+'\n'+'\nEND DESIGN'
        
        ff=open(will_be_change,'w') 
        ff.write(add_lines)
        ff.close()

        error3='\nTEMPORARILY ADDED NETS FOR UNCONNEDCTED_PINS_OF_CELL : '+str(len(neccessary_unconnected_net))

    return error1+error2+error3







def get_new_wirelength_hpwl(position_list_list):
    if len(position_list_list)==1:
        return float(0)

    else:

        min_x=float()
        max_x=float()
        min_y=float()
        max_y=float()
        for kkdx in range(len(position_list_list)):
            if max_x<position_list_list[kkdx][0]:
                max_x=position_list_list[kkdx][0]
            if max_y<position_list_list[kkdx][1]:
                max_y=position_list_list[kkdx][1]
        min_x=max_x
        min_y=max_y
        for kkdx in range(len(position_list_list)):
            if min_x>position_list_list[kkdx][0]:
                min_x=position_list_list[kkdx][0]
            if min_y>position_list_list[kkdx][1]:
                min_y=position_list_list[kkdx][1]


        ans=(float(max_x)-float(min_x))+float((max_y)-float(min_y))
        return ans




def get_new_wirelength_star(position_list_list): 
    if len(position_list_list)==1:
        return float(0)
    else:

        dis_x=float()
        dis_y=float()
        start_x=float(position_list_list[0][0])
        start_y=float(position_list_list[0][1])

        for kkdx in range(len(position_list_list)):
                dis_x=dis_x+abs(start_x-float(position_list_list[kkdx][0]))
                dis_y=dis_y+abs(start_y-float(position_list_list[kkdx][1]))

        ans=dis_x+dis_y
        return ans




def get_new_wirelength_clique(position_list_list):
    if len(position_list_list)==1:
        return float(0)
    else:

        dis_x=float()
        dis_y=float()
        start_x=float()
        start_y=float()
        for iiidx in range(len(position_list_list)):
            for kkkdx in range(len(position_list_list)):
                if kkkdx <= iiidx :
                    continue
                else:
                    dis_x=dis_x+abs(float(position_list_list[iiidx][0])-float(position_list_list[kkkdx][0]))
                    dis_y=dis_y+abs(float(position_list_list[iiidx][1])-float(position_list_list[kkkdx][1]))
            ans=dis_x+dis_y
        return ans




def get_net_summary(defdef,leflef,if_testing):
    macroInfo = getMacroInfo(leflef)
    port_first_RECT=Get_firstRECT_macro(leflef)
    lef_data_unit=get_lef_data_unit(leflef)
    netListInfo = getNetListInfo(defdef) 
    cell=getCell(defdef)
    extPinInfo = getExtPinInfo(defdef)
    def_data_unit=get_def_data_unit(defdef)
    netnet=getpinport(netListInfo,macroInfo,cell,port_first_RECT,extPinInfo,def_data_unit,lef_data_unit)
    if if_testing==1:
        netnet=temp_for_file(netnet)

    return netnet




def temp_for_file(nets):



    return nets



if __name__ == "__main__":
    arguments=sys.argv
    def_name=arguments[1]
    inputdef=def_name.split('.def')[0]+'_revised.def'
    inputlef='NangateOpenCellLibrary.mod.lef'
    ##inputdef='gcd.def'



    if_testing=int()



    name_of_defdef=inputdef.replace('.def','')
    leflef="../data/deflef_to_graph_and_verilog/1. lefs/"+inputlef
    defdef="../data/deflef_to_graph_and_verilog/0. defs/"+name_of_defdef.replace('_revised','')+'/'+inputdef


    list_of_data_directory=list()
    targetdir=r'../data/deflef_to_graph_and_verilog/3. graphs/'
    files = os.listdir(targetdir)
    for i in files :
            if os.path.isdir(targetdir+r"//"+i):
                list_of_data_directory.append(i)






    ffiillee='../data/deflef_to_graph_and_verilog/3. graphs/'+name_of_defdef+'(temp)/net_info_for_graph_'+name_of_defdef+'(temp).json'

    temporary_net_info='../data/deflef_to_graph_and_verilog/3. graphs/'+name_of_defdef+'(temp)/temporary_net_info_'+name_of_defdef+'(temp).json'

    temporary_def=name_of_defdef+'(temp).def'

    temporary_def_file_name='../data/deflef_to_graph_and_verilog/0. defs/'+name_of_defdef.replace('_revised','')+'/'+temporary_def

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ parsing 
    macroInfo = getMacroInfo(leflef)
    def_data_unit=get_def_data_unit(defdef)
    area_die=getAreaInfo(defdef)

    netinfo=get_net_summary(defdef,leflef,if_testing)

################################################
    '''while type(netinfo)==type(''):
        get_temporary1_defdef(netinfo,defdef)
        netinfo=get_net_summary(new_defdef,leflef,if_testing)'''
    shutil.copyfile(defdef,temporary_def_file_name)


    if name_of_defdef+'(temp)' not in list_of_data_directory:
        os.mkdir('../data/deflef_to_graph_and_verilog/3. graphs/'+name_of_defdef+'(temp)')


    with open(temporary_net_info, 'w') as tempfile:
        json.dump(netinfo,tempfile,indent=4)

    

    with open(temporary_net_info, 'r') as temp1file:
        netinfo=json.load(temp1file)

    will_be_graph=get_graph(netinfo,macroInfo,def_data_unit)

    total_error_of_graph=str()
    
    while type(will_be_graph) == type(' '):
        info_error=str()

        info_error=get_temporary2_defdef(will_be_graph,temporary_def,macroInfo,def_data_unit,if_testing)
        if type(info_error) ==type(' '):
            netinfo=get_net_summary(temporary_def_file_name,leflef,if_testing)
            will_be_graph=get_graph(netinfo,macroInfo,def_data_unit)
            total_error_of_graph=total_error_of_graph+info_error
        else:
            netinfo=get_net_summary(temporary_def_file_name,leflef,if_testing)
            will_be_graph=info_error

    print(total_error_of_graph)




    netinfo.update({'def_unit_should_divide_distance':def_data_unit})
    netinfo.update({'def_die_area':area_die})

    with open(temporary_net_info, 'w') as tempfile:
        json.dump(netinfo,tempfile,indent=4)
        
    with open(ffiillee, 'w')as fgfille:
        json.dump(will_be_graph,fgfille, indent=4)
#########################################################################################


 


  
        