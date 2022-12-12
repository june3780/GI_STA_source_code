
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






def get_position_with_wire_cap(def_unit,lef_unit,cell_extpin_position,std_pin_of_cell_position,All,wlm,wire_mode):

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

                    else:
                        temp_position_list=list()
                        temp_ivalue_position=cell_extpin_position[ivalue]['position']
                        temp_output_position=std_pin_of_cell_position[All[ivalue]['macroID']][kvalue][0]
                        temp_position_list.append(get_real_position_on_die(temp_ivalue_position,temp_output_position,lef_unit,def_unit))

                        for jvalue in All[ivalue]['output'][kvalue]['to']:
                            temp_jvalue=jvalue
                            if ' ' in temp_jvalue:
                                temp_jvalue=temp_jvalue.split(' ')[0]
                            
                            if All[temp_jvalue]['type']=='cell':
                                temp_ivalue_position=cell_extpin_position[temp_jvalue]['position']
                                temp_output_position=std_pin_of_cell_position[All[temp_jvalue]['macroID']][jvalue.split(' ')[1]][0]
                                temp_position_list.append(get_real_position_on_die(temp_ivalue_position,temp_output_position,lef_unit,def_unit))
                            
                            else:
                                temp_ivalue_position=cell_extpin_position[temp_jvalue]['position']
                                temp_output_position=[float(0), float(0), float(0), float(0)]
                                temp_position_list.append(get_real_position_on_die(temp_ivalue_position,temp_output_position,lef_unit,def_unit))
                        if wire_mode=='nothing':
                            continue
                        if wire_mode=='hpwl':
                            All[ivalue]['output'][kvalue]['load_cap_fall']=All[ivalue]['output'][kvalue]['load_cap_fall']+get_new_wirelength_hpwl(temp_position_list)
                            All[ivalue]['output'][kvalue]['load_cap_rise']=All[ivalue]['output'][kvalue]['load_cap_rise']+get_new_wirelength_hpwl(temp_position_list)
                        
                        elif wire_mode=='clique':
                            All[ivalue]['output'][kvalue]['load_cap_fall']=All[ivalue]['output'][kvalue]['load_cap_fall']+get_new_wirelength_clique(temp_position_list)
                            All[ivalue]['output'][kvalue]['load_cap_rise']=All[ivalue]['output'][kvalue]['load_cap_rise']+get_new_wirelength_clique(temp_position_list)

                        elif wire_mode=='star':
                            All[ivalue]['output'][kvalue]['load_cap_fall']=All[ivalue]['output'][kvalue]['load_cap_fall']+get_new_wirelength_star(temp_position_list)
                            All[ivalue]['output'][kvalue]['load_cap_rise']=All[ivalue]['output'][kvalue]['load_cap_rise']+get_new_wirelength_star(temp_position_list)
                        
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


def get_new_Delay_of_nodes_CLK(clk_All_with_wire_cap,CLK_mode,liberty_file):
    All=copy.deepcopy(clk_All_with_wire_cap)
    all_stage_delay=dict()
    if CLK_mode=='ideal':
        for idx,ivalue in enumerate(All):
            All[ivalue]['fall_Delay']=0
            All[ivalue]['rise_Delay']=0
            All[ivalue]['fall_Transition']=0
            All[ivalue]['rise_Transition']=0
        return All

    else: ############################ 코딩 필요 (clk의 real한 경우)
        dict_dict=dict()
        first_stage_delay=get_new_Delay_of_nodes_stage0(All,dict_dict,liberty_file)
        all_stage_delay=get_new_all_Delay_Transition_of_nodes(first_stage_delay,liberty_file)

        return all_stage_delay



        

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
        nextyyy=1
        y1=float(table_capa[stryyy])
        y2=float(table_capa[nextyyy])

    elif value_capacitance>=float(table_capa[len(table_capa)-1]):
        stryyy=len(table_capa)-2
        nextyyy=len(table_capa)-1
        y1=float(table_capa[stryyy])
        y2=float(table_capa[nextyyy])

    elif value_capacitance>float(table_capa[0]) and value_capacitance<float(table_capa[len(table_capa)-1]):
        for idx in range(len(table_capa)-1):
            if float(table_capa[idx])<=value_capacitance and value_capacitance<=float(table_capa[idx+1]):
                stryyy=idx
                nextyyy=idx+1
                y1=float(table_capa[stryyy])
                y2=float(table_capa[nextyyy])

    if value_transition<=table_transition[0]:
        indxxx=0
        x1=table_transition[indxxx]
        x2=table_transition[indxxx+1]

    if value_transition>=table_transition[len(table_transition)-1]:
        indxxx=len(table_transition)-2
        x1=table_transition[indxxx]
        x2=table_transition[indxxx+1]

    if value_transition>table_transition[0] and value_transition<table_transition[len(table_transition)-1]:
        for idx in range(len(table_transition)-1):
            if table_transition[idx]<=value_transition and value_transition<=table_transition[idx+1]:
                indxxx=idx
                x1=table_transition[indxxx]
                x2=table_transition[indxxx+1]

    T11=float(data_list_list[stryyy][indxxx])
    T12=float(data_list_list[nextyyy][indxxx])
    T21=float(data_list_list[stryyy][indxxx+1])
    T22=float(data_list_list[nextyyy][indxxx+1])


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
                    if sys.argv[1]==str(1) or sys.argv[1]==str(2):
                        All[ivalue].update({'rise_Transition':float(0)})
                        All[ivalue].update({'fall_Transition':float(0)})
                    elif sys.argv[1]==str(3):
                        All[ivalue].update({'rise_Transition':float(10)})
                        All[ivalue].update({'fall_Transition':float(10)})
                    
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
                            if sys.argv[1]!=str(3):
                                ck_from=TAll[ivalue]['input']['CK']['from']
                            else:
                                ck_from=TAll[ivalue]['input']['ck']['from']
                            checking_falling=float() ############# 인풋 파라미터1-1 클락의 경우 unateness가 non-unate이다.
                            checking_rising=float() ############# 인풋 파라미터1-2
                            checking_rising_delay=float()
                            if ' ' in ck_from:
                                checking_rising=TAll[ck_from.split(' ')[0]]['output'][ck_from.split(' ')[1]]['rise_Transition']
                                checking_rising_delay=TAll[ck_from.split(' ')[0]]['output'][ck_from.split(' ')[1]]['rise_Delay']
                            else:
                                checking_rising=TAll[ck_from]['rise_Transition']
                                checking_rising_delay=   TAll[ck_from]['rise_Delay']                      
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
        temp_temp_dict=dict()


        for kvalue in All:
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
                            All[kvalue]['output'][jvalue].update({'latest_pin_rise':[related_pin,unateness]})



        for kvalue in All:
            if All[kvalue]['stage']==idx:
                if len(All[kvalue]['output'])==0:
                    continue

                for jvalue in All[kvalue]['output']:

                    fall_delay_candidate=list()
                    rise_delay_candidate=list()
                    if len(lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'])==1:

                        only_input=str()
                        for rvalue in All[kvalue]['input']:
                            only_input=rvalue
                        from_input=All[kvalue]['input'][only_input]['from']
                        temp_fall_Delay=float()
                        temp_rise_Delay=float()
                        if ' ' in from_input:
                            from_input=from_input.split(' ')[0]
                        if All[from_input]['type']=='pin':
                            temp_fall_Delay=All[from_input]['fall_Delay']
                            temp_rise_Delay=All[from_input]['rise_Delay']
                        else:
                            temp_fall_Delay=All[from_input]['output'][All[kvalue]['input'][only_input]['from'].split(' ')[1]]['fall_Delay']
                            temp_rise_Delay=All[from_input]['output'][All[kvalue]['input'][only_input]['from'].split(' ')[1]]['rise_Delay']

                        unateness=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][0].split(", unateness : ")[1].strip()
                        if unateness=='negative_unate':
                            fall_delay_candidate.append([only_input,[unateness,'No_condition',temp_rise_Delay]])
                            rise_delay_candidate.append([only_input,[unateness,'No_condition',temp_fall_Delay]])
                        else:
                            fall_delay_candidate.append([only_input,[unateness,'No_condition',temp_fall_Delay]])
                            rise_delay_candidate.append([only_input,[unateness,'No_condition',temp_rise_Delay]])
                            
                    else:
                        other_pins=list()
                        unateness=str()
                        for tdx in range(len(lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'])):
                            temp_input=lib_dict[All[kvalue]['macroID']]['output'][jvalue]['conditionlist'][tdx].split(", related_pin : ")[1].split(', unateness')[0].strip()
                            from_temp_input=All[kvalue]['input'][temp_input]['from']

                            temp_fall_Delay=float()
                            temp_rise_Delay=float()
                            if ' ' in from_temp_input:
                                from_temp_input=from_temp_input.split(' ')[0]
                            if All[from_temp_input]['type']=='pin':
                                temp_fall_Delay=All[from_temp_input]['fall_Delay']
                                temp_rise_Delay=All[from_temp_input]['rise_Delay']
                            else:

                                temp_fall_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['fall_Delay']
                                temp_rise_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['rise_Delay']

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
                                if All[temp_input_other_from]['type']=='pin':
                                    temp_fall_other=All[temp_input_other_from]['fall_Delay']
                                    temp_rise_other=All[temp_input_other_from]['rise_Delay']
                                else:
                                    temp_fall_other=All[temp_input_other_from]['output'][All[kvalue]['input'][no_mark_other_pins[jdx]]['from'].split(' ')[1]]['fall_Delay']
                                    temp_rise_other=All[temp_input_other_from]['output'][All[kvalue]['input'][no_mark_other_pins[jdx]]['from'].split(' ')[1]]['rise_Delay']

                                if '!' in other_pins[jdx]:
                                    other_pins_delay.append(temp_fall_other)
                                else:
                                    other_pins_delay.append(temp_rise_other)
                            
                            if unateness=='negative_unate':
                                kk=int()
                                for jdx in range(len(other_pins_delay)):
                                    if other_pins_delay[jdx]<temp_rise_Delay:
                                        kk=kk+1
                                if kk == len(other_pins_delay):
                                    fall_delay_candidate.append([temp_input,[unateness,'condition_number: '+str(tdx),temp_rise_Delay]])
                            
                                qq=int()
                                for jdx in range(len(other_pins_delay)):
                                    if other_pins_delay[jdx]<temp_fall_Delay:
                                        qq=qq+1
                                if qq == len(other_pins_delay):
                                    rise_delay_candidate.append([temp_input,[unateness,'condition_number: '+str(tdx),temp_fall_Delay]])                         

                            if unateness=='positive_unate':
                                kk=int()
                                for jdx in range(len(other_pins_delay)):
                                    if other_pins_delay[jdx]<temp_fall_Delay:
                                        kk=kk+1
                                if kk == len(other_pins_delay):
                                    fall_delay_candidate.append([temp_input,[unateness,'condition_number: '+str(tdx),temp_fall_Delay]])
                            
                                qq=int()
                                for jdx in range(len(other_pins_delay)):
                                    if other_pins_delay[jdx]<temp_rise_Delay:
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
                                if All[from_temp_input]['type']=='pin':
                                    temp_fall_Delay=All[from_temp_input]['fall_Delay']
                                    temp_rise_Delay=All[from_temp_input]['rise_Delay']
                                else:
                                    temp_fall_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['fall_Delay']
                                    temp_rise_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['rise_Delay']

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
                                if All[from_temp_input]['type']=='pin':
                                    temp_fall_Delay=All[from_temp_input]['fall_Delay']
                                    temp_rise_Delay=All[from_temp_input]['rise_Delay']
                                else:
                                    temp_fall_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['fall_Delay']
                                    temp_rise_Delay=All[from_temp_input]['output'][All[kvalue]['input'][temp_input]['from'].split(' ')[1]]['rise_Delay']

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
                        if ' ' in from_the_input:
                            from_the_input=from_the_input.split(' ')[0]
                            
                        trans_fall_from_input=float()
                        trans_rise_from_input=float()

                        if All[from_the_input]['type']=='pin':
                            trans_fall_from_input=All[from_the_input]['fall_Transition']
                            trans_rise_from_input=All[from_the_input]['rise_Transition']
                        else:
                            trans_fall_from_input=All[from_the_input]['output'][All[kvalue]['input'][who_is_the_input]['from'].split(' ')[1]]['fall_Transition']
                            trans_rise_from_input=All[from_the_input]['output'][All[kvalue]['input'][who_is_the_input]['from'].split(' ')[1]]['rise_Transition']
                        
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

                            df5_delay=path_to_table['fall_delay']
                            df5_trans=path_to_table['fall_transition']
            
                        elif fall_delay_candidate[tdx][1][0]=='positive_unate':
                            unate='positive_unate'
                            input_ttrraann=trans_fall_from_input

                            df5_delay=path_to_table['rise_delay']
                            df5_trans=path_to_table['rise_transition']

                        fall_delay_finals.append([fall_delay_candidate[tdx][0],fall_delay_candidate[tdx][1][2]+get_new_value_from_table(df5_delay,input_ttrraann,load_capa),get_new_value_from_table(df5_trans,input_ttrraann,load_capa),unate])
                        


                    rise_delay_finals=list()
                    for tdx in range(len(rise_delay_candidate)):
                        who_is_the_input=rise_delay_candidate[tdx][0]
                        from_the_input=All[kvalue]['input'][who_is_the_input]['from']
                        if ' ' in from_the_input:
                            from_the_input=from_the_input.split(' ')[0]

                        trans_fall_from_input=float()
                        trans_rise_from_input=float()

                        if All[from_the_input]['type']=='pin':
                            trans_fall_from_input=All[from_the_input]['fall_Transition']
                            trans_rise_from_input=All[from_the_input]['rise_Transition']
                        else:
                            trans_fall_from_input=All[from_the_input]['output'][All[kvalue]['input'][who_is_the_input]['from'].split(' ')[1]]['fall_Transition']
                            trans_rise_from_input=All[from_the_input]['output'][All[kvalue]['input'][who_is_the_input]['from'].split(' ')[1]]['rise_Transition']

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
                            df5_delay=path_to_table['rise_delay']
                            df5_trans=path_to_table['rise_transition']

                        elif rise_delay_candidate[tdx][1][0]=='positive_unate':
                            unate='positive_unate'
                            input_ttrraann=trans_rise_from_input
                            df5_delay=path_to_table['fall_delay']
                            df5_trans=path_to_table['fall_transition']

                        rise_delay_finals.append([rise_delay_candidate[tdx][0],rise_delay_candidate[tdx][1][2]+get_new_value_from_table(df5_delay,input_ttrraann,load_capa),get_new_value_from_table(df5_trans,input_ttrraann,load_capa),unate])

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
                    All[kvalue]['output'][jvalue].update({'fall_Transition':fall_delay_finals[number_of_latest1][2]})
                    All[kvalue]['output'][jvalue].update({'rise_Transition':rise_delay_finals[number_of_latest][2]})
                    All[kvalue]['output'][jvalue].update({'latest_pin_fall':[fall_delay_finals[number_of_latest1][0],fall_delay_finals[number_of_latest1][3]]})
                    All[kvalue]['output'][jvalue].update({'latest_pin_rise':[rise_delay_finals[number_of_latest][0],rise_delay_finals[number_of_latest][3]]})

                    temp_temp_dict.update({kvalue:{'fall_Delay':fall_delay_finals[number_of_latest1][1],'rise_Delay':rise_delay_finals[number_of_latest][1]}})
                    temp_temp_dict[kvalue].update({'fall_Transition':fall_delay_finals[number_of_latest1][2],'rise_Transition':rise_delay_finals[number_of_latest][2]})
                    temp_temp_dict[kvalue].update({'latest_pin_fall':[fall_delay_finals[number_of_latest1][0],fall_delay_finals[number_of_latest1][3]],'latest_pin_rise':[rise_delay_finals[number_of_latest][0],rise_delay_finals[number_of_latest][3]]})

    return All


def get_latest_node(All):
    latest_delay=float()
    latest_pin=str()
    for ivalue in All:
        if All[ivalue]['stage']==0:
            if All[ivalue]['type']=='pin':
                if All[ivalue]['pin_direction']=='output':

                    from_output=All[ivalue]['from']
                    if ' ' in from_output:
                        from_output=from_output.split(' ')[0]
                    if All[from_output]['type']=='pin':
                        if latest_delay<All[from_output]['fall_Delay']:
                            latest_delay=All[from_output]['fall_Delay']
                            latest_pin=ivalue
                        if latest_delay<All[from_output]['rise_Delay']:
                            latest_delay=All[from_output]['rise_Delay']
                            latest_pin=ivalue
                    else:
                        if latest_delay<All[from_output]['output'][All[ivalue]['from'].split(' ')[1]]['fall_Delay']:
                            latest_delay=All[from_output]['output'][All[ivalue]['from'].split(' ')[1]]['fall_Delay']
                            latest_pin=ivalue
                        if latest_delay<All[from_output]['output'][All[ivalue]['from'].split(' ')[1]]['rise_Delay']:
                            latest_delay=All[from_output]['output'][All[ivalue]['from'].split(' ')[1]]['rise_Delay']
                            latest_pin=ivalue

            elif All[ivalue]['description']=='Pos.edge D-Flip-Flop':
                for kvalue in All[ivalue]['input']:

                    from_output=All[ivalue]['input'][kvalue]['from']
                    if ' ' in from_output:
                        from_output=from_output.split(' ')[0]
                    if All[from_output]['type']=='pin':
                        if latest_delay<All[from_output]['fall_Delay']:
                            latest_delay=All[from_output]['fall_Delay']
                            latest_pin=ivalue
                        if latest_delay<All[from_output]['rise_Delay']:
                            latest_delay=All[from_output]['rise_Delay']
                            latest_pin=ivalue
                    else:
                        if latest_delay<All[from_output]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]]['fall_Delay']:
                            latest_delay=All[from_output]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]]['fall_Delay']
                            latest_pin=ivalue  
                        if latest_delay<All[from_output]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]]['rise_Delay']:
                            latest_delay=All[from_output]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]]['rise_Delay']
                            latest_pin=ivalue

    print(latest_delay)
    print(latest_pin)
    return 0



def get_new_worst_path(All,worst_nodes):
    list_of_path=list()
    checking=worst_nodes


    worst_state=str()
    if All[worst_nodes]['fall_Delay']>All[worst_nodes]['rise_Delay']:
        worst_state='falling'
    else:
        worst_state='rising'

    idx=int()
    while True:
        if All[checking]['stage'][1]=='INPUT':

            list_of_path.append([checking,worst_state])
            checking=All[checking]['from'][0]
        else:
            if worst_state=='falling':

                list_of_path.append([checking,worst_state])

                if len(All[checking]['from'])==0:
                    break

                if All[checking]['latest_pin_fall'][1]=='positive_unate':
                    worst_state='falling'
                else:
                    worst_state='rising'

                checking=checking.split(" ")[0]+' '+All[checking]['latest_pin_fall'][0]

            else:

                list_of_path.append([checking,worst_state])

                if len(All[checking]['from'])==0:
                    break

                if All[checking]['latest_pin_rise'][1]=='positive_unate':
                    worst_state='rising'
                else:
                    worst_state='falling'
                
                checking=checking.split(" ")[0]+' '+All[checking]['latest_pin_rise'][0]


    reverse_list_of_path=list(reversed(list_of_path))
    for idx in range(len(reverse_list_of_path)):
            if All[reverse_list_of_path[idx][0]]['stage'][1]=='OUTPUT':
                if reverse_list_of_path[idx][1]=='falling':
                    reverse_list_of_path[idx].append(All[reverse_list_of_path[idx][0]]['fall_Delay'])
                if reverse_list_of_path[idx][1]=='rising':
                    reverse_list_of_path[idx].append(All[reverse_list_of_path[idx][0]]['rise_Delay'])

    return reverse_list_of_path








if __name__ == "__main__":
    ##os.chdir('Documents/PNR/timing/source/')
    file_address_lef='../data/deflef_to_graph_and_verilog/lefs/'
    if sys.argv[1]==str(1) or sys.argv[1]==str(2):
        file_address_lef=file_address_lef+'NangateOpenCellLibrary.mod.lef'
    elif sys.argv[1]==str(3):
        file_address_lef=file_address_lef+'superblue16.lef'

    file_address_def='../data/deflef_to_graph_and_verilog/defs/'
    if sys.argv[1]==str(1):
        file_address_def=file_address_def+'gcd.def'  
    elif sys.argv[1]==str(2):
        file_address_def=file_address_def+'scratch_detailed.def'
    elif sys.argv[1]==str(3):
        file_address_def=file_address_def+'superblue16.def'

    file_verilog='../data/deflef_to_graph_and_verilog/hypergraph/'

    if sys.argv[1]==str(1):
        file_verilog=file_verilog+'gcd_OPENSTA_example1_slow/'
    elif sys.argv[1]==str(2):
            file_verilog=file_verilog+'scratch_detailed_temp_OPENSTA_example1_slow/'
    elif sys.argv[1]==str(3):
        file_verilog=file_verilog+'superblue16_superblue16_Late/'


    file_verilog_without_clk=file_verilog+'stage_without_clk(temp).pickle'
    file_verilog_with_clk=file_verilog+'stage_with_clk(temp).pickle'

    file_address_lib='../data/deflef_to_graph_and_verilog/libs/'
    if sys.argv[1]==str(1) or sys.argv[1]==str(2):
        file_address_lib=file_address_lib+'OPENSTA_example1_slow/'
    elif sys.argv[1]==str(3):
        file_address_lib=file_address_lib+'superblue16_Late/'

    lib_dict=dict()
    lib_dict_add=file_address_lib+'dictionary_of_lib.json'
    with open(lib_dict_add,'r') as fiel:
        lib_dict=json.load(fiel)
    fiel.close()

    lef_info=Get_info_lef(file_address_lef)
    std_pin_of_cell_position=lef_info[0]
    lef_unit=lef_info[1]

    def_info=Get_info_def(file_address_def)
    die_Area=def_info[0]
    cell_extpin_position=def_info[1]
    def_unit=def_info[2]

    
    stage_without_clk=dict()
    with open(file_verilog_without_clk,'rb') as fw:
        stage_without_clk=pickle.load(fw)
    fw.close()

    stage_with_clk=dict()
    with open(file_verilog_with_clk,'rb') as fw:
        stage_with_clk=pickle.load(fw)
    fw.close()

    file_address='../data/macro_info_nangate_typical/'
    wire_load_model=list()   
    with open('../data/OPENSTA/wire_load_model_openSTA.json', 'r') as f:
        wire_load_model=json.load(f)
    f.close()

    default_wire_load_model=dict()
    for idx in range(len(wire_load_model)):
        if 'default_wire_load' in wire_load_model[idx]['wire_load']:
            default_wire_load_model=wire_load_model[idx]

    wire_cap_without_clk=get_position_with_wire_cap(def_unit,lef_unit,cell_extpin_position,std_pin_of_cell_position,stage_without_clk,default_wire_load_model,'nothing')
    wire_cap_with_clk=get_position_with_wire_cap(def_unit,lef_unit,cell_extpin_position,std_pin_of_cell_position,stage_with_clk,default_wire_load_model,'nothing')


    ideal_clk=get_new_Delay_of_nodes_CLK(wire_cap_with_clk,'real',lib_dict)
    first_delay=get_new_Delay_of_nodes_stage0(wire_cap_without_clk,ideal_clk,lib_dict)
    all_delay=get_new_all_Delay_Transition_of_nodes(first_delay,lib_dict)
    get_latest_node(all_delay)

    '''file_pathpath='temp_all_delay_method1_sdc.json'
    with open(file_pathpath,'w') as f:
        json.dump(all_delay,f,indent=4)
    print('saving')






    file_pathpath='temp_all_delay_method1_sdc.json'
    with open(file_pathpath,'r') as f:
        all_delay=json.load(f)
    f.close()
    get_latest_node(all_delay)'''




        