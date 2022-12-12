


import json

from typing import Type
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import json
import copy
import scipy
import pickle
from networkx.algorithms import tournament
import pandas as pd
import time
import os
import time
import sys








def get_initial_condition(initial_condition_list,a,b,c,d):
    print(a,b,c,d)
    new_initial_condition_list=dict()
    new_initial_condition_list['CLK_mode']=initial_condition_list['CLK_mode'][a]
    new_initial_condition_list['wire_mode']=initial_condition_list['wire_mode'][b]
    new_initial_condition_list['liberty_type']=initial_condition_list['liberty_type'][c]
    new_initial_condition_list['file_name']=initial_condition_list['file_name'][d]        

    return new_initial_condition_list    










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

    if_less_than1=int()
    if_less_than2=int()
    if_over_than1=int()
    if_over_than2=int()

    if value_capacitance<=float(list(df.columns)[1]):
        stryyy=list(df.columns)[1]
        nextyyy=list(df.columns)[2]
        y1=float(list(df.columns)[1])
        y2=float(list(df.columns)[2])
        if_less_than1=1

    if value_capacitance>=float(list(df.columns)[7]):
        stryyy=list(df.columns)[6]
        nextyyy=list(df.columns)[7]
        y1=float(list(df.columns)[6])
        y2=float(list(df.columns)[7])
        if_over_than1=1

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
        if_less_than2=1

    if value_transition>=list(df['Unnamed: 0'])[6]:
        indxxx=5
        x1=list(df['Unnamed: 0'])[5]
        x2=list(df['Unnamed: 0'])[6]
        if_over_than2=1

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










def get_type_of_new_graph(netinfo,file_address):
    seperated_netinfo=copy.deepcopy(netinfo)
    
    for idx,ivalue in enumerate(seperated_netinfo):
        if 'macroID' in seperated_netinfo[ivalue]:
            seperated_netinfo[ivalue]['cell_type']=str()
            path_of_macro=file_address+seperated_netinfo[ivalue]['macroID']+'/1. macro_info.tsv'
            df=pd.read_csv(path_of_macro,sep='\t')

            for kdx in range(df.shape[0]):
                if 'macro_type' in df.values[kdx]:
                    seperated_netinfo[ivalue]['cell_type']=str(df.values[kdx]).split(" '")[1].split("']")[0]            

    return seperated_netinfo










def get_delnode_new_list(TALL):
    All=copy.deepcopy(TALL)
    shoulddelnode1=list()
    shoulddelnode2=list()

    for idx,ivalue in enumerate(All):
        if 'macroID' in (All[ivalue]):
            if All[ivalue]['cell_type']=='Sequential':
                if All[ivalue]['direction']=='INPUT':
                    shoulddelnode1.append(ivalue)
                elif All[ivalue]['direction']=='OUTPUT':
                    shoulddelnode2.append(ivalue)
            

    for idx,ivalue in enumerate(All):
        if ivalue in shoulddelnode1:
            All[ivalue]['to']=[]
        elif ivalue in shoulddelnode2:
            All[ivalue]['from']=[]

    return All










def get_CLK2CK_new_graph(TAll):
    All=copy.deepcopy(TAll)
    sync_nodes_to_clock_list=list()
    checking=str()
    only_clk_All=dict()

    for idx,ivalue in enumerate(All):
        if 'macroID' in (All[ivalue]) and All[ivalue]['direction']=='INPUT':
            if All[ivalue]['cell_type']=='Sequential':
                checking=ivalue

                while True:
                    if_pin_is_clk=list()
                    if All[checking]['from'][0]=='PIN clk':

                        sync_nodes_to_clock_list.append(ivalue)

                        for kdx in range(len(if_pin_is_clk)):
                            sync_nodes_to_clock_list.append(if_pin_is_clk[kdx])

                        break

                    elif len(All[checking]['from'])==1:
                        temp1=All[checking]['from'][0]
                        if_pin_is_clk.append(temp1)

                        if len(All[temp1]['from'])==1:
                            checking=All[temp1]['from'][0]
                            if_pin_is_clk.append(checking)

                        else:
                            break

                        continue

                    else:
                        break
    
    sync_nodes_to_clock_list.append('PIN clk')

    for idx,ivalue in enumerate(All):
        if ivalue in sync_nodes_to_clock_list:
            only_clk_All.update({ivalue:All[ivalue]})

    return only_clk_All










def get_new_del_related_with_CLK(cutting_All,CLK2reg):
    All=copy.deepcopy(cutting_All)
    node_related_with_clk=list()

    for idx,ivalue in enumerate(CLK2reg):
        node_related_with_clk.append(ivalue)

    for idx,ivalue in enumerate(cutting_All):
        if ivalue in node_related_with_clk:
            del All[ivalue]

    return All










def new_del_unconnected_nodes(TAll):
    All=copy.deepcopy(TAll)
    dellist=list()

    for idx, ivalue in enumerate(All):
        if len(All[ivalue]['to'])==0 and len(All[ivalue]['from'])==0:
            dellist.append(ivalue)

    for idx in range(len(dellist)):
            del All[dellist[idx]]

    return All








def get_new_stage_nodes_for_clk_nodes(TAll,netinfo_for_clk):

    All=copy.deepcopy(TAll)

    for idx, ivalue in enumerate(All):
        All[ivalue]['stage']=[None,None]
        if len(All[ivalue]['from'])==0:
            All[ivalue]['stage']=[0,'OUTPUT']
    

    for idx,ivalue in enumerate(All):
        if All[ivalue]['stage']==[0,'OUTPUT']:
            for kdx in range(len(All[ivalue]['to'])):
                All[All[ivalue]['to'][kdx]]['stage']=[0,'INPUT']

    tt=int()
    for idx,ivalue in enumerate(All):
        if 'stage' in All[ivalue]:
            tt=tt+1

    if idx+1==tt:
        print('Clock Tree Synthesis is needed')

    else:
        current_stage=1
        while True:
            rrr=int()
            willget_stage_input=list()

            for idx,ivalue in enumerate(All):
                if All[ivalue]['stage']==[None,None]:
                    rrr=rrr+1


                if (All[ivalue]['direction']=='OUTPUT' and All[ivalue]['type']=='cell' and All[ivalue]['stage']==[None,None]):

                    check_number_of_stage=int()
                    max_stage=int()
                    for kdx in range(len(All[ivalue]['from'])):
                        if All[All[ivalue]['from'][kdx]]['stage']==[None, None]:
                            break
                        else:
                            check_number_of_stage=check_number_of_stage+1

                    if check_number_of_stage==len(All[ivalue]['from']):
                        All[ivalue]['stage']=[current_stage,'OUTPUT']

                        for kdx in range(len(All[ivalue]['to'])):
                            willget_stage_input.append(All[ivalue]['to'][kdx])
            
            for idx in range(len(willget_stage_input)):
                    All[willget_stage_input[idx]]['stage']=[current_stage,'INPUT']

            if rrr==0:
                break

            else:
                current_stage=current_stage+1
                continue
    

    for idx, ivalue in enumerate(All):
        for kdx,kvalue in enumerate(netinfo_for_clk):
            for jdx in range(len(netinfo_for_clk[kvalue])):
                if 'cell_name' in netinfo_for_clk[kvalue][jdx]:
                    if ivalue==netinfo_for_clk[kvalue][jdx]['cell_name']+' '+netinfo_for_clk[kvalue][jdx]['used_port']:
                        All[ivalue]['position']=[netinfo_for_clk[kvalue][jdx]['port_pos'][0],netinfo_for_clk[kvalue][jdx]['port_pos'][1]]

                elif 'net_name' in netinfo_for_clk[kvalue][jdx]:
                    if ivalue=='PIN '+netinfo_for_clk[kvalue][jdx]['net_name']:
                        All[ivalue]['position']=[netinfo_for_clk[kvalue][jdx]['pin_pos'][0],netinfo_for_clk[kvalue][jdx]['pin_pos'][1]]

    return All










def get_new_stage_nodes(TAll):
    All=copy.deepcopy(TAll)

    for idx, ivalue in enumerate(All):
        All[ivalue]['stage']=[None,None]
        if len(All[ivalue]['from'])==0:
            All[ivalue]['stage']=[0,'OUTPUT']
    

    for idx,ivalue in enumerate(All):
        if All[ivalue]['stage']==[0,'OUTPUT']:
            for kdx in range(len(All[ivalue]['to'])):
                All[All[ivalue]['to'][kdx]]['stage']=[0,'INPUT']
    

    current_stage=1
    while True:
        rrr=int()
        willget_stage_input=list()

        for idx,ivalue in enumerate(All):
            if All[ivalue]['stage']==[None,None]:
                rrr=rrr+1


            if (All[ivalue]['direction']=='OUTPUT' and All[ivalue]['type']=='cell' and All[ivalue]['stage']==[None,None]):

                check_number_of_stage=int()
                max_stage=int()
                for kdx in range(len(All[ivalue]['from'])):
                    if All[All[ivalue]['from'][kdx]]['stage']==[None, None]:
                        break
                    else:
                        check_number_of_stage=check_number_of_stage+1

                if check_number_of_stage==len(All[ivalue]['from']):
                    All[ivalue]['stage']=[current_stage,'OUTPUT']

                    for kdx in range(len(All[ivalue]['to'])):
                        willget_stage_input.append(All[ivalue]['to'][kdx])
        
        for idx in range(len(willget_stage_input)):
                All[willget_stage_input[idx]]['stage']=[current_stage,'INPUT']

        if rrr==0:
            break

        else:
            current_stage=current_stage+1
            continue

    return All










def get_new_wire_cap(Gall,wlm): ############femto farad
    All=copy.deepcopy(Gall)

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

            All[ivalue]['hpwl_model_cap']=All[ivalue]['wire_length_hpwl']*capa_estimate
            All[ivalue]['clique_model_cap']=All[ivalue]['wire_length_clique']*capa_estimate
            All[ivalue]['star_model_cap']=All[ivalue]['wire_length_star']*capa_estimate
            All[ivalue]['wire_length_wire_load']=float()
            All[ivalue]['wire_load_model_cap']=float()

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
    liberty_type=lliberty_type.split('.lib')[0]
    All=copy.deepcopy(Gall)
    TAll=copy.deepcopy(TALL)
    wirecap=wire_mode+'_model_cap'
    '''will_del_wire_models=['hpwl_model_cap','clique_model_cap','star_model_cap','wire_load_model_cap',\
        'wire_length_hpwl','wire_length_star','wire_length_clique','wire_length_wire_load'] ############################################################################################################################################## 지워야함
    will_del_wire_models.remove(wire_mode+'_model_cap') ############################################################################################################################################## 지워야함
    will_del_wire_models.remove('wire_length_'+wire_mode) ############################################################################################################################################## 지워야함
     ############################################################################################################################################## 지워야함

    for idx in range(len(will_del_wire_models)): ############################################################################################################################################## 지워야함
        for kdx, kvalue in enumerate(All): ############################################################################################################################################## 지워야함
            if will_del_wire_models[idx] in All[kvalue]: ############################################################################################################################################## 지워야함
                del All[kvalue][will_del_wire_models[idx]] ############################################################################################################################################## 지워야함


    for idx,ivalue in enumerate(All): 
        if ('wire_length_'+wire_mode) in All[ivalue]: ############################################################################################################################################## 지워야함
            del All[ivalue]['wire_length_'+wire_mode]''' ############################################################################################################################################## 지워야함

    for idx,ivalue in enumerate(All):

        if All[ivalue]['stage']==[0,'OUTPUT'] and All[ivalue]['type']=='PIN':################ direction이 INPUT 인 external PIN의 초기조건 : no slew, no delay로 본다.
            All[ivalue]['fall_Delay']=0
            All[ivalue]['rise_Delay']=0
            All[ivalue]['fall_Transition']=0
            All[ivalue]['rise_Transition']=0
            All[ivalue]['load_capacitance_rise']=0
            All[ivalue]['load_capacitance_fall']=0

        if All[ivalue]['stage']==[0,'OUTPUT'] and All[ivalue]['type']=='cell' and 'LOGIC' not in All[ivalue]['macroID']: ############################ (clk to q delay)
            checking_path_output='../data/deflef_to_graph_and_verilog/libs/OPENSTA_'+liberty_type+'/'+All[ivalue]['macroID']+'/3_output_'+ivalue.split(' ')[1]
            checking_falling=TAll[ivalue.split(" ")[0]+' CK']['rise_Transition'] ############# 인풋 파라미터1-1 클락의 경우 unateness가 non-unate이다.
            checking_rising=TAll[ivalue.split(" ")[0]+' CK']['rise_Transition'] ############# 인풋 파라미터1-2

            load_capa_fall=float()
            load_capa_rise=float()
            for kdx in range(len(All[ivalue]['to'])):
                if All[All[ivalue]['to'][kdx]]['type']=='cell':
                    checking_path_input='../data/deflef_to_graph_and_verilog/libs/OPENSTA_'+liberty_type+'/'+All[All[ivalue]['to'][kdx]]['macroID']+'/2_input_'+All[ivalue]['to'][kdx].split(" ")[1]+'.tsv'
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
            
            All[ivalue]['fall_Delay']=get_value_from_table(df_fall_delay,checking_rising,All[ivalue]['load_capacitance_fall'])+TAll[ivalue.split(" ")[0]+' CK']['rise_Delay']
            All[ivalue]['rise_Delay']=get_value_from_table(df_rise_delay,checking_rising,All[ivalue]['load_capacitance_rise'])+TAll[ivalue.split(" ")[0]+' CK']['rise_Delay']
            All[ivalue]['fall_Transition']=get_value_from_table(df_fall_transition,checking_rising,All[ivalue]['load_capacitance_fall'])
            All[ivalue]['rise_Transition']=get_value_from_table(df_rise_transition,checking_rising,All[ivalue]['load_capacitance_rise'])


        elif All[ivalue]['stage']==[0,'OUTPUT'] and All[ivalue]['type']=='cell' and 'LOGIC' in All[ivalue]['macroID']:
            All[ivalue]['load_capacitance_rise']=float(0)
            All[ivalue]['load_capacitance_fall']=float(0)

            All[ivalue]['fall_Delay']=float(0)
            All[ivalue]['rise_Delay']=float(0)
            All[ivalue]['fall_Transition']=float(0)
            All[ivalue]['rise_Transition']=float(0)

    for idx,ivalue in enumerate(All):
        if All[ivalue]['stage']==[0,'INPUT']:
            All[ivalue]['fall_Delay']=All[All[ivalue]['from'][0]]['fall_Delay']
            All[ivalue]['rise_Delay']=All[All[ivalue]['from'][0]]['rise_Delay']
            All[ivalue]['input_transition_fall']=All[All[ivalue]['from'][0]]['fall_Transition']
            All[ivalue]['input_transition_rise']=All[All[ivalue]['from'][0]]['rise_Transition']
            
    return All










def get_new_all_Delay_Transition_of_nodes(delay_only_first_stage_without_clk_All,wire_mode,lliberty_type):
    All=copy.deepcopy(delay_only_first_stage_without_clk_All)
    liberty_type=lliberty_type.split('.lib')[0]
    condition_table='../data/deflef_to_graph_and_verilog/libs/OPENSTA_'+liberty_type+'/'

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
                df_condition=pd.read_csv(condition_table+All[kvalue]['macroID']+'/3_output_'+kvalue.split(" ")[1]+'/0_info.tsv',sep='\t')

                if len(list(df_condition.iloc[2:,1]))==1:
                    related_pin=list(df_condition.iloc[2:,1])[0].split('related_pin : ')[1].split(", unateness :")[0]
                    unateness=list(df_condition.iloc[2:,1])[0].split(", unateness : ")[1].strip()
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

                        related_pin=list(df_condition.iloc[2:,1])[tdx].split('related_pin : ')[1].split(", unateness :")[0]
                        other_pins=list(df_condition.iloc[2:,1])[tdx].split("condition : ")[1].split(", related_pin : ")[0].split(' & ')
                        unateness=list(df_condition.iloc[2:,1])[tdx].split(", unateness : ")[1].strip()
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
                            related_pin=list(df_condition.iloc[2:,1])[tdx].split('related_pin : ')[1].split(", unateness :")[0]
                            other_pins=list(df_condition.iloc[2:,1])[tdx].split("condition : ")[1].split(", related_pin : ")[0].split(' & ')
                            unateness=list(df_condition.iloc[2:,1])[tdx].split(", unateness : ")[1].strip()
                            if unateness=='negative_unate':
                                fall_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['rise_Delay']]])
                            else:
                                fall_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['fall_Delay']]])

                    rr=int()
                    for tdx in range(len(rise_delay_candidate)):
                        rr=rr+1
                    if rr ==0:
                        for tdx in range(len(list(df_condition.iloc[2:,1]))):
                            related_pin=list(df_condition.iloc[2:,1])[tdx].split('related_pin : ')[1].split(", unateness :")[0]
                            other_pins=list(df_condition.iloc[2:,1])[tdx].split("condition : ")[1].split(", related_pin : ")[0].split(' & ')
                            unateness=list(df_condition.iloc[2:,1])[tdx].split(", unateness : ")[1].strip()
                            if unateness=='negative_unate':
                                rise_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['fall_Delay']]])
                            else:
                                rise_delay_candidate.append([related_pin,[unateness,'condition_number: '+str(tdx),All[kvalue.split(' ')[0]+' '+related_pin]['rise_Delay']]])

                All[kvalue]['load_capacitance_rise']=float()
                All[kvalue]['load_capacitance_fall']=float()

                for tdx in range(len(All[kvalue]['to'])):
                    if All[All[kvalue]['to'][tdx]]['type'] == 'cell':
                        df4=pd.read_csv(condition_table+All[All[kvalue]['to'][tdx]]['macroID']+'/'+'2_input_'+All[kvalue]['to'][tdx].split(' ')[1]+'.tsv',sep='\t')
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
                        path_to_table=condition_table+All[kvalue]['macroID']+'/3_output_'+kvalue.split(" ")[1]+'/condition_0_'
                    else:
                        path_to_table=condition_table+All[kvalue]['macroID']+'/3_output_'+kvalue.split(" ")[1]+'/condition_'+fall_delay_candidate[tdx][1][1].split(': ')[1]+'_'

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
                        path_to_table=condition_table+All[kvalue]['macroID']+'/3_output_'+kvalue.split(" ")[1]+'/condition_0_'
                    else:
                        path_to_table=condition_table+All[kvalue]['macroID']+'/3_output_'+kvalue.split(" ")[1]+'/condition_'+rise_delay_candidate[tdx][1][1].split(': ')[1]+'_'

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







def get_start_points(All,strstr):
    list_points=list()
    max_stage_number=int()



    for idx,ivalue in enumerate(All):
        if All[ivalue]['stage'][0]>max_stage_number:
            max_stage_number=All[ivalue]['stage'][0]
    
    if len(All[strstr]['to'])!=0:
        print('the pin is not Sequential input pin')
        return 0
   
    else:
        get_list(All,strstr,list_points)


        return list(set(list_points))




def get_list(All,strstr,listlist):

    checking=All[strstr]['from'][0]
    if len(All[checking]['from'])==0:
        listlist.append(checking)
    else:
        for idx in range(len(All[checking]['from'])):
            get_list(All,All[checking]['from'][idx],listlist)
    return listlist







def get_clk_partitioning(clk_All,die_area,def_unit):


    All=dict()

    tt=int()
    if clk_All['PIN clk']['stage']==[0,'OUTPUT']:
        for kdx,kvalue in enumerate(clk_All):
            tt=tt+1
            All.update({kvalue:{'position':clk_All[kvalue]['position'],'stage':clk_All[kvalue]['stage']}})



    for idx in range(len(die_area)):
        for kdx in range(len(die_area[idx])):
            die_area[idx][kdx]=die_area[idx][kdx]/def_unit
    for ivalue in All:
        All[ivalue]['position'][0]=All[ivalue]['position'][0]/def_unit
        All[ivalue]['position'][1]=All[ivalue]['position'][1]/def_unit
    


    ##print(All['PIN clk'])
    ##print(die_area)


    start_line1=[[die_area[0][0],die_area[1][1]],[die_area[1][0],die_area[1][1]]]
    start_line2=[[die_area[1][0],die_area[0][1]],[die_area[1][0],die_area[1][1]]]
    first_square=copy.deepcopy(All)
    del first_square['PIN clk']

    appropriate_first_line=list()

    appropriate_line_x=list()
    appropriate_line_y=list()
    oddoreven=get_odd_or_even(first_square)
    start_line1_x=copy.deepcopy(start_line1)
    start_line1_y=copy.deepcopy(start_line2)
    alpha=1

    counts=int()
    target_num=int()
    new_line_x=list()
    half_line_x=get_half_line(start_line1_x,counts,target_num,new_line_x,first_square,alpha,'x')

    alpha=1
    counts=int()
    target_num=int()
    new_line_y=list()
    half_line_y=get_half_line(start_line1_y,counts,target_num,new_line_y,first_square,alpha,'y')
    print(half_line_x[0:2])
    print(half_line_y[0:2])

    if oddoreven=='odd':
        if half_line_x[2][0]==half_line_x[2][1] or half_line_x[2][0]==(half_line_x[2][1]-1):
            appropriate_line_x=half_line_x[0:2]
        if half_line_y[2][0]==half_line_y[2][1] or half_line_y[2][0]==(half_line_y[2][1]-1):
            appropriate_line_y=half_line_y[0:2]
    else:
        if half_line_x[2][0]==half_line_x[2][1]:
            appropriate_line_x=half_line_x[0:2]
        if half_line_y[2][0]==half_line_y[2][1]:
            appropriate_line_y=half_line_y[0:2]

    if len(half_line_x[0:2])==2 and len(half_line_y[0:2])==2:
        y_axis_dist=abs(half_line_x[0:2][0][1]-All['PIN clk']['position'][1])
        x_axis_dist=abs(half_line_y[0:2][0][0]-All['PIN clk']['position'][0])
        print(y_axis_dist)
        print(x_axis_dist)



    print(All['PIN clk'])
    return 0





def get_odd_or_even(square):
    kk=int()
    for ivalue in (square):
        kk=kk+1
    if kk&2==0:
        return 'even'
    else:
        return 'odd'







def get_half_line(start_line1_x,counts,target_num,new_line_x,first_square,alpha,xory):
    kkk=int()
    while True:
        counts=get_number(start_line1_x,first_square)[0]
        target_num=get_number(start_line1_x,first_square)[1]
        new_line_x=descending_find_line(start_line1_x,first_square,alpha,xory)

        if new_line_x=='break':
            break
        elif counts>target_num:
            alpha=alpha*0.1
            kkk=kkk+1
            while True:
                counts=get_number(start_line1_x,first_square)[0]
                target_num=get_number(start_line1_x,first_square)[1]
                new_new_line=ascending_find_line(new_line_x,first_square,alpha,xory)
                
                if new_new_line=='break':
                    break
                elif counts<target_num:
                    start_line1_x=new_new_line
                    alpha=alpha*0.1
                    kkk=kkk+1
                    break
                elif counts>target_num:
                    continue
        elif counts<target_num-1:
            continue

        if kkk==6:
            break

    new_line_x.append([counts,target_num])

    return new_line_x



def get_number(line,squares):
    xisconstant=int()
    yisconstant=int()

    if line[0][0]==line[1][0]:
        xisconstant=1
    elif line[0][1]==line[1][1]:
        yisconstant=1

    tt=int()
    for ivalue in squares:
        tt=tt+1

    target_number=int()
    odd_number=int()
    target_number2=int()

    if tt%2==0:
        target_number=tt/2
        odd_number=0

    else:
        target_number=int((tt+1)/2)
        target_number2=target_number-1
        odd_number=1

    counts=int()
    if xisconstant==1:
        for ivalue in squares:
            if squares[ivalue]['position'][0]>line[0][0]:
                counts=counts+1
            elif squares[ivalue]['position'][0]==line[0][0]:
                return ivalue+' overlapped'

        if odd_number==1:
            if counts==target_number or counts==target_number2:
                return 1

        else:
            if counts==target_number:
                return 1
        

    elif yisconstant==1:
        for ivalue in squares:
            if squares[ivalue]['position'][0]>line[0][1]:
                counts=counts+1
            elif squares[ivalue]['position'][0]==line[0][1]:
                return ivalue+' overlapped'
        
        if odd_number==1:        
            if counts==target_number or counts==target_number2:
                return 1
        
        else:
            if counts==target_number:
                return 1

    return [counts,target_number,odd_number]





def ascending_find_line(line,square,alpha,xory):
    if xory=='x':
        if type(get_number(line,square))!=1:
            line[0][1]=line[0][1]+alpha
            line[1][1]=line[1][1]+alpha
            return line

        elif get_number(line,square)==1:
            return 'break'    

    elif xory=='y':
        if type(get_number(line,square))!=1:
            line[0][0]=line[0][0]+alpha
            line[1][0]=line[1][0]+alpha
            return line

        elif get_number(line,square)==1:
            return 'break'    
    return 0




def descending_find_line(line,square,alpha,xory):
    if xory=='x':
        if type(get_number(line,square))!=1:
            line[0][1]=line[0][1]-alpha
            line[1][1]=line[1][1]-alpha
            return line

        elif get_number(line,square)==1:
            return 'break'

    elif xory=='y':
        if type(get_number(line,square))!=1:
            line[0][0]=line[0][0]-alpha
            line[1][0]=line[1][0]-alpha
            return line

        elif get_number(line,square)==1:
            return 'break'        
    return 0











if __name__ == "__main__":
    arguments=sys.argv
    print(arguments)
    def_name=arguments[1]
    ffffile_name=def_name.split('.def')[0]+'_revised.def'

    file_address_name=arguments[3]

    wire_mode=arguments[2]
    CLK_mode='ideal'
    liberty_type='example1_slow.lib'

    file_name=ffffile_name.split('.def')[0]
    netinfo=dict()

    file_path = '../data/deflef_to_graph_and_verilog/3. graphs/'+file_name+'(temp)/net_info_for_graph_'+file_name+'(temp).json'
    with open(file_path, 'r')as file:
        netinfo=json.load(file)
    file.close()


    file_path='../data/deflef_to_graph_and_verilog/3. graphs/'+file_name+'(temp)/temporary_net_info_'+file_name+'(temp).json'
    with open(file_path, 'r')as file:
        netinfo_for_clk=json.load(file)
    file.close()
    

    file_address='../data/macro_info_nangate_typical/'
    wire_load_model=list()   
    with open('../data/OPENSTA/wire_load_model_openSTA.json', 'r') as f:
        wire_load_model=json.load(f)
    f.close()


    default_wire_load_model=dict()
    for idx in range(len(wire_load_model)):
        if 'default_wire_load' in wire_load_model[idx]['wire_load']:
            default_wire_load_model=wire_load_model[idx]
    

    def_unit=netinfo_for_clk['def_unit_should_divide_distance']
    del netinfo_for_clk['def_unit_should_divide_distance']
    die_area=netinfo_for_clk['def_die_area']
    del netinfo_for_clk['def_die_area']






    typed_All=get_type_of_new_graph(netinfo,file_address)

    cutting_All=get_delnode_new_list(typed_All)
    CLK2reg_All=get_CLK2CK_new_graph(cutting_All)
    without_clk_All=get_new_del_related_with_CLK(cutting_All,CLK2reg_All)

    without_unconnected_All_clk=new_del_unconnected_nodes(CLK2reg_All)
    without_unconnected_All=new_del_unconnected_nodes(without_clk_All)



    stage_All_clk=get_new_stage_nodes_for_clk_nodes(without_unconnected_All_clk,netinfo_for_clk)

    stage_All=get_new_stage_nodes(without_unconnected_All)
    clk_All_with_wire_cap=get_new_wire_cap(stage_All_clk,default_wire_load_model)
    All_with_wire_cap=get_new_wire_cap(stage_All,default_wire_load_model)



    delay_with_clk_All=get_new_Delay_of_nodes_CLK(clk_All_with_wire_cap,CLK_mode)

    delay_only_first_stage_without_clk_All=get_new_Delay_of_nodes_stage0(All_with_wire_cap,delay_with_clk_All,wire_mode,liberty_type)
    delay_without_clk_All=get_new_all_Delay_Transition_of_nodes(delay_only_first_stage_without_clk_All,wire_mode,liberty_type)



    total_delay=list()
    total_delay_info=get_last_nodes_list(delay_without_clk_All)
    for idxxx in range(len(total_delay_info)):
        what_has_worst_delay=total_delay_info[idxxx]
        path_worst=get_new_worst_path(delay_without_clk_All,what_has_worst_delay)
        total_delay.append(path_worst)

    dir_list=os.listdir('../data/deflef_to_graph_and_verilog/results')

    if file_address_name not in dir_list:
        os.mkdir('../data/deflef_to_graph_and_verilog/results/'+file_address_name)
        wire_modess=['star','clique','hpwl']
        for wireidx in range(4):
            os.mkdir('../data/deflef_to_graph_and_verilog/results/'+file_address_name+'/test_7800_'+wire_modess[wireidx])
            os.mkdir('../data/deflef_to_graph_and_verilog/results/'+file_address_name+'/test_7800_without_clk_'+wire_modess[wireidx])
            os.mkdir('../data/deflef_to_graph_and_verilog/results/'+file_address_name+'/test_7800_zfor_clk_'+wire_modess[wireidx])

    file_pathtt='../data/deflef_to_graph_and_verilog/results/'+file_address_name+'/test_7800_'+wire_mode+'/'+file_name.split('_revised')[0]+'.json'
    with open(file_pathtt,'w') as f:
        json.dump(total_delay,f,indent=4)

    file_pathpath='../data/deflef_to_graph_and_verilog/results/'+file_address_name+'/test_7800_without_clk_'+wire_mode+'/'+file_name.split('_revised')[0]+'.json'
    with open(file_pathpath,'w') as f:
        json.dump(delay_without_clk_All,f,indent=4)

    file_pathpath='../data/deflef_to_graph_and_verilog/results/'+file_address_name+'/test_7800_zfor_clk_'+wire_mode+'/'+file_name.split('_revised')[0]+'.json'
    with open(file_pathpath,'w') as f:
        json.dump(stage_All_clk,f,indent=4)


##################################################################################################################################################



    '''file_pathpath='../data/deflef_to_graph_and_verilog/results/'+file_address_name+'/test_7800_without_clk_'+wire_mode+'/'+file_name.split('_revised')[0]+'.json'
    with open(file_pathpath,'r') as f:
        delay_without_clk_All=json.load(f)

    file_pathpath='../data/deflef_to_graph_and_verilog/results/'+file_address_name+'/test_7800_zfor_clk_'+wire_mode+'/'+file_name.split('_revised')[0]+'.json'
    with open(file_pathpath,'r') as f:
        stage_All_clk=json.load(f)'''







    ##group_list_of_startpoints_of_path=get_start_points(delay_without_clk_All,what_has_worst_delay)
    ##print(group_list_of_startpoints_of_path)


    '''for idx,ivalue in enumerate(delay_without_clk_All):
        if len(delay_without_clk_All[ivalue]['from'])==0 and ivalue.split(' ')[1]=='Q':
            kk=kk+1
            outnodes.append(ivalue)
            print(ivalue, delay_without_clk_All[ivalue])
    print(idx)
    print(kk)
    print()
    print(outnodes)'''

    '''parts_clk_all=get_clk_partitioning(clk_All,die_area,def_unit)'''
