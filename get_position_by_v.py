
import json
import copy
import os
import numpy as np
import sys
import shutil
import re
import pickle
import pandas as pd
import time



def Get_info_lef(fileAddress):
    file = open(fileAddress, 'r')
    macroInfo = dict()
    data_unit=None
    macroID = None

    for idx, line in enumerate(file):
        line = line.strip()

        if line.startswith("DATABASE MICRONS"):
            pp=re.sub(r'[^0-9]','',line)
            data_unit=int(pp)

        if line.startswith("MACRO"):
            macroID = line.replace("MACRO", "").replace("\n", "").strip()
            macroInfo.update({macroID:{}})
            startIdx = idx
        if macroID != None:
            if line.startswith("END" +" " + macroID):
                endIdx = idx
                macroInfo[macroID].update({'idx_range':[startIdx, endIdx]})
    file.close()

    if data_unit==None:
        print('Error : lef_data_unit doesn\'t exist')
        return 'Error : lef_data_unit doesn\'t exist : '+str(data_unit)

    for macroID in macroInfo:
        startIdx = macroInfo[macroID]["idx_range"][0]
        endIdx = macroInfo[macroID]["idx_range"][1]
        file = open(fileAddress, 'r')
        for idx, line in enumerate(file):
            if idx > startIdx and idx < endIdx:
                line = line.strip()
                if line.startswith("PIN"):
                    pinID = line.replace("PIN", "").replace("\n", "").replace(";","").strip()
                    if pinID not in macroInfo[macroID]:
                        macroInfo[macroID].update({pinID:[]})

                elif line.startswith("RECT"):
                    rect = line.replace("RECT", "").replace("\n", "").replace(";","").strip().split(" ")
                    rect = [float(coord) for coord in rect]
                    if pinID not in macroInfo[macroID]:
                        continue
                    macroInfo[macroID][pinID].append(rect)

        if "VSS" in macroInfo[macroID]:
            del macroInfo[macroID]["VSS"]
        if "VDD" in macroInfo[macroID]:
            del macroInfo[macroID]["VDD"]
        if "idx_range" in macroInfo[macroID]:
            del macroInfo[macroID]['idx_range']
        file.close()

    return [macroInfo,data_unit]





def Get_info_def(fileAddress):

    range_macro=list()
    area_line=str()
    data_unit=None


    file = open(fileAddress)
    cellInfo = dict()
    for idx, line in enumerate(file):
        line = line.strip()

        if line.startswith("DIEAREA"):                                   
            area_line=line

        elif line.startswith("UNITS DISTANCE MICRONS"):
            pp=re.sub(r'[^0-9]','',line)
            data_unit=int(pp)

        elif line.startswith("COMPONENTS"):
            startc_idx = idx+1
        elif line.startswith("END COMPONENTS"):
            endc_idx = idx-1

        elif line.startswith("PINS"):
            startpIdx = idx+1

        elif line.startswith("END PINS"):
            endpIdx = idx-1

    file.close()

    if data_unit==None:
        print('Error : def_data_unit doesn\'t exist')
        return 'Error : def_data_unit doesn\'t exist : '+str(data_unit)
        
    range_macro.append(area_line.split(") (")[0].split('( ')[1].strip().split(' '))
    range_macro.append(area_line.split(") (")[1].split(' )')[0].strip().split(' '))

    for idx in range(len(range_macro)):
        for kdx in range(len(range_macro[idx])):
            range_macro[idx][kdx]=float(range_macro[idx][kdx])


    all_lines_pin=list()
    all_lines=list()

    file = open(fileAddress)
    for idx, line in enumerate(file):
        line=line.replace('\n','').strip()
        if idx >= startc_idx and idx <= endc_idx:
            if line.startswith("-"):
                all_lines.append(line)
            else:
                all_lines[-1]=all_lines[-1]+' '+line

        elif idx >=startpIdx and idx <= endpIdx:
            if line.startswith("-"):
                all_lines_pin.append(line)
            else:
                all_lines_pin[-1]=all_lines_pin[-1]+' '+line
    
    vdd_int=int()
    vss_int=int()
    vdd_is=int()
    vss_is=int()
    checking_pin_list=copy.deepcopy(all_lines_pin)
    for idx in range(len(checking_pin_list)):
        if '- VDD' in all_lines_pin[idx]:
            vdd_is=1
            vdd_int=idx

        if '- VSS' in all_lines_pin[idx]:
            vss_is=1
            vss_int=idx

    if vdd_is==1:
        del all_lines_pin[vdd_int]
    if vss_is==1:
        del all_lines_pin[vss_int]

    cellInfo=dict()
    for kdx in range(len(all_lines)):
        info_list=all_lines[kdx].split(' ')

        cell_name=info_list[1]
        macro_id=info_list[2]
        position=[info_list[6],info_list[7]]
        orientation=info_list[9]
        cellInfo.update({cell_name:{'macroID':macro_id,'position':position,'orientation':orientation}})

    pinInfo=dict()
    for kdx in range(len(all_lines_pin)):
        info_list_pin=all_lines_pin[kdx].split(' ')

        layer_idx=int()
        direction_idx=int()
        position_idx=int()

        for jdx in range(len(info_list_pin)):
            if 'LAYER' in info_list_pin[jdx]:
                layer_idx=jdx
            elif 'DIRECTION' in info_list_pin[jdx]:
                direction_idx=jdx
            elif 'FIXED' in info_list_pin[jdx] or 'PLACED' in info_list_pin[jdx]:
                position_idx=jdx
        
        layer_list=info_list_pin[layer_idx:]
        direction_list=info_list_pin[direction_idx:]
        position_list=info_list_pin[position_idx:]


        pin_name=info_list_pin[1]
        layer_info=layer_list[1]
        direction='external_pin_'+direction_list[1]
        position=[position_list[2],position_list[3]]

        pinInfo.update({pin_name:{'position':position,'layer':layer_info,'direction':direction}})
    
    total_info=dict()
    total_info.update(cellInfo)
    total_info.update(pinInfo)
    range_macro[0][0]=float(float(range_macro[0][0])/float(data_unit))
    range_macro[0][1]=float(float(range_macro[0][1])/float(data_unit))
    range_macro[1][0]=float(float(range_macro[1][0])/float(data_unit))
    range_macro[1][1]=float(float(range_macro[1][1])/float(data_unit))

    return [range_macro,total_info,data_unit]






def get_position_with_wire_cap(def_unit,lef_unit,cell_extpin_position,std_pin_of_cell_position,All,wlm,wire_mode,capa):

    capa_wlm=wlm['capacitance']
    slope=wlm['slope']
    fanoutdict=dict()
    fanlist=list()
    refanlist=list()
    for ivalue in wlm:
        if 'fanout_length' in ivalue:
            fanoutdict[int(ivalue.split("fanout_length")[1])]=wlm[ivalue]

    fanlist=sorted(fanoutdict.keys())        
    refanlist=copy.deepcopy(fanlist)
    refanlist.sort(reverse=True)
    
    for ivalue in All:
        if All[ivalue]['type']=='cell':
            for kvalue in All[ivalue]['output']:
                if All[ivalue]['description']!='Constant cell' and All[ivalue]['description']!='MACRO':

                    if wire_mode=='wire_load':
                        how_many_fanout=len(All[ivalue]['output'][kvalue]['to'])
                        if how_many_fanout==0:
                            continue

                        if how_many_fanout in fanoutdict:
                            All[ivalue]['output'][kvalue]['load_cap_fall']=All[ivalue]['output'][kvalue]['load_cap_fall']+fanoutdict[how_many_fanout]*capa_wlm
                            All[ivalue]['output'][kvalue]['load_cap_rise']=All[ivalue]['output'][kvalue]['load_cap_rise']+fanoutdict[how_many_fanout]*capa_wlm

                        elif how_many_fanout>fanlist[-1]:
                            All[ivalue]['output'][kvalue]['load_cap_fall']=All[ivalue]['output'][kvalue]['load_cap_fall']+slope*(how_many_fanout-(fanlist[-1]))+fanoutdict[fanlist[-1]]*capa_wlm
                            All[ivalue]['output'][kvalue]['load_cap_rise']=All[ivalue]['output'][kvalue]['load_cap_rise']+slope*(how_many_fanout-(fanlist[-1]))+fanoutdict[fanlist[-1]]*capa_wlm

                        else:
                            min_int=int()
                            max_int=int()
                            for kdx in range(len(fanlist)):
                                if fanlist[kdx]<how_many_fanout and fanlist[kdx+1]>how_many_fanout:
                                    min_int=fanlist[kdx]
                                    break

                            for kdx in range(len(refanlist)):
                                if refanlist[kdx]>how_many_fanout and refanlist[kdx+1]<how_many_fanout:
                                    max_int=refanlist[kdx]
                                    break

                            All[ivalue]['output'][kvalue]['load_cap_fall']=All[ivalue]['output'][kvalue]['load_cap_fall']+(((how_many_fanout-min_int)/(max_int-min_int))*(fanoutdict[min_int]-fanoutdict[max_int]))+fanoutdict[min_int]*capa_wlm
                            All[ivalue]['output'][kvalue]['load_cap_rise']=All[ivalue]['output'][kvalue]['load_cap_rise']+(((how_many_fanout-min_int)/(max_int-min_int))*(fanoutdict[min_int]-fanoutdict[max_int]))+fanoutdict[min_int]*capa_wlm
############################################# macro의 상황을 따져야됨!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    else:
                        temp_position_list=list()
                        temp_ivalue_position=list()
                        temp_id=str()
                        if All[ivalue]['description']=='MACRO':
                            temp_id=ivalue.split(' ')[0].split('_stage')[0]
                            temp_ivalue_position=cell_extpin_position[temp_id]['position']
                        else:
                            temp_ivalue_position=cell_extpin_position[ivalue]['position']##

                        temp_output_position=std_pin_of_cell_position[All[ivalue]['macroID']][kvalue][0]
                        temp_position_list.append(get_real_position_on_die(temp_ivalue_position,temp_output_position,lef_unit,def_unit))

                        for jvalue in All[ivalue]['output'][kvalue]['to']:
                            temp_jvalue=jvalue
                            if ' ' in temp_jvalue:
                                temp_jvalue=temp_jvalue.split(' ')[0]
                                temp_ivalue_position=list()
                                temp_rid=str()
                                if All[temp_jvalue]['description']=='MACRO':
                                    temp_rid=temp_jvalue.split(' ')[0].split('_stage')[0]
                                    temp_ivalue_position=cell_extpin_position[temp_rid]['position']
                                else:
                                    temp_ivalue_position=cell_extpin_position[temp_jvalue]['position']##
                                temp_output_position=std_pin_of_cell_position[All[temp_jvalue]['macroID']][jvalue.split(' ')[1]][0]
                                temp_position_list.append(get_real_position_on_die(temp_ivalue_position,temp_output_position,lef_unit,def_unit))                            

                            else:
                                temp_ivalue_position=cell_extpin_position[temp_jvalue]['position']
                                temp_output_position=[float(0), float(0), float(0), float(0)]
                                temp_position_list.append(get_real_position_on_die(temp_ivalue_position,temp_output_position,lef_unit,def_unit))
############################################# macro의 상황을 따져야됨!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if wire_mode=='nothing':
                            continue
                        if wire_mode=='hpwl':
                            All[ivalue]['output'][kvalue]['load_cap_fall']=All[ivalue]['output'][kvalue]['load_cap_fall']+get_new_wirelength_hpwl(temp_position_list)*capa
                            All[ivalue]['output'][kvalue]['load_cap_rise']=All[ivalue]['output'][kvalue]['load_cap_rise']+get_new_wirelength_hpwl(temp_position_list)*capa
                        
                        elif wire_mode=='clique':
                            All[ivalue]['output'][kvalue]['load_cap_fall']=All[ivalue]['output'][kvalue]['load_cap_fall']+get_new_wirelength_clique(temp_position_list)*capa
                            All[ivalue]['output'][kvalue]['load_cap_rise']=All[ivalue]['output'][kvalue]['load_cap_rise']+get_new_wirelength_clique(temp_position_list)*capa

                        elif wire_mode=='star':
                            All[ivalue]['output'][kvalue]['load_cap_fall']=All[ivalue]['output'][kvalue]['load_cap_fall']+get_new_wirelength_star(temp_position_list)*capa
                            All[ivalue]['output'][kvalue]['load_cap_rise']=All[ivalue]['output'][kvalue]['load_cap_rise']+get_new_wirelength_star(temp_position_list)*capa

                del All[ivalue]['output'][kvalue]['to']
    return All






def get_real_position_on_die(ivalue,kvalue,lef_unit,def_unit):

    xpos=(float(ivalue[0])+(kvalue[0]+kvalue[2])/(2*lef_unit))/def_unit
    ypos=(float(ivalue[1])+(kvalue[1]+kvalue[3])/(2*lef_unit))/def_unit

    return [xpos,ypos]





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


def get_new_Delay_of_nodes_CLK(All,CLK_mode,liberty_file):

    if CLK_mode=='ideal':
        for ivalue in All:
            if All[ivalue]['type']=='pin':
                All[ivalue].update({'fall_Delay':0})
                All[ivalue].update({'rise_Delay':0})
                All[ivalue].update({'fall_Transition':0})
                All[ivalue].update({'rise_Transition':0})
            else:
                for kvalue in All[ivalue]['output']:
                    All[ivalue]['output'][kvalue].update({'fall_Delay':0})
                    All[ivalue]['output'][kvalue].update({'rise_Delay':0})
                    All[ivalue]['output'][kvalue].update({'fall_Transition':0})
                    All[ivalue]['output'][kvalue].update({'rise_Transition':0})
        return All

    else: ############################ 코딩 필요 (clk의 real한 경우)
        all_stage_delay=dict()
        dict_dict=dict()
        first_stage_delay=get_new_Delay_of_nodes_stage0(All,dict_dict,liberty_file)
        all_stage_delay=get_new_all_Delay_Transition_of_nodes(first_stage_delay,liberty_file)
        all_stage_delay_clk=get_skew_of_clk(all_stage_delay)
        return all_stage_delay_clk


def get_skew_of_clk(All):
    shortest_delay=float()
    max_delay=float()
    checking=list()
    for ivalue in All:
        if All[ivalue]['stage']==0 and All[ivalue]['type']=='cell':
            for kvalue in All[ivalue]['input']:
                temp_input_from=All[ivalue]['input'][kvalue]['from']
                if ' ' in temp_input_from:
                    temp_input_from=temp_input_from.split(' ')[0]
                    temp_rise_delay=All[temp_input_from]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]]['rise_Delay']
                    if max_delay<temp_rise_delay:
                        max_delay=temp_rise_delay
                else:
                    temp_rise_delay=All[temp_input_from]['rise_Delay']
                    if max_delay<temp_rise_delay:
                        max_delay=temp_rise_delay

    shortest_delay=max_delay
    for ivalue in All:
        if All[ivalue]['stage']==0 and All[ivalue]['type']=='cell':
            for kvalue in All[ivalue]['input']:
                temp_input_from=All[ivalue]['input'][kvalue]['from']
                if ' ' in temp_input_from:
                    temp_input_from=temp_input_from.split(' ')[0]
                    temp_rise_delay=All[temp_input_from]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]]['rise_Delay']
                    if shortest_delay>temp_rise_delay:
                        shortest_delay=temp_rise_delay
                else:
                    temp_rise_delay=All[temp_input_from]['rise_Delay']
                    if shortest_delay>temp_rise_delay:
                        shortest_delay=temp_rise_delay

    already_check=list()
    for ivalue in All:
        if All[ivalue]['stage']==0 and All[ivalue]['type']=='cell':
            for kvalue in All[ivalue]['input']:
                temp_input_from=All[ivalue]['input'][kvalue]['from']
                if temp_input_from not in already_check:
                    already_check.append(temp_input_from)

                    if ' ' in temp_input_from:
                        temp_port_from=temp_input_from.split(' ')[1]
                        temp_input_from=temp_input_from.split(' ')[0]
                        temp_rise_delay=All[temp_input_from]['output'][temp_port_from]['rise_Delay']
                        All[temp_input_from]['output'][temp_port_from]['rise_Delay']=temp_rise_delay-shortest_delay

                    else:
                        All[temp_input_from]['rise_Delay']=All[temp_input_from]['rise_Delay']-shortest_delay

    return All
        



def get_last_nodes(All):
    listlist=list()
    for ivalue in All:
        if len(All[ivalue]['to'])==0 and All[ivalue]['direction']=='INPUT':
            listlist.append(ivalue)
    return listlist


def get_list_of_last_one(list_list,one_last_node_output,All):
    list_list=list()
    checking=one_last_node_output
    while len(All[checking]['from'])!=0:
        if checking not in list_list:
            list_list.append(checking)
        input__checking=All[checking]['from'][0]
        if input__checking not in list_list:
            list_list.append(input__checking)
        checking=All[input__checking]['from'][0]

    if checking not in list_list:
        list_list.append(checking)


    return list_list



def get_lists_of_output(list_of_all,one_output,All):
    if one_output not in list_of_all:
        list_of_all.append(one_output)
        for jhvalue in All[one_output]['to']:
            if jhvalue not in list_of_all:
                list_of_all.append(jhvalue)

    if len(All[one_output]['from'])==0:
        return list_of_all

    else:
        for hvalue in All[one_output]['from']:
            if hvalue not in list_of_all:
                list_of_all.append(hvalue)
            
            temp_output=All[hvalue]['from'][0]
            temp_lists=list()
            temp_lists=get_lists_of_output(list_of_all,temp_output,All)
            for hjvalue in temp_lists:
                if hjvalue not in list_of_all:
                    list_of_all.append(hjvalue)

    return list_of_all



    '''checking_clk=nets[ivalue]['from'][0]
                        while len(nets[checking_clk]['from'])!=0:
                            if checking_clk not in group_of_clk:
                                group_of_clk.append(checking_clk)
                            input__checking=nets[checking_clk]['from'][0]
                            if input__checking not in group_of_clk:
                                group_of_clk.append(input__checking)
                            checking_clk=nets[input__checking]['from'][0]
                        if checking_clk not in group_of_clk:
                            group_of_clk.append(checking_clk)'''




def get_new_value_from_table(data_dictionary,value_transition,value_capacitance):
    table_capa=data_dictionary['load_capacitance']
    table_transition=data_dictionary['input_transition']
    data_list_list=data_dictionary['data_list']
    value_float=float()
    x1=float()
    x2=float()
    y1=float()
    y2=float()
    aaa=float()
    bbb=float()
    ccc=float()
    ddd=float()

    stryyy=str()
    nextyyy=str()
    indxxx=int()

    if value_capacitance<=float(table_capa[0]):
        stryyy=0

    elif value_capacitance>=float(table_capa[len(table_capa)-1]):
        stryyy=len(table_capa)-2

    else:
        for idx in range(len(table_capa)-1):
            if float(table_capa[idx])<=value_capacitance and value_capacitance<=float(table_capa[idx+1]):
                stryyy=idx

    y1=float(table_capa[stryyy])
    y2=float(table_capa[stryyy+1])

    if value_transition<=table_transition[0]:
        indxxx=0

    elif value_transition>=table_transition[len(table_transition)-1]:
        indxxx=len(table_transition)-2

    else:
        for idx in range(len(table_transition)-1):
            if table_transition[idx]<=value_transition and value_transition<=table_transition[idx+1]:
                indxxx=idx

    x1=table_transition[indxxx]
    x2=table_transition[indxxx+1]

    T11=float(data_list_list[stryyy][indxxx])
    T12=float(data_list_list[stryyy+1][indxxx])
    T21=float(data_list_list[stryyy][indxxx+1])
    T22=float(data_list_list[stryyy+1][indxxx+1])


    aaa=(value_transition-x1)/(x2-x1)
    bbb=(x2-value_transition)/(x2-x1)
    ccc=(value_capacitance-y1)/(y2-y1)
    ddd=(y2-value_capacitance)/(y2-y1)



    TTT11=T11*bbb*ddd
    TTT12=T12*bbb*ccc
    TTT21=T21*aaa*ddd
    TTT22=T22*aaa*ccc

    value_float=TTT11+TTT12+TTT21+TTT22
    return value_float







def get_delay_partition_of_All(ideal_clk__1,one_last_input,All,lib_add,lib_dict):
    temp_dict=dict()
    one_last_output=All[one_last_input]['from'][0]
    list_for_one_last_output=list()
    temp_list_of_one=list()
    list_for_one_last_output=get_lists_of_output(temp_list_of_one,one_last_output,All)
    for ivalue in list_for_one_last_output:
        temp_dict.update({ivalue:All[ivalue]})
    temp_dict.update({one_last_input:All[one_last_input]})

    temp_dict
    first_delay=get_new_Delay_of_nodes_stage0(temp_dict,ideal_clk__1,'wire_load',lib_add,lib_dict)
    all_delay=get_new_all_Delay_Transition_of_nodes(first_delay,'wire_load',lib_add,lib_dict)


    return all_delay








def get_new_Delay_of_nodes_stage0(All,TAll,lib_dict): ################ wire_mode: 'hpwl_model'의 경우, 'clique_model'의 경우, 'star_model'의 경우, 'wire_load_model'의 경우가 있다.

    for ivalue in All:
        if All[ivalue]['stage']==0:
            if All[ivalue]['type']=='pin':
                if All[ivalue]['pin_direction']=='input' and (ivalue !='clk' or ivalue !='iccad_clk'):################ sdc 파일
                    ####################################### sdc 파일
                    All[ivalue].update({'fall_Delay':float(0)})
                    All[ivalue].update({'rise_Delay':float(0)})
                    if sys.argv[1]=='NangateOpenCellLibrary.mod.lef':
                        All[ivalue].update({'rise_Transition':float(0)})
                        All[ivalue].update({'fall_Transition':float(0)})
                    else:
                        All[ivalue].update({'rise_Transition':float(0)})
                        All[ivalue].update({'fall_Transition':float(0)})

                elif All[ivalue]['pin_direction']=='input':
                    All[ivalue].update({'fall_Delay':float(0)})
                    All[ivalue].update({'rise_Delay':float(0)})
                    All[ivalue].update({'rise_Transition':float(0)})
                    All[ivalue].update({'fall_Transition':float(0)})



            elif All[ivalue]['type']=='cell':
                if All[ivalue]['description']=='Constant cell': ############################ (constant cell)
                    for kvalue in All[ivalue]['output']:
                        All[ivalue]['output'][kvalue].update({'fall_Delay':float(0)})
                        All[ivalue]['output'][kvalue].update({'rise_Delay':float(0)})
                        All[ivalue]['output'][kvalue].update({'rise_Transition':float(0)})
                        All[ivalue]['output'][kvalue].update({'fall_Transition':float(0)})

                else:
                    if All[ivalue]['description']=='Pos.edge D-Flip-Flop': ############################ (clk to q delay)
                        
                        for kvalue in All[ivalue]['output']:
                            ck_from=str()
                            if sys.argv[1]=='NangateOpenCellLibrary.mod.lef':
                                ck_from=TAll[ivalue]['input']['CK']['from']
                            else:
                                ck_from=TAll[ivalue]['input']['ck']['from']
                            checking_falling=float() ############# 인풋 파라미터1-1 클락의 경우 unateness가 non-unate이다.
                            checking_rising=float() ############# 인풋 파라미터1-2
                            checking_rising_delay=float()
                            if ' ' in ck_from:
                                checking_rising=TAll[ck_from.split(' ')[0]]['output'][ck_from.split(' ')[1]]['fall_Transition']
                                checking_rising_delay=TAll[ck_from.split(' ')[0]]['output'][ck_from.split(' ')[1]]['fall_Delay']
                            else:
                                checking_rising=TAll[ck_from]['rise_Transition']
                                checking_rising_delay=TAll[ck_from]['rise_Delay']

                            All[ivalue]['output'][kvalue].update({'fall_Delay':get_new_value_from_table(lib_dict[All[ivalue]['macroID']]['output'][kvalue]['condition_0']['fall_delay'],checking_rising,All[ivalue]['output'][kvalue]['load_cap_fall'])+checking_rising_delay})
                            All[ivalue]['output'][kvalue].update({'rise_Delay':get_new_value_from_table(lib_dict[All[ivalue]['macroID']]['output'][kvalue]['condition_0']['rise_delay'],checking_rising,All[ivalue]['output'][kvalue]['load_cap_rise'])+checking_rising_delay})
                            All[ivalue]['output'][kvalue].update({'fall_Transition':get_new_value_from_table(lib_dict[All[ivalue]['macroID']]['output'][kvalue]['condition_0']['fall_transition'],checking_rising,All[ivalue]['output'][kvalue]['load_cap_fall'])})
                            All[ivalue]['output'][kvalue].update({'rise_Transition':get_new_value_from_table(lib_dict[All[ivalue]['macroID']]['output'][kvalue]['condition_0']['rise_transition'],checking_rising,All[ivalue]['output'][kvalue]['load_cap_rise'])})

                    else: ####################################################(macro의 경우)
                        for kvalue in All[ivalue]['output']:
                            if All[ivalue]['output'][kvalue]['stage']==0:
                                All[ivalue]['output'][kvalue].update({'fall_Delay':float(0)})
                                All[ivalue]['output'][kvalue].update({'rise_Delay':float(0)})
                                All[ivalue]['output'][kvalue].update({'fall_Transition':float(0)})
                                All[ivalue]['output'][kvalue].update({'rise_Transition':float(0)})



    return All






def get_new_all_Delay_Transition_of_nodes(All,lib_dict):
    max_stage_number=int()
    for idx,ivalue in enumerate(All):
        if max_stage_number<All[ivalue]['stage']:
            max_stage_number=All[ivalue]['stage']

    for idx in range(max_stage_number+1):
        if idx==0:
            continue

        '''for kvalue in All:
            if All[kvalue]['type']=='cell':
                if All[kvalue]['description']=='MACRO':
                    for jvalue in All[kvalue]['output']:
                        if All[kvalue]['output'][jvalue]['stage']==idx:
                            condition_string=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][0]

                            unateness=condition_string.split(' unateness : ')[0]
                            related_pin=condition_string.split(', related_pin : ')[1].split(', unateness :')[0]
                            from_related_pin=All[kvalue]['input'][related_pin]['from']

                            constant_fall_D=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['condition_0']['fall_delay']
                            constant_rise_D=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['condition_0']['rise_delay']
                            constant_fall_T=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['condition_0']['fall_transition']
                            constant_rise_T=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['condition_0']['rise_transition']         

                            previous_fall_D=float()
                            previous_rise_D=float()

                            if ' ' in from_related_pin:
                                from_related_pin=from_related_pin.split(' ')[0]

                            if All[from_related_pin]['type']=='pin':
                                previous_fall_D=All[from_related_pin]['fall_Delay']
                                previous_rise_D=All[from_related_pin]['rise_Delay']
                            else:
                                previous_fall_D=All[from_related_pin]['output'][All[kvalue]['input'][related_pin]['from'].split(' ')[1]]['fall_Delay']
                                previous_rise_D=All[from_related_pin]['output'][All[kvalue]['input'][related_pin]['from'].split(' ')[1]]['rise_Delay']
                            
                            if unateness=='positive_unate':
                                All[kvalue]['output'][jvalue].update({'fall_Delay':previous_fall_D+constant_fall_D})
                                All[kvalue]['output'][jvalue].update({'rise_Delay':previous_rise_D+constant_rise_D})
                            else:
                                All[kvalue]['output'][jvalue].update({'fall_Delay':previous_fall_D+constant_rise_D})
                                All[kvalue]['output'][jvalue].update({'rise_Delay':previous_rise_D+constant_fall_D})

                            All[kvalue]['output'][jvalue].update({'fall_Transition':constant_fall_T})
                            All[kvalue]['output'][jvalue].update({'rise_Transition':constant_rise_T})
                            All[kvalue]['output'][jvalue].update({'latest_pin_fall':[related_pin,unateness]})
                            All[kvalue]['output'][jvalue].update({'latest_pin_rise':[related_pin,unateness]})'''


        for kvalue in All:
            if All[kvalue]['stage']==idx:
                if len(All[kvalue]['output'])==0:
                    continue
                if All[kvalue]['description']=='MACRO':
                    for jvalue in All[kvalue]['output']:
                        condition_string=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][0]

                        unateness=condition_string.split(' unateness : ')[1]
                        related_pin=condition_string.split(', related_pin : ')[1].split(', unateness :')[0]
                        from_related_pin=All[kvalue]['input'][related_pin]['from']

                        constant_fall_D=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['condition_0']['fall_delay']
                        constant_rise_D=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['condition_0']['rise_delay']
                        constant_fall_T=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['condition_0']['fall_transition']
                        constant_rise_T=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['condition_0']['rise_transition']         

                        previous_fall_D=float()
                        previous_rise_D=float()

                        if ' ' in from_related_pin:
                            from_related_pin=from_related_pin.split(' ')[0]
                            previous_fall_D=All[from_related_pin]['output'][All[kvalue]['input'][related_pin]['from'].split(' ')[1]]['fall_Delay']
                            previous_rise_D=All[from_related_pin]['output'][All[kvalue]['input'][related_pin]['from'].split(' ')[1]]['rise_Delay']

                        else:
                            previous_fall_D=All[from_related_pin]['fall_Delay']
                            previous_rise_D=All[from_related_pin]['rise_Delay']


                        if unateness=='positive_unate':
                            All[kvalue]['output'][jvalue].update({'fall_Delay':previous_fall_D+constant_fall_D})
                            All[kvalue]['output'][jvalue].update({'rise_Delay':previous_rise_D+constant_rise_D})
                        else:
                            All[kvalue]['output'][jvalue].update({'fall_Delay':previous_rise_D+constant_fall_D})
                            All[kvalue]['output'][jvalue].update({'rise_Delay':previous_fall_D+constant_rise_D})

                        All[kvalue]['output'][jvalue].update({'fall_Transition':constant_fall_T})
                        All[kvalue]['output'][jvalue].update({'rise_Transition':constant_rise_T})
                        All[kvalue]['output'][jvalue].update({'latest_pin_fall':[related_pin,unateness]})
                        All[kvalue]['output'][jvalue].update({'latest_pin_rise':[related_pin,unateness]})



                else:
                    for jvalue in All[kvalue]['output']:
                        fall_delay_candidate=list()
                        rise_delay_candidate=list()
                        the_latest_fall_transition=float()
                        the_latest_rise_transition=float()
                        load_capa_fall=All[kvalue]['output'][jvalue]['load_cap_fall']
                        load_capa_rise=All[kvalue]['output'][jvalue]['load_cap_rise']

                        if len(lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'])==1:

                            only_input=str()
                            for rvalue in All[kvalue]['input']:
                                only_input=rvalue
                            from_input=All[kvalue]['input'][only_input]['from']
                            temp_fall_Delay=float()
                            temp_rise_Delay=float()
                            temp_fall_T=float()
                            temp_rise_T=float()

                            if ' ' in from_input:
                                from_input=from_input.split(' ')[0]
                                temp_fall_Delay=All[from_input]['output'][All[kvalue]['input'][only_input]['from'].split(' ')[1]]['fall_Delay']
                                temp_rise_Delay=All[from_input]['output'][All[kvalue]['input'][only_input]['from'].split(' ')[1]]['rise_Delay']
                                temp_fall_T=All[from_input]['output'][All[kvalue]['input'][only_input]['from'].split(' ')[1]]['fall_Transition']
                                temp_rise_T=All[from_input]['output'][All[kvalue]['input'][only_input]['from'].split(' ')[1]]['rise_Transition']

                            else:
                                temp_fall_Delay=All[from_input]['fall_Delay']
                                temp_rise_Delay=All[from_input]['rise_Delay']
                                temp_fall_T=All[from_input]['fall_Transition']
                                temp_rise_T=All[from_input]['rise_Transition']

                            path_to_table=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['condition_0']
                                    
                            unateness=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][0].split(", unateness : ")[1].strip()
                            if unateness=='positive_unate':
                                fall_delay_candidate.append([only_input,[unateness,'No_condition',temp_fall_Delay]])
                                rise_delay_candidate.append([only_input,[unateness,'No_condition',temp_rise_Delay]])
                                df5_trans=path_to_table['fall_transition']
                                the_latest_fall_transition=get_new_value_from_table(df5_trans,temp_fall_T,load_capa_fall)
                                df5_trans=path_to_table['rise_transition']
                                the_latest_rise_transition=get_new_value_from_table(df5_trans,temp_rise_T,load_capa_rise)

                            else:
                                fall_delay_candidate.append([only_input,[unateness,'No_condition',temp_rise_Delay]])
                                rise_delay_candidate.append([only_input,[unateness,'No_condition',temp_fall_Delay]])
                                df5_trans=path_to_table['fall_transition']
                                the_latest_fall_transition=get_new_value_from_table(df5_trans,temp_rise_T,load_capa_fall)
                                df5_trans=path_to_table['rise_transition']
                                the_latest_rise_transition=get_new_value_from_table(df5_trans,temp_fall_T,load_capa_rise)

                        else:
                            other_pins=list()
                            unateness=str()


                            for tdx in range(len(lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'])):

                                temp_input=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][tdx].split(", related_pin : ")[1].split(', unateness')[0].strip()
                                from_temp_input=All[kvalue]['input'][temp_input]['from']

                                condition_number='condition_'+str(tdx)
                                path_to_table=lib_dict[All[kvalue]['macroID']]['output'][jvalue][condition_number]

                                temp_fall_Delay=float()
                                temp_rise_Delay=float()
                                temp_fall_T=float()
                                temp_rise_T=float()

                                if ' ' in from_temp_input:
                                    from_temp_input=from_temp_input.split(' ')[0]
                                    temp_fall_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['fall_Delay']
                                    temp_rise_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['rise_Delay']
                                    temp_fall_T=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['fall_Transition']
                                    temp_rise_T=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['rise_Transition']
                                else:
                                    temp_fall_Delay=All[from_temp_input]['fall_Delay']
                                    temp_rise_Delay=All[from_temp_input]['rise_Delay']
                                    temp_fall_T=All[from_temp_input]['fall_Transition']
                                    temp_rise_T=All[from_temp_input]['rise_Transition']

                                other_pins=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][tdx].split("condition : ")[1].split(", related_pin : ")[0].split(' & ')
                                unateness=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][tdx].split(", unateness : ")[1].strip()
                                other_pins_delay=list()

                                no_mark_other_pins=list()
                                for jdx in range(len(other_pins)):
                                    if '!' not in other_pins[jdx]:
                                        no_mark_other_pins.append(other_pins[jdx])
                                    else:
                                        no_mark_other_pins.append(other_pins[jdx].replace('!',''))

                                for jdx in range(len(other_pins)):
                                    temp_input_other_from=All[kvalue]['input'][no_mark_other_pins[jdx]]['from']
                                    temp_fall_other=float()
                                    temp_rise_other=float()

                                    if ' ' in temp_input_other_from:
                                        temp_input_other_from=temp_input_other_from.split(' ')[0]
                                        temp_fall_other=All[temp_input_other_from]['output'][All[kvalue]['input'][no_mark_other_pins[jdx]]['from'].split(' ')[1]]['fall_Delay']
                                        temp_rise_other=All[temp_input_other_from]['output'][All[kvalue]['input'][no_mark_other_pins[jdx]]['from'].split(' ')[1]]['rise_Delay']

                                    else:
                                        temp_fall_other=All[temp_input_other_from]['fall_Delay']
                                        temp_rise_other=All[temp_input_other_from]['rise_Delay']


                                    if '!' in other_pins[jdx]:
                                        other_pins_delay.append(temp_fall_other)
                                    else:
                                        other_pins_delay.append(temp_rise_other)
                                
                                if unateness=='negative_unate':

                                    df5_trans=path_to_table['fall_transition']
                                    if the_latest_fall_transition<get_new_value_from_table(df5_trans,temp_rise_T,load_capa_fall):
                                        the_latest_fall_transition=get_new_value_from_table(df5_trans,temp_rise_T,load_capa_fall)
                                    df5_trans=path_to_table['rise_transition']
                                    if the_latest_rise_transition<get_new_value_from_table(df5_trans,temp_fall_T,load_capa_rise):
                                        the_latest_rise_transition=get_new_value_from_table(df5_trans,temp_fall_T,load_capa_rise)

                                    kk=int()
                                    for jdx in range(len(other_pins_delay)):
                                        if other_pins_delay[jdx]<=temp_rise_Delay:
                                            kk=kk+1
                                    if kk == len(other_pins_delay):
                                        fall_delay_candidate.append([temp_input,[unateness,'condition_number: '+str(tdx),temp_rise_Delay]])
                                
                                    qq=int()
                                    for jdx in range(len(other_pins_delay)):
                                        if other_pins_delay[jdx]<=temp_fall_Delay:
                                            qq=qq+1
                                    if qq == len(other_pins_delay):
                                        rise_delay_candidate.append([temp_input,[unateness,'condition_number: '+str(tdx),temp_fall_Delay]])

                                if unateness=='positive_unate':

                                    df5_trans=path_to_table['fall_transition']
                                    if the_latest_fall_transition<get_new_value_from_table(df5_trans,temp_fall_T,load_capa_fall):
                                        the_latest_fall_transition=get_new_value_from_table(df5_trans,temp_fall_T,load_capa_fall)
                                    df5_trans=path_to_table['rise_transition']
                                    if the_latest_rise_transition<get_new_value_from_table(df5_trans,temp_rise_T,load_capa_rise):
                                        the_latest_rise_transition=get_new_value_from_table(df5_trans,temp_rise_T,load_capa_rise)

                                    kk=int()
                                    for jdx in range(len(other_pins_delay)):
                                        if other_pins_delay[jdx]<=temp_fall_Delay:
                                            kk=kk+1
                                    if kk == len(other_pins_delay):
                                        fall_delay_candidate.append([temp_input,[unateness,'condition_number: '+str(tdx),temp_fall_Delay]])
                                
                                    qq=int()
                                    for jdx in range(len(other_pins_delay)):
                                        if other_pins_delay[jdx]<=temp_rise_Delay:
                                            qq=qq+1
                                    if qq == len(other_pins_delay):
                                        rise_delay_candidate.append([temp_input,[unateness,'condition_number: '+str(tdx),temp_rise_Delay]])
                            

                            if len(fall_delay_candidate) ==0:
                                for tdx in range(len(lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'])):
                                    temp_input=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][tdx].split(", related_pin : ")[1].split(', unateness')[0]
                                    from_temp_input=All[kvalue]['input'][temp_input]['from']

                                    temp_fall_Delay=float()
                                    temp_rise_Delay=float()
                                    if ' ' in from_temp_input:
                                        from_temp_input=from_temp_input.split(' ')[0]
                                        temp_fall_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['fall_Delay']
                                        temp_rise_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['rise_Delay']

                                    else:
                                        temp_fall_Delay=All[from_temp_input]['fall_Delay']
                                        temp_rise_Delay=All[from_temp_input]['rise_Delay']


                                    other_pins=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][tdx].split("condition : ")[1].split(", related_pin : ")[0].split(' & ')
                                    unateness=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][tdx].split(", unateness : ")[1].strip()
                                    if unateness=='negative_unate':
                                        fall_delay_candidate.append([temp_input,[unateness,'condition_number: '+str(tdx),temp_rise_Delay]])
                                    else:
                                        fall_delay_candidate.append([temp_input,[unateness,'condition_number: '+str(tdx),temp_fall_Delay]])


                            if len(rise_delay_candidate) ==0:

                                for tdx in range(len(lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'])):
                                    temp_input=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][tdx].split(", related_pin : ")[1].split(', unateness')[0].strip()
                                    from_temp_input=All[kvalue]['input'][temp_input]['from']

                                    temp_fall_Delay=float()
                                    temp_rise_Delay=float()

                                    if ' ' in from_temp_input:
                                        from_temp_input=from_temp_input.split(' ')[0]
                                        temp_fall_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['fall_Delay']
                                        temp_rise_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['rise_Delay']

                                    else:
                                        temp_fall_Delay=All[from_temp_input]['fall_Delay']
                                        temp_rise_Delay=All[from_temp_input]['rise_Delay']


                                    other_pins=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][tdx].split("condition : ")[1].split(", related_pin : ")[0].split(' & ')
                                    unateness=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][tdx].split(", unateness : ")[1].strip()
                                    if unateness=='negative_unate':
                                        rise_delay_candidate.append([temp_input,[unateness,'condition_number: '+str(tdx),temp_fall_Delay]])
                                    else:
                                        rise_delay_candidate.append([temp_input,[unateness,'condition_number: '+str(tdx),temp_rise_Delay]])
            ###############################################################

                        fall_delay_finals=list()
                        for tdx in range(len(fall_delay_candidate)):
                            who_is_the_input=fall_delay_candidate[tdx][0]
                            from_the_input=All[kvalue]['input'][who_is_the_input]['from']

                            trans_fall_from_input=float()
                            trans_rise_from_input=float()

                            if ' ' in from_the_input:
                                from_the_input=from_the_input.split(' ')[0]
                                trans_fall_from_input=All[from_the_input]['output'][All[kvalue]['input'][who_is_the_input]['from'].split(' ')[1]]['fall_Transition']
                                trans_rise_from_input=All[from_the_input]['output'][All[kvalue]['input'][who_is_the_input]['from'].split(' ')[1]]['rise_Transition']


                            else:
                                trans_fall_from_input=All[from_the_input]['fall_Transition']
                                trans_rise_from_input=All[from_the_input]['rise_Transition']

                            
                            load_capa=All[kvalue]['output'][jvalue]['load_cap_fall']

                            input_ttrraann=float()
                            unate=str()
                            df5_delay=list()
                            df5_trans=list()
                            if fall_delay_candidate[tdx][1][1]=='No_condition':
                                path_to_table=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['condition_0']
                            else:
                                condition_number='condition_'+fall_delay_candidate[tdx][1][1].split(': ')[1]
                                path_to_table=lib_dict[All[kvalue]['macroID']]['output'][jvalue][condition_number]

                            if fall_delay_candidate[tdx][1][0]=='negative_unate':
                                unate='negative_unate'
                                input_ttrraann=trans_rise_from_input
                
                            else:
                                unate='positive_unate'
                                input_ttrraann=trans_fall_from_input


                            df5_delay=path_to_table['fall_delay']
                            df5_trans=path_to_table['fall_transition']

                            fall_delay_finals.append([fall_delay_candidate[tdx][0],fall_delay_candidate[tdx][1][2]+get_new_value_from_table(df5_delay,input_ttrraann,load_capa),str(),unate])
                            


                        rise_delay_finals=list()
                        for tdx in range(len(rise_delay_candidate)):
                            who_is_the_input=rise_delay_candidate[tdx][0]
                            from_the_input=All[kvalue]['input'][who_is_the_input]['from']

                            trans_fall_from_input=float()
                            trans_rise_from_input=float()

                            if ' ' in from_the_input:
                                from_the_input=from_the_input.split(' ')[0]
                                trans_fall_from_input=All[from_the_input]['output'][All[kvalue]['input'][who_is_the_input]['from'].split(' ')[1]]['fall_Transition']
                                trans_rise_from_input=All[from_the_input]['output'][All[kvalue]['input'][who_is_the_input]['from'].split(' ')[1]]['rise_Transition']


                            else:
                                trans_fall_from_input=All[from_the_input]['fall_Transition']
                                trans_rise_from_input=All[from_the_input]['rise_Transition']


                            load_capa=All[kvalue]['output'][jvalue]['load_cap_rise']
                            input_ttrraann=float()
                            unate=str()
                            df5_delay=list()
                            df5_trans=list()
                            if rise_delay_candidate[tdx][1][1]=='No_condition':
                                path_to_table=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['condition_0']
                            else:
                                condition_number='condition_'+rise_delay_candidate[tdx][1][1].split(': ')[1]
                                path_to_table=lib_dict[All[kvalue]['macroID']]['output'][jvalue][condition_number]

                            if rise_delay_candidate[tdx][1][0]=='negative_unate':
                                unate='negative_unate'
                                input_ttrraann=trans_fall_from_input

                            else:
                                unate='positive_unate'
                                input_ttrraann=trans_rise_from_input


                            df5_delay=path_to_table['rise_delay']
                            df5_trans=path_to_table['rise_transition']

                            rise_delay_finals.append([rise_delay_candidate[tdx][0],rise_delay_candidate[tdx][1][2]+get_new_value_from_table(df5_delay,input_ttrraann,load_capa),str(),unate])

                        comparing_delay1=float()
                        number_of_latest1=int()
                        for tdx in range(len(fall_delay_finals)):
                            if comparing_delay1<fall_delay_finals[tdx][1]:
                                number_of_latest1=tdx
                                comparing_delay1=fall_delay_finals[tdx][1]

                        comparing_delay=float()
                        number_of_latest=int()
                        for tdx in range(len(rise_delay_finals)):
                            if comparing_delay<rise_delay_finals[tdx][1]:
                                number_of_latest=tdx
                                comparing_delay=rise_delay_finals[tdx][1]
                        

                        All[kvalue]['output'][jvalue].update({'fall_Delay':fall_delay_finals[number_of_latest1][1]})
                        All[kvalue]['output'][jvalue].update({'rise_Delay':rise_delay_finals[number_of_latest][1]})
                        All[kvalue]['output'][jvalue].update({'fall_Transition':the_latest_fall_transition})
                        All[kvalue]['output'][jvalue].update({'rise_Transition':the_latest_rise_transition})
                        All[kvalue]['output'][jvalue].update({'latest_pin_fall':[fall_delay_finals[number_of_latest1][0],fall_delay_finals[number_of_latest1][3]]})
                        All[kvalue]['output'][jvalue].update({'latest_pin_rise':[rise_delay_finals[number_of_latest][0],rise_delay_finals[number_of_latest][3]]})


    return All


def get_latest_node(All):
    latest_delay=float()
    latest_pin=str()
    latest_port=str()

    for ivalue in All:
        if All[ivalue]['stage']==0:
            if All[ivalue]['type']=='pin':
                if All[ivalue]['pin_direction']=='output':

                    from_output=All[ivalue]['from']

                    if ' ' in from_output:
                        from_output=from_output.split(' ')[0]
                        if latest_delay<All[from_output]['output'][All[ivalue]['from'].split(' ')[1]]['fall_Delay']:
                            latest_delay=All[from_output]['output'][All[ivalue]['from'].split(' ')[1]]['fall_Delay']
                            latest_pin=ivalue
                        if latest_delay<All[from_output]['output'][All[ivalue]['from'].split(' ')[1]]['rise_Delay']:
                            latest_delay=All[from_output]['output'][All[ivalue]['from'].split(' ')[1]]['rise_Delay']
                            latest_pin=ivalue

                    else:
                        if latest_delay<All[from_output]['fall_Delay']:
                            latest_delay=All[from_output]['fall_Delay']
                            latest_pin=ivalue
                        if latest_delay<All[from_output]['rise_Delay']:
                            latest_delay=All[from_output]['rise_Delay']
                            latest_pin=ivalue


            elif All[ivalue]['description']=='Pos.edge D-Flip-Flop':
                for kvalue in All[ivalue]['input']:

                    from_output=All[ivalue]['input'][kvalue]['from']
                    if ' ' in from_output:
                        from_output=from_output.split(' ')[0]
                        if latest_delay<All[from_output]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]]['fall_Delay']:
                            latest_delay=All[from_output]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]]['fall_Delay']
                            latest_pin=ivalue
                            latest_port=kvalue
                        if latest_delay<All[from_output]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]]['rise_Delay']:
                            latest_delay=All[from_output]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]]['rise_Delay']
                            latest_pin=ivalue
                            latest_port=kvalue

                    else:
                        if latest_delay<All[from_output]['fall_Delay']:
                            latest_delay=All[from_output]['fall_Delay']
                            latest_pin=ivalue
                            latest_port=kvalue
                        if latest_delay<All[from_output]['rise_Delay']:
                            latest_delay=All[from_output]['rise_Delay']
                            latest_pin=ivalue
                            latest_port=kvalue

    return [latest_pin,latest_port]



def get_new_worst_path(worst_nodes,All):
    list_of_path=list()
    temp_worst=float()
    list_of_path.append([worst_nodes[0]])
    checking=str()

    if All[worst_nodes[0]]['type']=='pin':
        checking=All[worst_nodes[0]]['from']
    else:
        checking=All[worst_nodes[0]]['input'][worst_nodes[1]]['from']

    
    if ' ' not in checking:
        if All[checking]['fall_Delay']>All[checking]['rise_Delay']:
            list_of_path[0].append(All[checking]['fall_Delay'])
        else:
            list_of_path[0].append(All[checking]['rise_Delay'])
        list_of_path.append(checking)
    
    else:
        temp_from=checking.split(' ')[0]
        temp_port=checking.split(' ')[1]
        if All[temp_from]['output'][temp_port]['fall_Delay']>All[temp_from]['output'][temp_port]['rise_Delay']:
            list_of_path[0].extend([All[temp_from]['output'][temp_port]['fall_Delay'],'falling',temp_port])
        else:
            list_of_path[0].extend([All[temp_from]['output'][temp_port]['rise_Delay'],'rising',temp_port])
        list_of_path.append([temp_from])
        idid=int()
        while True:

            temp_input=str()
            unateness=str()

            if list_of_path[-2][2]=='rising':
                temp_input=All[checking.split(' ')[0]]['output'][checking.split(' ')[1]]['latest_pin_rise'][0]
                unateness=All[checking.split(' ')[0]]['output'][checking.split(' ')[1]]['latest_pin_rise'][1]

            else:
                temp_input=All[checking.split(' ')[0]]['output'][checking.split(' ')[1]]['latest_pin_fall'][0]
                unateness=All[checking.split(' ')[0]]['output'][checking.split(' ')[1]]['latest_pin_fall'][1]
            
            input_from=All[checking.split(' ')[0]]['input'][temp_input]['from']
            temp_output=str()

            if ' ' in input_from:
                checking=input_from
                temp_output=input_from.split(' ')[1]
                input_from=input_from.split(' ')[0]
                
                
                if unateness=='negative_unate':
                    if list_of_path[-2][2]=='rising':
                        list_of_path[-1].extend([All[input_from]['output'][temp_output]['fall_Delay'],'falling',temp_output])
                        list_of_path.append([input_from])
                    else:
                        list_of_path[-1].extend([All[input_from]['output'][temp_output]['rise_Delay'],'rising',temp_output])
                        list_of_path.append([input_from])
                else:
                    if list_of_path[-2][2]=='rising':
                        list_of_path[-1].extend([All[input_from]['output'][temp_output]['rise_Delay'],'rising',temp_output])
                        list_of_path.append([input_from])
                    else:
                        list_of_path[-1].extend([All[input_from]['output'][temp_output]['fall_Delay'],'falling',temp_output])
                        list_of_path.append([input_from])

            else:
                if list_of_path[-2][2]=='rising':
                    list_of_path[-1].extend([All[input_from]['rise_Delay'],'rising',str()])
                    list_of_path.append([input_from])
                else:
                    list_of_path[-1].extend([All[input_from]['fall_Delay'],'falling',str()])
                    list_of_path.append([input_from])
            
            if All[input_from]['stage']==0:
                break


    #for ivalue in list_of_path:
    #    print(ivalue)

    list_of_path.reverse()
    temp_input_temp=str()
    templist=list()
    for idx in range(len(list_of_path)):
        if idx==0:
            templist.append([list_of_path[idx+1][1],list_of_path[idx+1][2],list_of_path[idx][0],list_of_path[idx+1][3]])

        elif idx!=len(list_of_path)-1:
            if list_of_path[idx][0]=='rising':
                temp_input_temp=All[list_of_path[idx][0]]['output'][list_of_path[idx+1][3]]['latest_pin_rise'][0]
                templist.append([list_of_path[idx+1][1],list_of_path[idx+1][2],list_of_path[idx][0],list_of_path[idx+1][3],'from :',temp_input_temp])

            else:
                temp_input_temp=All[list_of_path[idx][0]]['output'][list_of_path[idx+1][3]]['latest_pin_fall'][0]
                templist.append([list_of_path[idx+1][1],list_of_path[idx+1][2],list_of_path[idx][0],list_of_path[idx+1][3],'from :',temp_input_temp])

        else:
            templist.append([list_of_path[idx][1],list_of_path[idx][2],list_of_path[idx][0]])

    aaa_temp=list()
    for idx in range(len(templist)):
        ##print(templist[idx])
        temp_list=list()
        if idx==0:
            temp_list.append(templist[idx][0])
        else:
            temp_list.append(templist[idx][0]-templist[idx-1][0])

        temp_list.extend(templist[idx])
        aaa_temp.append(temp_list)

    for idx in range(len(aaa_temp)):
        if '_stage' in aaa_temp[idx][3]:
            aaa_temp[idx][3]=aaa_temp[idx][3].split('_stage')[0]
    print()
    for ivalue in aaa_temp:
        print(ivalue)
    return aaa_temp







if __name__ == "__main__":
    ## sys.argv[lef, def, v, lib]
    ##os.chdir('Documents/PNR/timing/source/')
    file_address_lef='../data/deflef_to_graph_and_verilog/lefs/'
    file_address_lef=file_address_lef+sys.argv[1]

    file_address_def='../data/deflef_to_graph_and_verilog/defs/'
    file_address_def=file_address_def+sys.argv[2]

    file_verilog='../data/deflef_to_graph_and_verilog/hypergraph/'
    file_verilog=file_verilog+sys.argv[3].split('.v')[0]+'_'+sys.argv[4].split('.lib')[0]+'/'
    file_verilog_without_clk=file_verilog+'stage_without_clk(temp).pickle'
    file_verilog_with_clk=file_verilog+'stage_with_clk(temp).pickle'

    file_address_lib='../data/deflef_to_graph_and_verilog/libs/'
    file_address_lib=file_address_lib+sys.argv[4].split('.lib')[0]+'/'
    lib_dict=dict()
    lib_dict_add=file_address_lib+'dictionary_of_lib.json'
    with open(lib_dict_add,'r') as fiel:
        lib_dict=json.load(fiel)
    fiel.close()

    temptemp=sys.argv[1].split('.lef')[0].split('superblue')[1]

    if sys.argv[5]==str(0):
        stage_without_clk=dict()
        with open(file_verilog_without_clk,'rb') as fw:
            stage_without_clk=pickle.load(fw)
        fw.close()

        stage_with_clk=dict()
        with open(file_verilog_with_clk,'rb') as fw:
            stage_with_clk=pickle.load(fw)
        fw.close()


        lef_info=Get_info_lef(file_address_lef)
        std_pin_of_cell_position=lef_info[0]
        lef_unit=lef_info[1]


        def_info=Get_info_def(file_address_def)
        die_Area=def_info[0]
        cell_extpin_position=def_info[1]
        def_unit=def_info[2]


        file_address='../data/macro_info_nangate_typical/'
        wire_load_model=list()   
        with open('../data/OPENSTA/wire_load_model_openSTA.json', 'r') as f:
            wire_load_model=json.load(f)
        f.close()
        temp_capacitance=0.000077161 ########## 1층 layer라고 가정하였다.



        default_wire_load_model=dict()
        for idx in range(len(wire_load_model)):
            if 'default_wire_load' in wire_load_model[idx]['wire_load']:
                default_wire_load_model=wire_load_model[idx]

        wire_wire='nothing'

        wire_cap_without_clk=get_position_with_wire_cap(def_unit,lef_unit,cell_extpin_position,std_pin_of_cell_position,stage_without_clk,default_wire_load_model,wire_wire,temp_capacitance)
        wire_cap_with_clk=get_position_with_wire_cap(def_unit,lef_unit,cell_extpin_position,std_pin_of_cell_position,stage_with_clk,default_wire_load_model,wire_wire,temp_capacitance)
        print(wire_wire)
        print()

        ideal_clk=get_new_Delay_of_nodes_CLK(wire_cap_with_clk,'ideal',lib_dict)
        first_delay=get_new_Delay_of_nodes_stage0(wire_cap_without_clk,ideal_clk,lib_dict)
        all_delay=get_new_all_Delay_Transition_of_nodes(first_delay,lib_dict)



        with open(temptemp+'temp_all_delay_nothing.json','w') as fw:
            json.dump(all_delay,fw,indent=4)
        fw.close()

    elif sys.argv[5]==str(1):
        with open(temptemp+'temp_all_delay_nothing.json','r') as fw:
            all_delay=json.load(fw)
        fw.close()


        latest_component=get_latest_node(all_delay)
        aaa=get_new_worst_path(latest_component,all_delay)
        with open(temptemp+'temp_sta.json','w') as fw:
            json.dump(aaa,fw,indent=4)
        fw.close()