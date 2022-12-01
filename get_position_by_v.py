
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






def get_position_with_wire_cap(def_unit,lef_unit,cell_extpin_position,std_pin_of_cell_position,stage,wlm):
    All=copy.deepcopy(stage)

    proportion=lef_unit/def_unit
    for ivalue in All:
        if All[ivalue]['type']=='pin':
            temp_pos=cell_extpin_position[ivalue]['position']
            temp_pos[0]=float(temp_pos[0])/def_unit
            temp_pos[1]=float(temp_pos[1])/def_unit
            All[ivalue].update({'position':temp_pos})

        else:
            temp_pos=cell_extpin_position[ivalue.split(' ')[0]]['position']
            temp_pin_pos=std_pin_of_cell_position[All[ivalue]['macroID']][ivalue.split(' ')[1]][0]
            xpos=(temp_pin_pos[2]+temp_pin_pos[0])/(2*proportion) ############## 중간점/2 ####### /2를 한 이유는 lef와 def의 scailing을 맞추기 위해서
            ypos=(temp_pin_pos[3]+temp_pin_pos[1])/(2*proportion) ############## 중간점/2 ####### /2를 한 이유는 lef와 def의 scailing을 맞추기 위해서
            temp_port_position=[(xpos+float(temp_pos[0]))/def_unit,(ypos+float(temp_pos[1]))/def_unit]
            All[ivalue].update({'position':temp_port_position})


    for ivalue in All:
        if All[ivalue]['direction']=='OUTPUT':
            position_list=list()
            All[ivalue].update({'wire_length_hpwl':float(0)})
            All[ivalue].update({'wire_length_clique':float(0)})
            All[ivalue].update({'wire_length_star':float(0)})
            position_list.append(All[ivalue]['position'])

            for kvalue in All[ivalue]['to']:
                position_list.append(All[kvalue]['position'])
                
            All[ivalue]['wire_length_hpwl']=get_new_wirelength_hpwl(position_list)
            All[ivalue]['wire_length_clique']=get_new_wirelength_clique(position_list)
            All[ivalue]['wire_length_star']=get_new_wirelength_star(position_list)


    capa_wlm=wlm['capacitance']
    capa_estimate=(0.07*0.077161)
    slope=wlm['slope']
    fanoutdict=dict()
    fanlist=list()
    refanlist=list()

    for idx,ivalue in enumerate(wlm):
        if 'fanout_length' in ivalue:
            fanoutdict[int(ivalue.split("fanout_length")[1])]=wlm[ivalue]

    fanlist=sorted(fanoutdict.keys())        
    refanlist=copy.deepcopy(fanlist)
    refanlist.sort(reverse=True)

    for idx,ivalue in enumerate(All):
        how_many_fanout=int()

        if All[ivalue]['stage'][1]=='OUTPUT':
            All[ivalue].update({'hpwl_model_cap':All[ivalue]['wire_length_hpwl']*capa_estimate})
            All[ivalue].update({'clique_model_cap':All[ivalue]['wire_length_clique']*capa_estimate})
            All[ivalue].update({'star_model_cap':All[ivalue]['wire_length_star']*capa_estimate})
            All[ivalue].update({'wire_length_wire_load':float(0)})
            All[ivalue].update({'wire_load_model_cap':float(0)})

            how_many_fanout=(len(All[ivalue]['to']))
            if how_many_fanout==0:
                All[ivalue]['wire_length_wire_load']=float(0)
                All[ivalue]['wire_load_model_cap']=float(0)
            
            else:
                if how_many_fanout in fanoutdict:
                    All[ivalue]['wire_length_wire_load']=fanoutdict[how_many_fanout]
                    
                elif how_many_fanout>fanlist[-1]:
                    All[ivalue]['wire_length_wire_load']=slope*(how_many_fanout-(fanlist[-1]))+fanoutdict[fanlist[-1]]

                else:

                    min_int=int()
                    max_int=int()
                    portion=float()
                    for kdx in range(len(fanlist)):
                        if fanlist[kdx]<how_many_fanout and fanlist[kdx+1]>how_many_fanout:
                            min_int=fanlist[kdx]
                            break

                    for kdx in range(len(refanlist)):
                        if refanlist[kdx]>how_many_fanout and refanlist[kdx+1]<how_many_fanout:
                            max_int=refanlist[kdx]
                            break

                    All[ivalue]['wire_length_wire_load']=(((how_many_fanout-min_int)/(max_int-min_int))*(fanoutdict[min_int]-fanoutdict[max_int]))+fanoutdict[min_int]
                
                All[ivalue]['wire_load_model_cap']=All[ivalue]['wire_length_wire_load']*capa_wlm
    return All




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


def get_new_Delay_of_nodes_CLK(clk_All_with_wire_cap,CLK_mode):
    All=copy.deepcopy(clk_All_with_wire_cap)
    if CLK_mode=='ideal':
        for idx,ivalue in enumerate(All):
            All[ivalue]['fall_Delay']=0
            All[ivalue]['rise_Delay']=0
            All[ivalue]['fall_Transition']=0
            All[ivalue]['rise_Transition']=0

    else: ############################ 코딩 필요 (clk의 real한 경우)
        for idx,ivalue in enumerate(All):
            if All[ivalue]['stage']==[0,'OUTPUT']:
                break

    return All




def get_new_Delay_of_nodes_stage0(Gall,TALL,wire_mode,lliberty_type): ################ wire_mode: 'hpwl_model'의 경우, 'clique_model'의 경우, 'star_model'의 경우, 'wire_load_model'의 경우가 있다.

    All=copy.deepcopy(Gall)
    TAll=copy.deepcopy(TALL)
    wirecap=wire_mode+'_model_cap'

    for idx,ivalue in enumerate(All):
        if All[ivalue]['stage']==[0,'OUTPUT']:
            if All[ivalue]['type']=='PIN':################ direction이 INPUT 인 external PIN의 초기조건 : no slew, no delay로 본다.
                All[ivalue]['fall_Delay']=0
                All[ivalue]['rise_Delay']=0
                All[ivalue]['fall_Transition']=0
                All[ivalue]['rise_Transition']=0
                All[ivalue]['load_capacitance_rise']=0
                All[ivalue]['load_capacitance_fall']=0

            elif All[ivalue]['type']=='cell':
                if All[ivalue]['cell_type']=='Constant cell': ############################ (constant cell)
                    All[ivalue]['load_capacitance_rise']=float(0)
                    All[ivalue]['load_capacitance_fall']=float(0)

                    All[ivalue]['fall_Delay']=float(0)
                    All[ivalue]['rise_Delay']=float(0)
                    All[ivalue]['fall_Transition']=float(0)
                    All[ivalue]['rise_Transition']=float(0)
                else:
                    checking_path_output=lliberty_type+All[ivalue]['macroID']+'/3_output_'+ivalue.split(' ')[1]
                    if All[ivalue]['cell_type']=='Pos.edge D-Flip-Flop': ############################ (clk to q delay)
                        checking_falling=TAll[ivalue.split(" ")[0]+' ck']['rise_Transition'] ############# 인풋 파라미터1-1 클락의 경우 unateness가 non-unate이다.
                        checking_rising=TAll[ivalue.split(" ")[0]+' ck']['rise_Transition'] ############# 인풋 파라미터1-2

                        load_capa_fall=float()
                        load_capa_rise=float()
                        for kdx in range(len(All[ivalue]['to'])):
                            if All[All[ivalue]['to'][kdx]]['type']=='cell':
                                temp_input=All[ivalue]['to'][kdx]
                                checking_path_input=lliberty_type+All[temp_input]['macroID']+'/2_input_'+temp_input.split(' ')[1]+'.tsv'
                                df1=pd.read_csv(checking_path_input,sep='\t')
                                load_capa_rise=load_capa_rise+float(df1.iloc[1,1])
                                load_capa_fall=load_capa_fall+float(df1.iloc[0,1])
                        load_capa_rise=load_capa_rise+All[ivalue][wirecap] ############### 인풋 파라미터2-1
                        load_capa_fall=load_capa_fall+All[ivalue][wirecap] ############### 인풋 파라미터2-2
                        All[ivalue]['load_capacitance_rise']=load_capa_rise
                        All[ivalue]['load_capacitance_fall']=load_capa_fall

                        df_fall_delay=pd.read_csv(checking_path_output+'/condition_0_cell_fall.tsv',sep='\t')
                        df_rise_delay=pd.read_csv(checking_path_output+'/condition_0_cell_rise.tsv',sep='\t')
                        df_fall_transition=pd.read_csv(checking_path_output+'/condition_0_fall_transition.tsv',sep='\t')
                        df_rise_transition=pd.read_csv(checking_path_output+'/condition_0_rise_transition.tsv',sep='\t')
                        
                        All[ivalue]['fall_Delay']=get_value_from_table(df_fall_delay,checking_rising,All[ivalue]['load_capacitance_fall'])+TAll[ivalue.split(" ")[0]+' ck']['rise_Delay']
                        All[ivalue]['rise_Delay']=get_value_from_table(df_rise_delay,checking_rising,All[ivalue]['load_capacitance_rise'])+TAll[ivalue.split(" ")[0]+' ck']['rise_Delay']
                        All[ivalue]['fall_Transition']=get_value_from_table(df_fall_transition,checking_rising,All[ivalue]['load_capacitance_fall'])
                        All[ivalue]['rise_Transition']=get_value_from_table(df_rise_transition,checking_rising,All[ivalue]['load_capacitance_rise'])

                    else:
                        df_info_macro=pd.read_csv(checking_path_output+'/0_info.tsv',sep='\t')
                        if 'unateness : complex' in list(df_info_macro[ivalue.split(' ')[1]])[2]:
                            All[ivalue]['fall_Delay']=float(0)
                            All[ivalue]['rise_Delay']=float(0)
                            All[ivalue]['fall_Transition']=float(0)
                            All[ivalue]['rise_Transition']=float(0)
                        else:
                            df_fall_delay=checking_path_output+'/condition_0_cell_fall.txt'
                            df_rise_delay=checking_path_output+'/condition_0_cell_rise.txt'
                            df_fall_transition=checking_path_output+'/condition_0_fall_transition.txt'
                            df_rise_transition=checking_path_output+'/condition_0_rise_transition.txt'

                            file=open(df_fall_delay,'r')
                            strings=file.readlines()
                            if '\n' in strings[0]:
                                strings[0]=strings[0].replace('\n','')
                            All[ivalue]['fall_Delay']=float(strings[0])
                            file.close()

                            file=open(df_rise_delay,'r')
                            strings=file.readlines()
                            if '\n' in strings[0]:
                                strings[0]=strings[0].replace('\n','')
                            All[ivalue]['fall_Delay']=float(strings[0])
                            file.close()

                            file=open(df_fall_transition,'r')
                            strings=file.readlines()
                            if '\n' in strings[0]:
                                strings[0]=strings[0].replace('\n','')
                            All[ivalue]['fall_Delay']=float(strings[0])
                            file.close()

                            file=open(df_rise_transition,'r')
                            strings=file.readlines()
                            if '\n' in strings[0]:
                                strings[0]=strings[0].replace('\n','')
                            All[ivalue]['fall_Delay']=float(strings[0])
                            file.close()


    for idx,ivalue in enumerate(All):
        if All[ivalue]['stage']==[0,'INPUT']:
            All[ivalue]['fall_Delay']=All[All[ivalue]['from'][0]]['fall_Delay']
            All[ivalue]['rise_Delay']=All[All[ivalue]['from'][0]]['rise_Delay']
            All[ivalue]['input_transition_fall']=All[All[ivalue]['from'][0]]['fall_Transition']
            All[ivalue]['input_transition_rise']=All[All[ivalue]['from'][0]]['rise_Transition']
            
    return All





def get_value_from_table(df,value_transition,value_capacitance):

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

    if value_capacitance<=float(list(df.columns)[1]):
        stryyy=list(df.columns)[1]
        nextyyy=list(df.columns)[2]
        y1=float(list(df.columns)[1])
        y2=float(list(df.columns)[2])

    if value_capacitance>=float(list(df.columns)[7]):
        stryyy=list(df.columns)[6]
        nextyyy=list(df.columns)[7]
        y1=float(list(df.columns)[6])
        y2=float(list(df.columns)[7])

    if value_capacitance>float(list(df.columns)[1]) and value_capacitance<float(list(df.columns)[7]):
        for idx in range(6):
            if float(list(df.columns)[idx+1])<=value_capacitance and value_capacitance<=float(list(df.columns)[idx+2]):
                stryyy=list(df.columns)[idx+1]
                nextyyy=list(df.columns)[idx+2]
                y1=float(list(df.columns)[idx+1])
                y2=float(list(df.columns)[idx+2])

    if value_transition<=list(df['Unnamed: 0'])[0]:
        indxxx=0
        x1=list(df['Unnamed: 0'])[0]
        x2=list(df['Unnamed: 0'])[1]

    if value_transition>=list(df['Unnamed: 0'])[6]:
        indxxx=5
        x1=list(df['Unnamed: 0'])[5]
        x2=list(df['Unnamed: 0'])[6]

    if value_transition>list(df['Unnamed: 0'])[0] and value_transition<list(df['Unnamed: 0'])[6]:
        for idx in range(6):
            if list(df['Unnamed: 0'])[idx]<=value_transition and value_transition<=list(df['Unnamed: 0'])[idx+1]:
                indxxx=idx
                x1=list(df['Unnamed: 0'])[idx]
                x2=list(df['Unnamed: 0'])[idx+1]

    T11=float(df[stryyy][indxxx])
    T12=float(df[nextyyy][indxxx])
    T21=float(df[stryyy][indxxx+1])
    T22=float(df[nextyyy][indxxx+1])


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




def get_new_all_Delay_Transition_of_nodes(delay_only_first_stage_without_clk_All,wire_mode,lliberty_type):
    All=copy.deepcopy(delay_only_first_stage_without_clk_All)


    wirecap=wire_mode+'_model_cap'
    max_stage_number=int()

    for idx,ivalue in enumerate(All):
        if max_stage_number<All[ivalue]['stage'][0]:
            max_stage_number=All[ivalue]['stage'][0]


    for idx in range(max_stage_number+1):
        if idx==0:
            continue

        for kdx,kvalue in enumerate(All):

            if All[kvalue]['stage'][0]==idx and All[kvalue]['stage'][1]=='OUTPUT':


                fall_delay_candidate=list()
                rise_delay_candidate=list()
                df_condition=pd.read_csv(lliberty_type+All[kvalue]['macroID']+'/3_output_'+kvalue.split(" ")[1]+'/0. info.tsv',sep='\t')

                if len(list(df_condition.iloc[2:,1]))==1:
                    related_pin=list(df_condition.iloc[2:,1])[0].split('related_pin : ')[1].split(" , unateness :")[0]
                    unateness=list(df_condition.iloc[2:,1])[0].split(" , unateness : ")[1].strip()
                    if unateness=='negative_unate':
                        fall_delay_candidate.append([related_pin,[unateness,'No_condition',All[kvalue.split(' ')[0]+' '+related_pin]['rise_Delay']]])
                        rise_delay_candidate.append([related_pin,[unateness,'No_condition',All[kvalue.split(' ')[0]+' '+related_pin]['fall_Delay']]])
                    else:
                        fall_delay_candidate.append([related_pin,[unateness,'No_condition',All[kvalue.split(' ')[0]+' '+related_pin]['fall_Delay']]])
                        rise_delay_candidate.append([related_pin,[unateness,'No_condition',All[kvalue.split(' ')[0]+' '+related_pin]['rise_Delay']]])
                        
                else:

                    related_pin=str()
                    other_pins=list()
                    unateness=str()
                    for tdx in range(len(list(df_condition.iloc[2:,1]))):

                        related_pin=list(df_condition.iloc[2:,1])[tdx].split('related_pin : ')[1].split(" , unateness :")[0]
                        other_pins=list(df_condition.iloc[2:,1])[tdx].split("condition : ")[1].split(", related_pin : ")[0].split(' & ')
                        unateness=list(df_condition.iloc[2:,1])[tdx].split(" , unateness : ")[1].strip()
                        other_pins_delay=list()

                        for jdx in range(len(other_pins)):
                            if '!' in other_pins[jdx]:
                                other_pins_delay.append(All[kvalue.split(' ')[0]+' '+other_pins[jdx].split('!')[1]]['fall_Delay'])
                            else:
                                other_pins_delay.append(All[kvalue.split(' ')[0]+' '+other_pins[jdx]]['rise_Delay'])
                        
                        if unateness=='negative_unate':
                            kk=int()
                            for jdx in range(len(other_pins_delay)):
                                if other_pins_delay[jdx]<All[kvalue.split(' ')[0]+' '+related_pin]['rise_Delay']:
                                    kk=kk+1
                            if kk == len(other_pins_delay):
                                fall_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['rise_Delay']]])
                        
                            qq=int()
                            for jdx in range(len(other_pins_delay)):
                                if other_pins_delay[jdx]<All[kvalue.split(' ')[0]+' '+related_pin]['fall_Delay']:
                                    qq=qq+1
                            if qq == len(other_pins_delay):
                                rise_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['fall_Delay']]])                         

                        if unateness=='positive_unate':
                            kk=int()
                            for jdx in range(len(other_pins_delay)):
                                if other_pins_delay[jdx]<All[kvalue.split(' ')[0]+' '+related_pin]['fall_Delay']:
                                    kk=kk+1
                            if kk == len(other_pins_delay):
                                fall_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['fall_Delay']]])
                        
                            qq=int()
                            for jdx in range(len(other_pins_delay)):
                                if other_pins_delay[jdx]<All[kvalue.split(' ')[0]+' '+related_pin]['rise_Delay']:
                                    qq=qq+1
                            if qq == len(other_pins_delay):
                                rise_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['rise_Delay']]])
                   
                    rr=int()
                    for tdx in range(len(fall_delay_candidate)):
                        rr=rr+1
                    if rr ==0:
                        for tdx in range(len(list(df_condition.iloc[2:,1]))):
                            related_pin=list(df_condition.iloc[2:,1])[tdx].split('related_pin : ')[1].split(" , unateness :")[0]
                            other_pins=list(df_condition.iloc[2:,1])[tdx].split("condition : ")[1].split(", related_pin : ")[0].split(' & ')
                            unateness=list(df_condition.iloc[2:,1])[tdx].split(" , unateness : ")[1].strip()
                            if unateness=='negative_unate':
                                fall_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['rise_Delay']]])
                            else:
                                fall_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['fall_Delay']]])

                    rr=int()
                    for tdx in range(len(rise_delay_candidate)):
                        rr=rr+1
                    if rr ==0:
                        for tdx in range(len(list(df_condition.iloc[2:,1]))):
                            related_pin=list(df_condition.iloc[2:,1])[tdx].split('related_pin : ')[1].split(" , unateness :")[0]
                            other_pins=list(df_condition.iloc[2:,1])[tdx].split("condition : ")[1].split(", related_pin : ")[0].split(' & ')
                            unateness=list(df_condition.iloc[2:,1])[tdx].split(" , unateness : ")[1].strip()
                            if unateness=='negative_unate':
                                rise_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['fall_Delay']]])
                            else:
                                rise_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['rise_Delay']]])

                All[kvalue]['load_capacitance_rise']=float()
                All[kvalue]['load_capacitance_fall']=float()

                for tdx in range(len(All[kvalue]['to'])):
                    if All[All[kvalue]['to'][tdx]]['type'] == 'cell':
                        df4=pd.read_csv(lliberty_type+All[All[kvalue]['to'][tdx]]['macroID']+'/2_input_'+All[kvalue]['to'][tdx].split(' ')[1]+'.tsv',sep='\t')
                        All[kvalue]['load_capacitance_fall']=All[kvalue]['load_capacitance_fall']+float(df4.iloc[0,1])
                        All[kvalue]['load_capacitance_rise']=All[kvalue]['load_capacitance_rise']+float(df4.iloc[1,1])

                All[kvalue]['load_capacitance_rise']=All[kvalue]['load_capacitance_rise']+All[kvalue][wirecap]
                All[kvalue]['load_capacitance_fall']=All[kvalue]['load_capacitance_fall']+All[kvalue][wirecap]


                fall_delay_finals=list()
                for tdx in range(len(fall_delay_candidate)):

                    input_ttrraann=float()
                    unate=str()
                    load_capa=All[kvalue]['load_capacitance_fall']
                    df5_delay=pd.DataFrame()
                    df5_trans=pd.DataFrame()
                    if fall_delay_candidate[tdx][1][1]=='No_condition':
                        path_to_table=lliberty_type+All[kvalue]['macroID']+'/3_output_'+kvalue.split(" ")[1]+'/condition_0_'
                    else:
                        path_to_table=lliberty_type+All[kvalue]['macroID']+'/3_output_'+kvalue.split(" ")[1]+'/condition_'+fall_delay_candidate[tdx][1][1].split(': ')[1]+'_'

                    if fall_delay_candidate[tdx][1][0]=='negative_unate':
                        unate='negative_unate'
                        input_ttrraann=All[kvalue.split(' ')[0]+' '+fall_delay_candidate[tdx][0]]['input_transition_rise']
                        df5_delay=pd.read_csv(path_to_table+'cell_fall.tsv',sep='\t')
                        df5_trans=pd.read_csv(path_to_table+'fall_transition.tsv',sep='\t')

                    elif fall_delay_candidate[tdx][1][0]=='positive_unate':
                        unate='positive_unate'
                        input_ttrraann=All[kvalue.split(' ')[0]+' '+fall_delay_candidate[tdx][0]]['input_transition_fall']
                        df5_delay=pd.read_csv(path_to_table+'cell_fall.tsv',sep='\t')
                        df5_trans=pd.read_csv(path_to_table+'fall_transition.tsv',sep='\t')

                    fall_delay_finals.append([fall_delay_candidate[tdx][0],fall_delay_candidate[tdx][1][2]+get_value_from_table(df5_delay,input_ttrraann,load_capa),get_value_from_table(df5_trans,input_ttrraann,load_capa),unate])
                    


                rise_delay_finals=list()
                for tdx in range(len(rise_delay_candidate)):

                    input_ttrraann=float()
                    unate=str()
                    load_capa=All[kvalue]['load_capacitance_rise']
                    df5_delay=pd.DataFrame()
                    df5_trans=pd.DataFrame()
                    if rise_delay_candidate[tdx][1][1]=='No_condition':
                        path_to_table=lliberty_type+All[kvalue]['macroID']+'/3_output_'+kvalue.split(" ")[1]+'/condition_0_'
                    else:
                        path_to_table=lliberty_type+All[kvalue]['macroID']+'/3_output_'+kvalue.split(" ")[1]+'/condition_'+rise_delay_candidate[tdx][1][1].split(': ')[1]+'_'

                    if rise_delay_candidate[tdx][1][0]=='negative_unate':
                        unate='negative_unate'
                        input_ttrraann=All[kvalue.split(' ')[0]+' '+rise_delay_candidate[tdx][0]]['input_transition_fall']
                        df5_delay=pd.read_csv(path_to_table+'cell_rise.tsv',sep='\t')
                        df5_trans=pd.read_csv(path_to_table+'rise_transition.tsv',sep='\t')

                    elif rise_delay_candidate[tdx][1][0]=='positive_unate':
                        unate='positive_unate'
                        input_ttrraann=All[kvalue.split(' ')[0]+' '+rise_delay_candidate[tdx][0]]['input_transition_rise']
                        df5_delay=pd.read_csv(path_to_table+'cell_rise.tsv',sep='\t')
                        df5_trans=pd.read_csv(path_to_table+'rise_transition.tsv',sep='\t')

                    rise_delay_finals.append([rise_delay_candidate[tdx][0],rise_delay_candidate[tdx][1][2]+get_value_from_table(df5_delay,input_ttrraann,load_capa),get_value_from_table(df5_trans,input_ttrraann,load_capa),unate])

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

                All[kvalue]['fall_Delay']=fall_delay_finals[number_of_latest1][1]
                All[kvalue]['rise_Delay']=rise_delay_finals[number_of_latest][1]
                All[kvalue]['fall_Transition']=fall_delay_finals[number_of_latest1][2]
                All[kvalue]['rise_Transition']=rise_delay_finals[number_of_latest][2]
                All[kvalue]['latest_pin_fall']=[fall_delay_finals[number_of_latest1][0],fall_delay_finals[number_of_latest1][3]]
                All[kvalue]['latest_pin_rise']=[rise_delay_finals[number_of_latest][0],rise_delay_finals[number_of_latest][3]]


        for kdx,kvalue in enumerate(All):
            if All[kvalue]['stage'][0]==idx and All[kvalue]['stage'][1]=='INPUT':
                All[kvalue]['fall_Delay']=All[All[kvalue]['from'][0]]['fall_Delay']
                All[kvalue]['rise_Delay']=All[All[kvalue]['from'][0]]['rise_Delay']
                All[kvalue]['input_transition_fall']=All[All[kvalue]['from'][0]]['fall_Transition']
                All[kvalue]['input_transition_rise']=All[All[kvalue]['from'][0]]['rise_Transition']
    
    return All




def get_last_nodes_list(All):
    list_of_path=list()
    max_stage_number=int()

    for idx,ivalue in enumerate(All):
        if All[ivalue]['stage'][0]>max_stage_number:
            max_stage_number=All[ivalue]['stage'][0]
    
    all_last_nodes=list()

    df=pd.DataFrame({'last_node_name':[],'delay':[]})
    new_df=pd.DataFrame()
    for idx,ivalue in enumerate(All):
        if len(All[ivalue]['to'])==0:
                worst_state=str()
                if All[ivalue]['fall_Delay']>All[ivalue]['rise_Delay']:
                    worst_state='fall_Delay'
                else:
                    worst_state='rise_Delay'
                new_df=pd.DataFrame({'last_node_name':[ivalue],'delay':[All[ivalue][worst_state]]})
                df=df.append(new_df,ignore_index=True)

    df=df.sort_values(by='delay',axis=0,ascending=False)
    all_last_nodes=(list(df['last_node_name']))
    return all_last_nodes



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


########################################################################################################################



'''def get_new_wire_cap(Gall,wlm): ############femto farad
    All=copy.deepcopy(Gall)
    
    for ivalue in All:
        if All[ivalue]['direction']=='OUTPUT':
            position_list=list()
            All[ivalue].update({'wire_length_hpwl':float(0)})
            All[ivalue].update({'wire_length_clique':float(0)})
            All[ivalue].update({'wire_length_star':float(0)})
            position_list.append(All[ivalue]['position'])

            for kvalue in All[ivalue]['to']:
                position_list.append(All[kvalue]['position'])
                
        All[ivalue]['wire_length_hpwl']=get_new_wirelength_hpwl(position_list)
        All[ivalue]['wire_length_clique']=get_new_wirelength_clique(position_list)
        All[ivalue]['wire_length_star']=get_new_wirelength_star(position_list)



    capa_wlm=wlm['capacitance']
    capa_estimate=(0.07*0.077161)
    slope=wlm['slope']
    fanoutdict=dict()
    fanlist=list()
    refanlist=list()

    for idx,ivalue in enumerate(wlm):
        if 'fanout_length' in ivalue:
            fanoutdict[int(ivalue.split("fanout_length")[1])]=wlm[ivalue]

    fanlist=sorted(fanoutdict.keys())        
    refanlist=copy.deepcopy(fanlist)
    refanlist.sort(reverse=True)

    for idx,ivalue in enumerate(All):
        how_many_fanout=int()

        if All[ivalue]['stage'][1]=='OUTPUT':
            All[ivalue].update({'hpwl_model_cap':All[ivalue]['wire_length_hpwl']*capa_estimate})
            All[ivalue].update({'clique_model_cap':All[ivalue]['wire_length_clique']*capa_estimate})
            All[ivalue].update({'star_model_cap':All[ivalue]['wire_length_star']*capa_estimate})
            All[ivalue].update({'wire_length_wire_load':float(0)})
            All[ivalue].update({'wire_load_model_cap':float(0)})

            how_many_fanout=(len(All[ivalue]['to']))
            if how_many_fanout==0:
                All[ivalue]['wire_length_wire_load']=float(0)
                All[ivalue]['wire_load_model_cap']=float(0)
            
            else:
                if how_many_fanout in fanoutdict:
                    All[ivalue]['wire_length_wire_load']=fanoutdict[how_many_fanout]
                    
                elif how_many_fanout>fanlist[-1]:
                    All[ivalue]['wire_length_wire_load']=slope*(how_many_fanout-(fanlist[-1]))+fanoutdict[fanlist[-1]]

                else:

                    min_int=int()
                    max_int=int()
                    portion=float()
                    for kdx in range(len(fanlist)):
                        if fanlist[kdx]<how_many_fanout and fanlist[kdx+1]>how_many_fanout:
                            min_int=fanlist[kdx]
                            break

                    for kdx in range(len(refanlist)):
                        if refanlist[kdx]>how_many_fanout and refanlist[kdx+1]<how_many_fanout:
                            max_int=refanlist[kdx]
                            break

                    All[ivalue]['wire_length_wire_load']=(((how_many_fanout-min_int)/(max_int-min_int))*(fanoutdict[min_int]-fanoutdict[max_int]))+fanoutdict[min_int]
                
                All[ivalue]['wire_load_model_cap']=All[ivalue]['wire_length_wire_load']*capa_wlm
    
    return All'''



def getExtPinInfo_new(fileAddress):
    expin=dict()
    startpIdx=int()
    endpIdx=int()


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
    start = time.time()
    print('start')

    file_address_lef='../data/deflef_to_graph_and_verilog/lefs/'
    file_address_lef=file_address_lef+'superblue16.lef'

    file_address_def='../data/deflef_to_graph_and_verilog/defs/'
    ##file_address_def=file_address_def+'gcd.def'
    file_address_def=file_address_def+'superblue16.def'

    file_verilog='../data/deflef_to_graph_and_verilog/hypergraph/'
    file_verilog=file_verilog+'superblue16_superblue16_Late/'

    file_verilog_without_clk=file_verilog+'stage_without_clk.pickle'
    file_verilog_with_clk=file_verilog+'stage_with_clk.pickle'

    file_address_lib='../data/deflef_to_graph_and_verilog/libs/'
    file_address_lib=file_address_lib+'superblue16_Late/'


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

    stage_with_clk=dict()
    with open(file_verilog_with_clk,'rb') as fw:
        stage_with_clk=pickle.load(fw)

    file_address='../data/macro_info_nangate_typical/'
    wire_load_model=list()   
    with open('../data/OPENSTA/wire_load_model_openSTA.json', 'r') as f:
        wire_load_model=json.load(f)
    f.close()

    default_wire_load_model=dict()
    for idx in range(len(wire_load_model)):
        if 'default_wire_load' in wire_load_model[idx]['wire_load']:
            default_wire_load_model=wire_load_model[idx]

    print('1차(clear)')
    wire_cap_without_clk=get_position_with_wire_cap(def_unit,lef_unit,cell_extpin_position,std_pin_of_cell_position,stage_without_clk,default_wire_load_model)
    wire_cap_with_clk=get_position_with_wire_cap(def_unit,lef_unit,cell_extpin_position,std_pin_of_cell_position,stage_with_clk,default_wire_load_model)

    print('2차(clear)')
    ideal_clk=get_new_Delay_of_nodes_CLK(wire_cap_with_clk,'ideal')
    first_delay=get_new_Delay_of_nodes_stage0(wire_cap_without_clk,ideal_clk,'wire_load',file_address_lib)
    print('3차')
    all_delay=get_new_all_Delay_Transition_of_nodes(first_delay,'wire_load',file_address_lib)
    print('성공?')

    file_pathpath='temp_all_delay.json'
    with open(file_pathpath,'w') as f:
        json.dump(all_delay,f,indent=4)

    total_delay=list()
    total_delay_info=get_last_nodes_list(all_delay)
    for idxxx in range(len(total_delay_info)):
        what_has_worst_delay=total_delay_info[idxxx]
        path_worst=get_new_worst_path(all_delay,what_has_worst_delay)
        total_delay.append(path_worst)
        if idxxx==0:
            print(json.dumps(total_delay[0],indent=4))


    print('확인하기')
    file_pathtt='temp_all_worst_delay.json'
    with open(file_pathtt,'w') as f:
        json.dump(total_delay,f,indent=4)


    print("time :", time.time() - start)
    
    '''arguments=sys.argv
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

    temporary_def_file_name='../data/deflef_to_graph_and_verilog/0. defs/'+name_of_defdef.replace('_revised','')+'/'+temporary_def'''

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ parsing 

    '''macroInfo = getMacroInfo(leflef)
    def_data_unit=get_def_data_unit(defdef)
    area_die=getAreaInfo(defdef)

    netinfo=get_net_summary(defdef,leflef,if_testing)

################################################
    while type(netinfo)==type(''):
        get_temporary1_defdef(netinfo,defdef)
        netinfo=get_net_summary(new_defdef,leflef,if_testing)
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
        json.dump(will_be_graph,fgfille, indent=4)'''
#########################################################################################


 


  
        