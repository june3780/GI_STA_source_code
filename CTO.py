



import json

import numpy as np
import json
import copy

import pandas as pd
import time
import sys

import time






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
        print()

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










def get_new_Delay_of_nodes_CLK(clk_All_with_wire_cap,CLK_mode,wire_mode,lliberty_type):
    All=copy.deepcopy(clk_All_with_wire_cap)
    if CLK_mode=='ideal':
        for idx,ivalue in enumerate(All):
            All[ivalue]['fall_Delay']=0
            All[ivalue]['rise_Delay']=0
            All[ivalue]['fall_Transition']=0
            All[ivalue]['rise_Transition']=0
        return All
    else: ############################ 코딩 필요 (clk의 real한 경우)
        for idx,ivalue in enumerate(All):
            if All[ivalue]['stage']==[0,'OUTPUT']:
                All[ivalue]['fall_Delay']=0
                All[ivalue]['rise_Delay']=0
                All[ivalue]['fall_Transition']=0
                All[ivalue]['rise_Transition']=0
                All[ivalue]['load_capacitance_rise']=0
                All[ivalue]['load_capacitance_fall']=0

        for idx,ivalue in enumerate(All):
            if All[ivalue]['stage']==[0,'INPUT']:
                All[ivalue]['fall_Delay']=All[All[ivalue]['from'][0]]['fall_Delay']
                All[ivalue]['rise_Delay']=All[All[ivalue]['from'][0]]['rise_Delay']
                All[ivalue]['input_transition_fall']=All[All[ivalue]['from'][0]]['fall_Transition']
                All[ivalue]['input_transition_rise']=All[All[ivalue]['from'][0]]['rise_Transition']

        All=get_new_all_Delay_Transition_of_nodes(All,wire_mode,lliberty_type)

        max_stage=int()
        for ivalue in All:
            if max_stage<All[ivalue]['stage'][0]:
                max_stage=All[ivalue]['stage'][0]

        for ivalue in All:
            if All[ivalue]['stage'][0]==max_stage and All[ivalue]['direction']=='INPUT':
                All[ivalue].update({'rise_Transition':All[ivalue]['input_transition_rise']})
                All[ivalue].update({'fall_Transition':All[ivalue]['input_transition_fall']})

        max_delay=float()
        for ivalue in All:
            if All[ivalue]['stage'][0]==max_stage and All[ivalue]['direction']=='INPUT':
                if max_delay<All[ivalue]['rise_Delay']:
                    max_delay=All[ivalue]['rise_Delay']
        
        min_delay=max_delay
        for ivalue in All:
            if All[ivalue]['stage'][0]==max_stage and All[ivalue]['direction']=='INPUT':
                if min_delay>All[ivalue]['rise_Delay']:
                    min_delay=All[ivalue]['rise_Delay']

        for ivalue in All:
            if All[ivalue]['stage'][0]==max_stage and All[ivalue]['direction']=='INPUT':
                All[ivalue]['rise_Delay']=All[ivalue]['rise_Delay']-min_delay

        skew=max_delay-min_delay
        return [All,skew]










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
            checking_path_output='../data/OPENSTA/OPENSTA_'+liberty_type+'/'+All[ivalue]['macroID']+'/3. output: '+ivalue.split(' ')[1]

            checking_falling=TAll[ivalue.split(" ")[0]+' CK']['rise_Transition'] ############# 인풋 파라미터1-1 클락의 경우 unateness가 non-unate이다.
            checking_rising=TAll[ivalue.split(" ")[0]+' CK']['rise_Transition'] ############# 인풋 파라미터1-2

            load_capa_fall=float()
            load_capa_rise=float()
            for kdx in range(len(All[ivalue]['to'])):
                if All[All[ivalue]['to'][kdx]]['type']=='cell':
                    checking_path_input='../data/OPENSTA/OPENSTA_'+liberty_type+'/'+All[All[ivalue]['to'][kdx]]['macroID']+'/2. input: '+All[ivalue]['to'][kdx].split(" ")[1]+'.tsv'
                    df1=pd.read_csv(checking_path_input,sep='\t')
                    load_capa_rise=load_capa_rise+float(df1.iloc[1,1])
                    load_capa_fall=load_capa_fall+float(df1.iloc[0,1])
            load_capa_rise=load_capa_rise+All[ivalue][wirecap] ############### 인풋 파라미터2-1
            load_capa_fall=load_capa_fall+All[ivalue][wirecap] ############### 인풋 파라미터2-2
            All[ivalue]['load_capacitance_rise']=load_capa_rise
            All[ivalue]['load_capacitance_fall']=load_capa_fall

            df_fall_delay=pd.read_csv(checking_path_output+'/condition: 0, cell_fall.tsv',sep='\t')
            df_rise_delay=pd.read_csv(checking_path_output+'/condition: 0, cell_rise.tsv',sep='\t')
            df_fall_transition=pd.read_csv(checking_path_output+'/condition: 0, fall_transtion.tsv',sep='\t')
            df_rise_transition=pd.read_csv(checking_path_output+'/condition: 0, rise_transtion.tsv',sep='\t')
            
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
    condition_table='../data/OPENSTA/OPENSTA_'+liberty_type+'/'

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
                df_condition=pd.read_csv(condition_table+All[kvalue]['macroID']+'/3. output: '+kvalue.split(" ")[1]+'/0. info.tsv',sep='\t')

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
                        df4=pd.read_csv(condition_table+All[All[kvalue]['to'][tdx]]['macroID']+'/'+'2. input: '+All[kvalue]['to'][tdx].split(' ')[1]+'.tsv',sep='\t')
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
                        path_to_table=condition_table+All[kvalue]['macroID']+'/3. output: '+kvalue.split(" ")[1]+'/condition: 0, '
                    else:
                        path_to_table=condition_table+All[kvalue]['macroID']+'/3. output: '+kvalue.split(" ")[1]+'/condition: '+fall_delay_candidate[tdx][1][1].split(': ')[1]+', '

                    if fall_delay_candidate[tdx][1][0]=='negative_unate':
                        unate='negative_unate'
                        input_ttrraann=All[kvalue.split(' ')[0]+' '+fall_delay_candidate[tdx][0]]['input_transition_rise']
                        df5_delay=pd.read_csv(path_to_table+'cell_fall.tsv',sep='\t')
                        df5_trans=pd.read_csv(path_to_table+'fall_transtion.tsv',sep='\t')

                    elif fall_delay_candidate[tdx][1][0]=='positive_unate':
                        unate='positive_unate'
                        input_ttrraann=All[kvalue.split(' ')[0]+' '+fall_delay_candidate[tdx][0]]['input_transition_fall']
                        df5_delay=pd.read_csv(path_to_table+'cell_fall.tsv',sep='\t')
                        df5_trans=pd.read_csv(path_to_table+'fall_transtion.tsv',sep='\t')

                    fall_delay_finals.append([fall_delay_candidate[tdx][0],fall_delay_candidate[tdx][1][2]+get_value_from_table(df5_delay,input_ttrraann,load_capa),get_value_from_table(df5_trans,input_ttrraann,load_capa),unate])
                    

                rise_delay_finals=list()
                for tdx in range(len(rise_delay_candidate)):

                    input_ttrraann=float()
                    unate=str()
                    load_capa=All[kvalue]['load_capacitance_rise']
                    df5_delay=pd.DataFrame()
                    df5_trans=pd.DataFrame()
                    if rise_delay_candidate[tdx][1][1]=='No_condition':
                        path_to_table=condition_table+All[kvalue]['macroID']+'/3. output: '+kvalue.split(" ")[1]+'/condition: 0, '
                    else:
                        path_to_table=condition_table+All[kvalue]['macroID']+'/3. output: '+kvalue.split(" ")[1]+'/condition: '+rise_delay_candidate[tdx][1][1].split(': ')[1]+', '

                    if rise_delay_candidate[tdx][1][0]=='negative_unate':
                        unate='negative_unate'
                        input_ttrraann=All[kvalue.split(' ')[0]+' '+rise_delay_candidate[tdx][0]]['input_transition_fall']
                        df5_delay=pd.read_csv(path_to_table+'cell_rise.tsv',sep='\t')
                        df5_trans=pd.read_csv(path_to_table+'rise_transtion.tsv',sep='\t')

                    elif rise_delay_candidate[tdx][1][0]=='positive_unate':
                        unate='positive_unate'
                        input_ttrraann=All[kvalue.split(' ')[0]+' '+rise_delay_candidate[tdx][0]]['input_transition_rise']
                        df5_delay=pd.read_csv(path_to_table+'cell_rise.tsv',sep='\t')
                        df5_trans=pd.read_csv(path_to_table+'rise_transtion.tsv',sep='\t')

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


###########################################################################




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


        return set(list_points)




def get_list(All,strstr,listlist):

    checking=All[strstr]['from'][0]
    if len(All[checking]['from'])==0:
        listlist.append(checking)
    else:
        for idx in range(len(All[checking]['from'])):
            get_list(All,All[checking]['from'][idx],listlist)
    return listlist

########################################################################





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
    
    start_line1=[[die_area[0][0],die_area[1][1]],[die_area[1][0],die_area[1][1]]]
    start_line2=[[die_area[1][0],die_area[0][1]],[die_area[1][0],die_area[1][1]]]
    first_square=copy.deepcopy(All)
    Clk_pos=first_square['PIN clk']['position']
    del first_square['PIN clk']


#######################################################################################################
    appropriate_first_line=list()

    appropriate_line_x=list()
    appropriate_line_y=list()
    xshouldbelow=int()
    yshouldbelow=int()
    start_line1_x=copy.deepcopy(start_line1)
    start_line1_y=copy.deepcopy(start_line2)


    half_line_x=get_half_line(start_line1_x,first_square,'x')
    if half_line_x[1]==1:
        appropriate_line_x=half_line_x[0]
    else:
        xshouldbelow=1 ############################## x가 낮아져서 count수를 늘려야 된다.


    half_line_y=get_half_line(start_line1_y,first_square,'y')
    if half_line_y[1]==1:
        appropriate_line_y=half_line_y[0]
    else:
        yshouldbelow=1 ############################## y가 낮아져서 count수를 늘려야 된다.


    paralleltoaxis=str()
    second_square1=dict()
    second_square2=dict()
    if xshouldbelow==0 and yshouldbelow==0:

        candidate_counts1=float()
        distance_to_parallel_yaxis=abs(appropriate_line_y[0][0]-Clk_pos[0])
        distance_to_parallel_xaxis=abs(appropriate_line_x[0][1]-Clk_pos[1])

        if distance_to_parallel_yaxis<distance_to_parallel_xaxis:
            appropriate_first_line=appropriate_line_y
            paralleltoaxis='y'
            for allidx,allivalue in enumerate(first_square):
                if first_square[allivalue]['position'][0]>appropriate_first_line[0][0]:
                    second_square1.update({allivalue:first_square[allivalue]})
                else:
                    second_square2.update({allivalue:first_square[allivalue]})

        else: 
            appropriate_first_line=appropriate_line_x
            paralleltoaxis='x'
            for allidx,allivalue in enumerate(first_square):
                if first_square[allivalue]['position'][1]>appropriate_first_line[0][1]:
                    second_square1.update({allivalue:first_square[allivalue]})
                else:
                    second_square2.update({allivalue:first_square[allivalue]})


    elif xshouldbelow==1 and yshouldbelow==0:

        appropriate_first_line=appropriate_line_y
        for allidx,allivalue in enumerate(first_square):
            if first_square[allivalue]['position'][0]>appropriate_first_line[0][0]:
                second_square1.update({allivalue:first_square[allivalue]})
            else:
                second_square2.update({allivalue:first_square[allivalue]})
        paralleltoaxis='y'
    

    elif xshouldbelow==0 and yshouldbelow==1:

        appropriate_first_line=appropriate_line_x
        for allidx,allivalue in enumerate(first_square):
            
            if first_square[allivalue]['position'][1]>appropriate_first_line[0][1]:
                second_square1.update({allivalue:first_square[allivalue]})
            else:
                second_square2.update({allivalue:first_square[allivalue]})
        paralleltoaxis='x'


    if xshouldbelow==1 and yshouldbelow==1:

        if get_temporary_line(half_line_x,first_square,'x')[1]<get_temporary_line(half_line_y,first_square,'y')[1]:

            comparing_float=half_line_x[0][0][1]
            for allidx,allivalue in enumerate(first_square):
                if first_square[allivalue]['position'][1]>comparing_float:
                    second_square1.update({allivalue:first_square[allivalue]})
                else:
                    second_square2.update({allivalue:first_square[allivalue]})

            paralleltoaxis='x'
            switching_list=get_temporary_line(half_line_x,first_square,'x')[0]

            for allidx in range(len(switching_list)):
                second_square1.update({switching_list[allidx]:second_square2[switching_list[allidx]]})
                second_square2.pop(switching_list[allidx])

        
        else:

            comparing_float=half_line_y[0][0][0]
            for allidx,allivalue in enumerate(first_square):
                if first_square[allivalue]['position'][0]>comparing_float:
                    second_square1.update({allivalue:first_square[allivalue]})
                else:
                    second_square2.update({allivalue:first_square[allivalue]})

            paralleltoaxis='y'
            switching_list=get_temporary_line(half_line_y,first_square,'y')[0]
            for allidx in range(len(switching_list)):
                second_square1.update({switching_list[allidx]:second_square2[switching_list[allidx]]})
                second_square2.pop(switching_list[allidx])

    square_for_1=copy.deepcopy(first_square)
    square_for_2=copy.deepcopy(first_square)

    for allivalue in second_square2:
        if allivalue in square_for_1:
            del square_for_1[allivalue]

    for allivalue in second_square1:
        if allivalue in square_for_2:
            del square_for_2[allivalue]

    buffer_list=dict()
    buffer_list.update({'temp_buffer0_0':{'from':['PIN clk'],'to':[],'position':[]}})
    return [second_square1,second_square2,paralleltoaxis,square_for_1,square_for_2,buffer_list]







def get_small_groups(second_square):

    second_square1=second_square[0]
    second_square2=second_square[1]
    square_info_for_1=second_square[3]
    square_info_for_2=second_square[4]
    hpwl1=get_hpwl_square(second_square1,square_info_for_1)
    hpwl2=get_hpwl_square(second_square2,square_info_for_2)


    if second_square[2]=='y':
        test_line111=[[hpwl1[0][0]-1,hpwl1[1][1]+1],[hpwl1[1][0]+1,hpwl1[1][1]+1]]
        test_line222=[[hpwl2[0][0]-1,hpwl2[1][1]+1],[hpwl2[1][0]+1,hpwl2[1][1]+1]]
        second_square[2]='x'
    else:
        test_line111=[[hpwl1[1][0]+1,hpwl1[0][1]-1],[hpwl1[1][0]+1,hpwl1[1][1]+1]]
        test_line222=[[hpwl2[1][0]+1,hpwl2[0][1]-1],[hpwl2[1][0]+1,hpwl2[1][1]+1]]
        second_square[2]='y'


    xxxxxx=get_small_square_partitioning(square_info_for_1,test_line111,second_square[2])
    yyyyyy=get_small_square_partitioning(square_info_for_2,test_line222,second_square[2])
    return [xxxxxx,yyyyyy]







def get_group_of_buffer(part_of_clk,temp_macro):
    kk=dict()

    number=1
    kkkk=get_segment_squares(part_of_clk[0:5],kk,number)
    tttt=copy.deepcopy(kkkk)


    naming_dict=dict()
    for idx, ivalue in enumerate(kkkk):
        naming_dict.update({ivalue:'temp_buffer_'+str(idx)})


    for ivalue in tttt:
        if ivalue in naming_dict:
            kkkk.update({naming_dict[ivalue]:kkkk[ivalue]})
            del kkkk[ivalue]

    tttt=copy.deepcopy(kkkk)

    for ivalue in tttt:
        for kdx in range(len(tttt[ivalue]['to'])):
            if len(tttt[ivalue]['to'][kdx].split('CK'))==2:
                kkkk[ivalue]['to'][kdx]=kkkk[ivalue]['to'][kdx].split('[\'')[1].split('\']')[0]
                continue
            kkkk[ivalue]['to'][kdx]=naming_dict[kkkk[ivalue]['to'][kdx]]

    tttt=copy.deepcopy(kkkk)
    
    for ivalue in tttt:
        for kvalue in tttt:
            if ivalue in tttt[kvalue]['to']:
                kkkk[ivalue]['from']=[kvalue]

    tttt=copy.deepcopy(kkkk)

    for ivalue in tttt:
        kkkk.update({ivalue+' A':{'type':'cell','direction':'INPUT','to':[ivalue+' Z'],'from':tttt[ivalue]['from'],'macroID':temp_macro,'cell_type':'Combinational'}})
        kkkk.update({ivalue+' Z':{'type':'cell','direction':'OUTPUT','to':tttt[ivalue]['to'],'from':[ivalue+' A'],'macroID':temp_macro,'cell_type':'Combinational'}})
        del kkkk[ivalue]

    for ivalue in kkkk:
        if 'Z' in ivalue:
            for kdx in range(len(kkkk[ivalue]['to'])):
                if 'CK' not in kkkk[ivalue]['to'][kdx]:
                    kkkk[ivalue]['to'][kdx]=kkkk[ivalue]['to'][kdx]+' A'
        if 'A' in ivalue:
            for kdx in range(len(kkkk[ivalue]['from'])):
                kkkk[ivalue]['from'][kdx]=kkkk[ivalue]['from'][kdx]+' Z'
    
    connecting=str()
    for ivalue in kkkk:
        if len(kkkk[ivalue]['from'])==0:
            connecting=ivalue

    kkkk.update({'temp_clk_buffer A':{'type': 'cell', 'direction': 'INPUT', 'to': ['temp_clk_buffer Z'],'from':['PIN clk'], 'macroID': temp_macro, 'cell_type': 'Combinational'}})
    kkkk.update({'temp_clk_buffer Z':{'type': 'cell', 'direction': 'OUTPUT', 'to': [connecting],'from':['temp_clk_buffer A'], 'macroID': temp_macro, 'cell_type': 'Combinational'}})
    kkkk['temp_buffer_0 A']['from']=['temp_clk_buffer Z']
    tttttt=int()

    return kkkk






def get_segment_squares(square,kk,number):
    name_of_dict=list()
    for ivalue in list(square[0].keys()):
        name_of_dict.append(ivalue)
    for ivalue in list(square[1].keys()):
        name_of_dict.append(ivalue)

    if len(square[3])>=number and len(square[4])>=number:
        square1=get_small_groups(square)[0]
        square2=get_small_groups(square)[1]

        name_of_dic1t=list()
        for ivalue in list(square1[0].keys()):
            name_of_dic1t.append(ivalue)
        for ivalue in list(square1[1].keys()):
            name_of_dic1t.append(ivalue)

        name_of_dic2t=list()
        for ivalue in list(square2[0].keys()):
            name_of_dic2t.append(ivalue)
        for ivalue in list(square2[1].keys()):
            name_of_dic2t.append(ivalue)


        kk.update({str(name_of_dict):{'to':[str(name_of_dic1t),str(name_of_dic2t)],'from':[]}})

        get_segment_squares(square1,kk,number)
        get_segment_squares(square2,kk,number)
        
        return kk
    else:
        return kk






def get_small_square_partitioning(square_info,line,xory):

#######################################################################################################
    appropriate_first_line=list()

    xshouldbelow=int()
    yshouldbelow=int()
    start_line1=copy.deepcopy(line)

    half_line=get_half_line(start_line1,square_info,xory)

    if half_line[1]==1:
        appropriate_first_line=half_line[0]
    else:
        if xory=='x':
            yshouldbelow=1 ############################## y가 낮아져서 count수를 늘려야 된다.
        else:
            xshouldbelow=1 ############################## x가 낮아져서 count수를 늘려야 한다.



    paralleltoaxis=str()
    second_square1=dict()
    second_square2=dict()

    if xshouldbelow==1 and yshouldbelow==0:

            comparing_float=half_line[0][0][0]
            for allidx,allivalue in enumerate(square_info):
                if square_info[allivalue]['position'][0]>comparing_float:
                    second_square1.update({allivalue:square_info[allivalue]})
                else:
                    second_square2.update({allivalue:square_info[allivalue]})


            paralleltoaxis='y'
            switching_list=get_temporary_line(half_line,square_info,'y')[0]
            for allidx in range(len(switching_list)):
                second_square1.update({switching_list[allidx]:second_square2[switching_list[allidx]]})
                second_square2.pop(switching_list[allidx])
    

    elif xshouldbelow==0 and yshouldbelow==1:

            comparing_float=half_line[0][0][1]
            for allidx,allivalue in enumerate(square_info):
                if square_info[allivalue]['position'][1]>comparing_float:
                    second_square1.update({allivalue:square_info[allivalue]})
                else:
                    second_square2.update({allivalue:square_info[allivalue]})


            paralleltoaxis='x'
            switching_list=get_temporary_line(half_line,square_info,'x')[0]
            for allidx in range(len(switching_list)):
                second_square1.update({switching_list[allidx]:second_square2[switching_list[allidx]]})
                second_square2.pop(switching_list[allidx])

    
    else:
        paralleltoaxis=xory
        if xory=='x':
            for allidx,allivalue in enumerate(square_info):
                if square_info[allivalue]['position'][1]>appropriate_first_line[0][1]:
                    second_square1.update({allivalue:square_info[allivalue]})
                else:
                    second_square2.update({allivalue:square_info[allivalue]})

        else: 
            for allidx,allivalue in enumerate(square_info):
                if square_info[allivalue]['position'][0]>appropriate_first_line[0][0]:
                    second_square1.update({allivalue:square_info[allivalue]})
                else:
                    second_square2.update({allivalue:square_info[allivalue]})




    square_for_1=copy.deepcopy(square_info)
    square_for_2=copy.deepcopy(square_info)

    for allivalue in second_square2:
        if allivalue in square_for_1:
            del square_for_1[allivalue]

    for allivalue in second_square1:
        if allivalue in square_for_2:
            del square_for_2[allivalue]


    return [second_square1,second_square2,paralleltoaxis,square_for_1,square_for_2]










def get_hpwl_square(square,info):
    max_x_in_second_square1=float()
    max_y_in_second_square1=float()
    min_x_in_second_square1=float()
    min_y_in_second_square1=float()
    for ivalue in (square):
        if max_x_in_second_square1 <info[ivalue]['position'][0]:
            max_x_in_second_square1=info[ivalue]['position'][0]
        if max_y_in_second_square1 <info[ivalue]['position'][1]:
            max_y_in_second_square1=info[ivalue]['position'][1]
    min_x_in_second_square1=max_x_in_second_square1
    min_y_in_second_square1=max_y_in_second_square1
    for ivalue in (square):
        if min_x_in_second_square1 >info[ivalue]['position'][0]:
            min_x_in_second_square1=info[ivalue]['position'][0]
        if min_y_in_second_square1 >info[ivalue]['position'][1]:
            min_y_in_second_square1=info[ivalue]['position'][1]

    return [[min_x_in_second_square1,min_y_in_second_square1],[max_x_in_second_square1,max_y_in_second_square1]]








def get_temporary_line(line_x,square,xory):
    candidate_counts1=float()
    objective_counts=int()

    if get_number(line_x[0],square)[2]==1:
        objective_counts=get_number(line_x[0],square)[1]-get_number(line_x[0],square)[0]-1
    else:
        objective_counts=get_number(line_x[0],square)[1]-get_number(line_x[0],square)[0]


    testing_half_xxx=copy.deepcopy(line_x)

    max_along_less_y=float()
    latest_del_in_testing_second_square2=list()

    while True:
        will_del_in_testing_second_square2=list()

        for ivalueivalue in square:
            if xory=='x':
                if square[ivalueivalue]['position'][1]<testing_half_xxx[0][0][1]:
                    if max_along_less_y<square[ivalueivalue]['position'][1]:
                        max_along_less_y=square[ivalueivalue]['position'][1]
            else:
                if square[ivalueivalue]['position'][0]<testing_half_xxx[0][0][0]:
                    if max_along_less_y<square[ivalueivalue]['position'][0]:
                        max_along_less_y=square[ivalueivalue]['position'][0]             

        for ivalueivalue in square:
            if xory=='x':
                if square[ivalueivalue]['position'][1]==max_along_less_y:
                    will_del_in_testing_second_square2.append(ivalueivalue)
            else:
                if square[ivalueivalue]['position'][0]==max_along_less_y:
                    will_del_in_testing_second_square2.append(ivalueivalue)


        couldbe_next_line=list()
        disdis=float()
        if xory=='x':
            couldbe_next_line=[[[testing_half_xxx[0][0][0],(testing_half_xxx[0][0][1]+max_along_less_y)/2],\
                [testing_half_xxx[0][1][0],(testing_half_xxx[0][1][1]+max_along_less_y)/2]],testing_half_xxx[1]]
            disdis=testing_half_xxx[0][1][1]-max_along_less_y
        else:
            couldbe_next_line=[[[testing_half_xxx[0][0][1],(testing_half_xxx[0][0][0]+max_along_less_y)/2],\
                [testing_half_xxx[0][1][1],(testing_half_xxx[0][1][0]+max_along_less_y)/2]],testing_half_xxx[1]]
            disdis=testing_half_xxx[0][1][0]-max_along_less_y

        
        

        if objective_counts==len(will_del_in_testing_second_square2):
            for ttddxx in range(len(will_del_in_testing_second_square2)):
                latest_del_in_testing_second_square2.append(will_del_in_testing_second_square2[ttddxx])
            break

        elif objective_counts<len(will_del_in_testing_second_square2):
            candidate_counts1=candidate_counts1+disdis*objective_counts

            listlist=list()
            for kvalue in will_del_in_testing_second_square2:
                if xory=='x':
                    listlist.append([kvalue,square[kvalue]['position'][0]])
                else:
                    listlist.append([kvalue,square[kvalue]['position'][1]])

            for ktdx in range(len(listlist)):
                for tdx in range(len(listlist)):
                    if tdx ==0:
                        continue
                    elif listlist[tdx][1]<listlist[tdx-1][1]:
                        temp=list()
                        temp=copy.deepcopy(listlist[tdx])
                        listlist[tdx]=copy.deepcopy(listlist[tdx-1])
                        listlist[tdx-1]=copy.deepcopy(temp)

            for tdx in range(objective_counts):
                latest_del_in_testing_second_square2.append(listlist[tdx][0])
            break

        else:
            objective_counts=objective_counts-len(will_del_in_testing_second_square2)
            for kvalue in will_del_in_testing_second_square2:
                latest_del_in_testing_second_square2.append(kvalue)
            candidate_counts1=candidate_counts1+disdis*len(will_del_in_testing_second_square2)
            testing_half_xxx=copy.deepcopy(couldbe_next_line)
            continue

    return [latest_del_in_testing_second_square2,candidate_counts1]





def get_half_line(start_line1_x,first_square,xory):
    kkk=int()
    beta=1
    success_line=int()
    if_the_line_is_half=copy.deepcopy(start_line1_x)

    while True:
        if get_number(if_the_line_is_half,first_square)==1:
            success_line=1
            break
        elif 'overlapped' in get_number(if_the_line_is_half,first_square):
            if xory=='x':
                if_the_line_is_half[0][1]=if_the_line_is_half[0][1]-beta
                if_the_line_is_half[1][1]=if_the_line_is_half[1][1]-beta
            else:
                if_the_line_is_half[0][0]=if_the_line_is_half[0][0]-beta
                if_the_line_is_half[1][0]=if_the_line_is_half[1][0]-beta        
        elif get_number(if_the_line_is_half,first_square)[0]<get_number(if_the_line_is_half,first_square)[1]+1:
            if xory=='x':
                if_the_line_is_half[0][1]=if_the_line_is_half[0][1]-beta
                if_the_line_is_half[1][1]=if_the_line_is_half[1][1]-beta
            else:
                
                if_the_line_is_half[0][0]=if_the_line_is_half[0][0]-beta
                if_the_line_is_half[1][0]=if_the_line_is_half[1][0]-beta   
        elif get_number(if_the_line_is_half,first_square)[0]>get_number(if_the_line_is_half,first_square)[1]:
                second_while=str()
                beta=beta*0.1

                kkk=kkk+1
                while True:
                    if get_number(if_the_line_is_half,first_square)==1:
                        success_line=1
                        second_while='break'
                        break
                    elif 'overlapped' in get_number(if_the_line_is_half,first_square):
                        if xory=='x':
                            if_the_line_is_half[0][1]=if_the_line_is_half[0][1]+beta
                            if_the_line_is_half[1][1]=if_the_line_is_half[1][1]+beta
                        else:
                            if_the_line_is_half[0][0]=if_the_line_is_half[0][0]+beta
                            if_the_line_is_half[1][0]=if_the_line_is_half[1][0]+beta   
                    elif (get_number(if_the_line_is_half,first_square)[0]>(get_number(if_the_line_is_half,first_square)[1])and get_number(if_the_line_is_half,first_square)[2]==1)or (get_number(if_the_line_is_half,first_square)[0]>(get_number(if_the_line_is_half,first_square)[1]) and get_number(if_the_line_is_half,first_square)[2]==0):
                        if xory=='x':
                            if_the_line_is_half[0][1]=if_the_line_is_half[0][1]+beta
                            if_the_line_is_half[1][1]=if_the_line_is_half[1][1]+beta
                        else:
                            if_the_line_is_half[0][0]=if_the_line_is_half[0][0]+beta
                            if_the_line_is_half[1][0]=if_the_line_is_half[1][0]+beta
                    elif (get_number(if_the_line_is_half,first_square)[0]<(get_number(if_the_line_is_half,first_square)[1]-1)and get_number(if_the_line_is_half,first_square)[2]==1)or (get_number(if_the_line_is_half,first_square)[0]<(get_number(if_the_line_is_half,first_square)[1]) and get_number(if_the_line_is_half,first_square)[2]==0):
                        kkk=kkk+1
                        break
                
                if  second_while=='break':
                    break
        if kkk==10:
            break
    
    return [if_the_line_is_half,success_line]




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
        target_number=int(tt/2)
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
            if squares[ivalue]['position'][1]>line[0][1]:
                counts=counts+1
            elif squares[ivalue]['position'][1]==line[0][1]:
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






def get_stage_with_CTS(clk, cts):
    for ivalue in clk:
        clk[ivalue]['from']=list()
        del clk[ivalue]['stage']
    clk['PIN clk']['to']=list()
    clk['PIN clk']['wire_length_hpwl']=float()
    clk['PIN clk']['wire_length_star']=float()
    clk['PIN clk']['wire_length_clique']=float()
    clk['PIN clk']['position']=list()
    
    for ivalue in cts:

        if cts[ivalue]['from'][0]=='PIN clk':
            clk['PIN clk']['to']=[ivalue]
        for jdx in range(len(cts[ivalue]['to'])):
            for kvalue in clk:
                if kvalue in cts[ivalue]['to'][jdx]:
                    clk[kvalue]['from']=[ivalue]

    cts.update(clk)
    All=get_new_stage_nodes(cts)
    return All





def get_new_position_of_CTS_cells(All,dieArea,temp_macro,clkpos):
    max_stage=int()
    for ivalue in All:
        if max_stage<All[ivalue]['stage'][0]:
            max_stage=All[ivalue]['stage'][0]


    last_temp_number=int()

    for ivalue in All:
        if All[ivalue]['stage'][1]=='OUTPUT' and 'clk' not in ivalue:
            last_temp=ivalue.split('temp_buffer_')[1].split(' ')[0]
            if last_temp_number<int(last_temp):
                last_temp_number=int(last_temp)

    TAll=copy.deepcopy(All)

    kkk=int()
    for ivalue in TAll:
        if All[ivalue]['stage'][1]=='OUTPUT' and All[ivalue]['stage'][0]==max_stage-1:
            counting_of_ck=int()
            for idx in range(len(All[ivalue]['to'])):
                if 'CK' in All[ivalue]['to'][idx]:
                    counting_of_ck=counting_of_ck+1
            if counting_of_ck==2:
                last_temp_number=last_temp_number+1
                All.update({'temp_buffer_'+str(last_temp_number)+' Z':{'type': 'cell', 'direction': 'OUTPUT', 'to':All[ivalue]['to'],'from':['temp_buffer_'+str(last_temp_number)+' A'],\
                    'macroID': temp_macro, 'cell_type': 'Combinational', 'stage':[max_stage,'OUTPUT']}})
                for kdx in range(len(All['temp_buffer_'+str(last_temp_number)+' Z']['to'])):
                    All[All['temp_buffer_'+str(last_temp_number)+' Z']['to'][kdx]]['from']=['temp_buffer_'+str(last_temp_number)+' Z']
                    All[All['temp_buffer_'+str(last_temp_number)+' Z']['to'][kdx]]['stage']=[max_stage,'INPUT']
                All.update({'temp_buffer_'+str(last_temp_number)+' A':{'type': 'cell', 'direction': 'INPUT', 'to':['temp_buffer_'+str(last_temp_number)+' Z'],'from':[ivalue],\
                    'macroID': temp_macro, 'cell_type': 'Combinational', 'stage':[max_stage-1,'INPUT']}})
                All[ivalue]['to']=['temp_buffer_'+str(last_temp_number)+' A']


    for ivalue in TAll:
        if All[ivalue]['stage'][1]=='OUTPUT' and All[ivalue]['stage'][0]==max_stage-1:
            counting_of_ck=int()
            whereisCK=int()
            for idx in range(len(All[ivalue]['to'])):
                if 'CK' in All[ivalue]['to'][idx]:
                    whereisCK=idx
                    counting_of_ck=counting_of_ck+1
            if counting_of_ck==1:
                last_temp_number=last_temp_number+1
                All.update({'temp_buffer_'+str(last_temp_number)+' Z':{'type': 'cell', 'direction': 'OUTPUT', 'to':[All[ivalue]['to'][whereisCK]],'from':['temp_buffer_'+str(last_temp_number)+' A'],\
                    'macroID': temp_macro, 'cell_type': 'Combinational', 'stage':[max_stage,'OUTPUT']}})
                All[All[ivalue]['to'][whereisCK]]['from']=['temp_buffer_'+str(last_temp_number)+' Z']
                All[All[ivalue]['to'][whereisCK]]['stage']=[max_stage,'INPUT']
                All.update({'temp_buffer_'+str(last_temp_number)+' A':{'type': 'cell', 'direction': 'INPUT', 'to':['temp_buffer_'+str(last_temp_number)+' Z'],'from':[ivalue],\
                    'macroID': temp_macro, 'cell_type': 'Combinational', 'stage':[max_stage-1,'INPUT']}})
                All[ivalue]['to'][whereisCK]='temp_buffer_'+str(last_temp_number)+' A'


    All=get_candidate_position_dict(All,max_stage,dieArea,temp_macro)[0]
    if All=='Error':
        return 'Error'

    position_dict=get_candidate_position_dict(All,max_stage,dieArea,temp_macro)[1]
    if position_dict=='Error':
        return 'Error'

    for ivalue in All:
        if All[ivalue]['stage'][0]==max_stage and All[ivalue]['direction']=='OUTPUT':
            max_stage_minus_one=All[All[ivalue]['from'][0]]['from'][0]
            if len(All[max_stage_minus_one]['to']) ==1 and 'position' not in All[ivalue]:

                max_stage_minus_two=All[All[max_stage_minus_one]['from'][0]]['from'][0]
                for jdx in range(len(All[max_stage_minus_two]['to'])):
                    if All[All[max_stage_minus_two]['to'][jdx]]['to'][0]==max_stage_minus_one:
                        continue
                    else:
                        other_max_stage_with_same_minus_one_stage=All[All[max_stage_minus_two]['to'][jdx]]['to'][0]

                        if len(All[other_max_stage_with_same_minus_one_stage]['to'])==1 and 'position' in All[All[All[other_max_stage_with_same_minus_one_stage]['to'][0]]['to'][0]]:
                            first_position=position_dict[ivalue]['candidate_position']
                            second_position=[All[All[All[other_max_stage_with_same_minus_one_stage]['to'][0]]['to'][0]]['position']]
                            All[ivalue].update({'position':get_hpwl_by_two_positions(first_position,second_position)[0]})

                        elif len(All[other_max_stage_with_same_minus_one_stage]['to'])==2:
                            position_of_other_1=All[All[All[other_max_stage_with_same_minus_one_stage]['to'][0]]['to'][0]]['position']
                            position_of_other_2=All[All[All[other_max_stage_with_same_minus_one_stage]['to'][1]]['to'][0]]['position']
                            other_position=[(position_of_other_1[0]+position_of_other_2[0])/2,(position_of_other_1[1]+position_of_other_2[1])/2]
                            first_position=position_dict[ivalue]['candidate_position']
                            second_position=[other_position]
                            All[ivalue].update({'position':get_hpwl_by_two_positions(first_position,second_position)[0]})
                        
                        else:
                            other_cell=All[All[other_max_stage_with_same_minus_one_stage]['to'][0]]['to'][0]
                            first_position=position_dict[ivalue]['candidate_position']
                            second_position=position_dict[other_cell]['candidate_position']
                            All[ivalue].update({'position':get_hpwl_by_two_positions(first_position,second_position)[0]})
                            All[other_cell].update({'position':get_hpwl_by_two_positions(first_position,second_position)[1]})

    for ivalue in All:
        if All[ivalue]['stage'][0]==max_stage-1 and All[ivalue]['direction']=='INPUT':
            A_position=get_input_position(All[All[ivalue]['to'][0]]['position'],temp_macro)
            All[ivalue].update({'position':A_position})


    All=get_candidate_position_dict(All,max_stage-1,dieArea,temp_macro)[0]
    if All=='Error':
        return 'Error'

    position_dict=get_candidate_position_dict(All,max_stage-1,dieArea,temp_macro)[1]
    if position_dict=='Error':
        return 'Error'

    for ivalue in All:
        if All[ivalue]['stage'][0]==max_stage-1 and All[ivalue]['direction']=='OUTPUT':
            if len(All[ivalue]['to']) ==1 and 'position' not in All[ivalue]:
                upper_stage=All[All[ivalue]['from'][0]]['from'][0]
                other_stage=str()
                if All[upper_stage]['to'][0]==All[ivalue]['from'][0]:
                    other_stage=All[All[upper_stage]['to'][1]]['to'][0]
                else:
                    other_stage=All[All[upper_stage]['to'][0]]['to'][0]

                if 'position' in All[other_stage]:
                    first_position=position_dict[ivalue]['candidate_position']
                    second_position=[All[other_stage]['position']]
                    All[ivalue].update({'position':get_hpwl_by_two_positions(first_position,second_position)[0]})

                else:
                    first_position=position_dict[ivalue]['candidate_position']
                    second_position=position_dict[other_stage]['candidate_position']
                    All[ivalue].update({'position':get_hpwl_by_two_positions(first_position,second_position)[0]})
                    All[other_stage].update({'position':get_hpwl_by_two_positions(first_position,second_position)[1]})                    

    for ivalue in All:
        if All[ivalue]['stage'][0]==max_stage-2 and All[ivalue]['direction']=='INPUT':
            A_position=get_input_position(All[All[ivalue]['to'][0]]['position'],temp_macro)
            All[ivalue].update({'position':A_position})


    counts=max_stage-2
    while True:
        if counts==1:
            break

        All=get_candidate_position_dict(All,counts,dieArea,temp_macro)[0]
        if All=='Error':
            return 'Error'

        for ivalue in All:
            if All[ivalue]['stage'][0]==counts-1 and All[ivalue]['direction']=='INPUT':
                A_position=get_input_position(All[All[ivalue]['to'][0]]['position'],temp_macro)
                All[ivalue].update({'position':A_position})
        counts=counts-1

    for ivalue in All:
        if ivalue =='PIN clk':
            continue
        All[ivalue]['stage'][0]=All[ivalue]['stage'][0]-1
    
    del All['temp_clk_buffer A']
    del All['temp_clk_buffer Z']
    All['temp_buffer_0 A']['from']=['PIN clk']
    All['PIN clk']['to']=['temp_buffer_0 A']
    All['PIN clk']['position']=clkpos
    

    length_dict=dict()
    for ivalue in All:
        if (All[ivalue]['type']=='PIN' and All[ivalue]['direction']=='INPUT') or (All[ivalue]['type']=='cell' and All[ivalue]['direction']=='OUTPUT'):
            length_dict.update({ivalue:[All[ivalue]['position']]})

    for ivalue in length_dict:
        for kdx in range(len(All[ivalue]['to'])):
            length_dict[ivalue].append(All[All[ivalue]['to'][kdx]]['position'])
        All[ivalue].update({'wire_length_hpwl':get_new_wirelength_hpwl(length_dict[ivalue]),'wire_length_clique':get_new_wirelength_clique(length_dict[ivalue]),'wire_length_star':get_new_wirelength_star(length_dict[ivalue])})


    return All











def get_candidate_position_dict(TAll,max_stage,dieArea,temp_macro):
    All=copy.deepcopy(TAll)
    max_minimum_length=float()
    position_dict=dict()

    cvalue_dict=dict()

    for ivalue in All:
        if All[ivalue]['stage'][0]==max_stage and All[ivalue]['direction']=='OUTPUT' and len(All[ivalue]['to'])==2:
            pos1=list()
            pos2=list()
            for idx in range(len(All[ivalue]['to'])):
                if idx==0:
                    pos1= All[All[ivalue]['to'][idx]]['position']
                else:
                    pos2= All[All[ivalue]['to'][idx]]['position']

            cvalue=(abs(pos1[0]-pos2[0])+abs(pos1[1]-pos2[1]))/2
            cvalue_dict.update({ivalue:cvalue})
            if (pos1[0]<pos2[0] and pos1[1]<pos2[1]) or (pos2[0]<pos1[0] and pos2[1]<pos1[1]):
                minx=min(pos1[0],pos2[0])
                maxx=max(pos1[0],pos2[0])
                miny=min(pos1[1],pos2[1])
                maxy=max(pos1[1],pos2[1])
                if abs(pos1[0]-pos2[0])<abs(pos1[1]-pos2[1]):
                    position_dict.update({ivalue:{'position1':pos1,'position2':pos2,'minimum_distance':cvalue,'candidate_position':[[str(minx)+' -x',str(miny+cvalue)],[str(maxx)+' +x',str(maxy-cvalue)]]}})
                elif abs(pos1[0]-pos2[0])>abs(pos1[1]-pos2[1]):
                    position_dict.update({ivalue:{'position1':pos1,'position2':pos2,'minimum_distance':cvalue,'candidate_position':[[str(minx+cvalue),str(miny)+' -y'],[str(maxx-cvalue),str(maxy)+' +y']]}})
                else:
                    position_dict.update({ivalue:{'position1':pos1,'position2':pos2,'minimum_distance':cvalue,'candidate_position':[[str(minx)+' -x',str(maxy)+' +y'],[str(maxx)+' +x',str(miny)+' -y']]}})

            elif (pos1[0]<pos2[0] and pos1[1]>pos2[1]) or (pos2[0]<pos1[0] and pos2[1]>pos1[1]):
                minx=min(pos1[0],pos2[0])
                maxx=max(pos1[0],pos2[0])
                miny=min(pos1[1],pos2[1])
                maxy=max(pos1[1],pos2[1])
                if abs(pos1[0]-pos2[0])<abs(pos1[1]-pos2[1]):
                    position_dict.update({ivalue:{'position1':pos1,'position2':pos2,'minimum_distance':cvalue,'candidate_position':[[str(minx)+' -x',str(maxy-cvalue)],[str(maxx)+' +x',str(miny+cvalue)]]}})
                elif abs(pos1[0]-pos2[0])>abs(pos1[1]-pos2[1]):
                    position_dict.update({ivalue:{'position1':pos1,'position2':pos2,'minimum_distance':cvalue,'candidate_position':[[str(maxx-cvalue),str(miny)+' -y'],[str(minx+cvalue),str(maxy)+' +y']]}})
                else:
                    position_dict.update({ivalue:{'position1':pos1,'position2':pos2,'minimum_distance':cvalue,'candidate_position':[[str(minx)+' -x',str(miny)+' -y'],[str(maxx)+' +x',str(maxy)+' +y']]}})

            elif pos1[0]==pos2[0]:
                position_dict.update({ivalue:{'position1':pos1,'position2':pos2,'minimum_distance':cvalue,'candidate_position':[[str(pos1[0])+' -x',str(min(pos1[1],pos2[1])+cvalue)],[str(pos1[0])+' +x',str(min(pos1[1],pos2[1])+cvalue)]]}})
            elif pos1[1]==pos2[1]:
                position_dict.update({ivalue:{'position1':pos1,'position2':pos2,'minimum_distance':cvalue,'candidate_position':[[str(min(pos1[0],pos2[0])+cvalue),str(pos1[1])+' -y'],[str(min(pos1[0],pos2[0])+cvalue),str(pos1[1])+' +y']]}})
    
        elif All[ivalue]['stage'][0]==max_stage and All[ivalue]['direction']=='OUTPUT' and len(All[ivalue]['to'])==1:
            pos1=list()
            pos1= All[All[ivalue]['to'][0]]['position']
            position_dict.update({ivalue:{'position1':pos1,'minimum_distance':float(0),'candidate_position':[[str(pos1[0])+' -x',str(pos1[1])],[str(pos1[0])+' +x',str(pos1[1])],[str(pos1[0]),str(pos1[1])+' -y'],[str(pos1[0]),str(pos1[1])+' +y']]}})

    counts_numbering=len(cvalue_dict)

    list_table=list()
    for idx in range(counts_numbering):
        max_minimum_length_of_cvalue_dict=float()
        whoisking=str()
        pseudo_cvalue_dict=copy.deepcopy(cvalue_dict)
        for ivalue in (pseudo_cvalue_dict):
            if max_minimum_length_of_cvalue_dict<cvalue_dict[ivalue]:
                max_minimum_length_of_cvalue_dict=cvalue_dict[ivalue]
                whoisking=ivalue

        if whoisking=='':
            for ivalue in (pseudo_cvalue_dict):
                list_table.append({ivalue:cvalue_dict[ivalue]})
        else:
            list_table.append({whoisking:cvalue_dict[whoisking]})
            del cvalue_dict[whoisking]


    max_minimum_length=list(list_table[0].values())[0]
    keys_list=list()
    values_list=list()
    for idx in range(len(list_table)):
        keys_list.append(list(list_table[idx].keys())[0])
        values_list.append(list(list_table[idx].values())[0])

    for ivalue in position_dict:
        if position_dict[ivalue]['minimum_distance'] == max_minimum_length:
            All[ivalue].update({'position':[(position_dict[ivalue]['position1'][0]+position_dict[ivalue]['position2'][0])/2,(position_dict[ivalue]['position1'][1]+position_dict[ivalue]['position2'][1])/2]})
            position_dict[ivalue]['candidate_position']=[[(position_dict[ivalue]['position1'][0]+position_dict[ivalue]['position2'][0])/2,(position_dict[ivalue]['position1'][1]+position_dict[ivalue]['position2'][1])/2]]
        else:
            for idx in range(len(position_dict[ivalue]['candidate_position'])):
                for jdx in range(len(position_dict[ivalue]['candidate_position'][idx])):
                    if ('x' in position_dict[ivalue]['candidate_position'][idx][jdx] and 'y' not in position_dict[ivalue]['candidate_position'][idx][jdx]) or ('x' not in position_dict[ivalue]['candidate_position'][idx][jdx] and 'y' in position_dict[ivalue]['candidate_position'][idx][jdx]):
                        if '-' in position_dict[ivalue]['candidate_position'][idx][jdx]:
                            position_dict[ivalue]['candidate_position'][idx][jdx]=float(position_dict[ivalue]['candidate_position'][idx][jdx].split(' ')[0])-(max_minimum_length-position_dict[ivalue]['minimum_distance'])
                        else:
                            position_dict[ivalue]['candidate_position'][idx][jdx]=float(position_dict[ivalue]['candidate_position'][idx][jdx].split(' ')[0])+(max_minimum_length-position_dict[ivalue]['minimum_distance'])
                    else:
                        position_dict[ivalue]['candidate_position'][idx][jdx]=float(position_dict[ivalue]['candidate_position'][idx][jdx])



        willdel=list()
        candidate_int=int(len(position_dict[ivalue]['candidate_position']))
        for jdx in range(len(position_dict[ivalue]['candidate_position'])):
            if position_dict[ivalue]['candidate_position'][jdx][0]<dieArea[0][0] or position_dict[ivalue]['candidate_position'][jdx][1]<dieArea[0][1] or position_dict[ivalue]['candidate_position'][jdx][0]>dieArea[1][0] or position_dict[ivalue]['candidate_position'][jdx][1]>dieArea[1][1]:
                willdel.append(position_dict[ivalue]['candidate_position'][jdx])

            A_position=list()
            A_position=get_input_position(position_dict[ivalue]['candidate_position'][jdx],temp_macro)
            if A_position[0]<dieArea[0][0] or A_position[1]<dieArea[0][1] or A_position[0]>dieArea[1][0] or A_position[1]>dieArea[1][1]:
                willdel.append(position_dict[ivalue]['candidate_position'][jdx])
        
        result=list()
        for jvalue in willdel:
            if jvalue not in result:
                result.append(jvalue)
        willdel=result

        restore_candidate=list()
        for jdx in range(len(willdel)):
            if willdel[jdx] in position_dict[ivalue]['candidate_position']:
                if len(willdel)==candidate_int:
                    restore_candidate.append(willdel[jdx])
                position_dict[ivalue]['candidate_position'].remove(willdel[jdx])




#####################################################################################

        if len(position_dict[ivalue]['candidate_position'])==0:
            print('Error(Midpoints are not in die_area): '+ivalue)

            if len(restore_candidate) ==2:
                pos1=position_dict[ivalue]['position1']
                pos2=position_dict[ivalue]['position2']

                whereis_problem=int()
                for jdx in range(len(list_table)):
                    if keys_list[jdx]==ivalue:
                        whereis_problem=jdx


                sero=int()
                garo=int()
                if (pos1[1]<restore_candidate[0][1] and pos2[1]<restore_candidate[0][1]) or (pos1[1]<restore_candidate[1][1] and pos2[1]<restore_candidate[1][1]):
                    sero=1

                for jdx in range(len(list_table)):
                    
                    if jdx==whereis_problem: ###################### 만약 ivalue 까지 point를 잡지 못하면, candidate_position을 해당 ivalue의 midpoint로 잡고 break
                        position_dict[ivalue]['candidate_position']=[[(position_dict[ivalue]['position1'][0]+position_dict[ivalue]['position2'][0])/2,(position_dict[ivalue]['position1'][1]+position_dict[ivalue]['position2'][1])/2]]
                        break

                    else:                    ####################################### position_dict[ivalue]를 확인함과 동시에, restore_candidate를 비교해가면서 die_Area 확인: 함수 만들기
                        temp_position=copy.deepcopy(restore_candidate)
                        if sero==1: ####################################### jdx번째의 길이를 적용했을 때, candidate_position을 하나라도 잡을 수 있으면 break: 함수 만들기
                            
                            if temp_position[0][1]>temp_position[1][1]:
                                temp_position[0][1]=max(pos1[1],pos2[1])
                                temp_position[1][1]=min(pos1[1],pos2[1])
                                temp_position[0][1]=temp_position[0][1]+values_list[jdx]-position_dict[ivalue]['minimum_distance']
                                temp_position[1][1]=temp_position[1][1]-values_list[jdx]+position_dict[ivalue]['minimum_distance']
                            else:
                                temp_position[1][1]=max(pos1[1],pos2[1])
                                temp_position[0][1]=min(pos1[1],pos2[1])
                                temp_position[1][1]=temp_position[1][1]+values_list[jdx]-position_dict[ivalue]['minimum_distance']
                                temp_position[0][1]=temp_position[0][1]-values_list[jdx]+position_dict[ivalue]['minimum_distance']
                        else:
                            if temp_position[0][0]>temp_position[1][0]:
                                temp_position[0][0]=max(pos1[0],pos2[0])
                                temp_position[1][0]=min(pos1[0],pos2[0])
                                temp_position[0][0]=temp_position[0][0]+values_list[jdx]-position_dict[ivalue]['minimum_distance']
                                temp_position[1][0]=temp_position[1][0]-values_list[jdx]+position_dict[ivalue]['minimum_distance']
                            else:
                                temp_position[1][0]=max(pos1[0],pos2[0])
                                temp_position[0][0]=min(pos1[0],pos2[0])
                                temp_position[1][0]=temp_position[0][0]+values_list[jdx]-position_dict[ivalue]['minimum_distance']
                                temp_position[0][0]=temp_position[1][0]-values_list[jdx]+position_dict[ivalue]['minimum_distance']

                        willdelindex=list()
                        for gdx in range(2):
                            A_position=get_input_position(temp_position[gdx],temp_macro)
                            if temp_position[gdx][0]<dieArea[0][0] or temp_position[gdx][1]<dieArea[0][1] or temp_position[gdx][0]>dieArea[1][0] or temp_position[gdx][1]>dieArea[1][1]:
                                willdelindex.append(gdx)
                            elif A_position[0]<dieArea[0][0] or A_position[1]<dieArea[0][1] or A_position[0]>dieArea[1][0] or A_position[1]>dieArea[1][1]:
                                willdelindex.append(gdx)
                        willdelindex.reverse()
                        for gdx in range(len(willdelindex)):
                            del temp_position[willdelindex[gdx]]

                        if len(temp_position) != 0:
                            position_dict[ivalue]['candidate_position']=temp_position
                            break


        del position_dict[ivalue]['minimum_distance']
        del position_dict[ivalue]['position1']
        if 'position2' in position_dict[ivalue]:
            del position_dict[ivalue]['position2']

        elif len(position_dict[ivalue]['candidate_position'])==1:
            All[ivalue].update({'position':position_dict[ivalue]['candidate_position'][0]})

    for ivalue in All:
        if All[ivalue]['stage'][0]==max_stage and All[ivalue]['direction']=='OUTPUT':
            if len(All[All[All[ivalue]['from'][0]]['from'][0]]['to']) ==2:
                counting_position=int()
                if 'position' in All[ivalue]:

                    whohas_position=str()
                    with_position=list()
                    for jdx in range(len(All[All[All[ivalue]['from'][0]]['from'][0]]['to'])):
                        with_position.append(All[All[All[All[ivalue]['from'][0]]['from'][0]]['to'][jdx]]['to'][0])
                        if 'position' in All[All[All[All[All[ivalue]['from'][0]]['from'][0]]['to'][jdx]]['to'][0]]:
                            counting_position=counting_position+1
                            whohas_position=All[All[All[All[ivalue]['from'][0]]['from'][0]]['to'][jdx]]['to'][0]


                    if counting_position==2:
                        continue

                    with_position.remove(whohas_position)
                    first_position=list()
                    second_position=list()

                    first_position=[All[whohas_position]['position']]
                    second_position=position_dict[with_position[0]]['candidate_position']
                    All[with_position[0]].update({'position':get_hpwl_by_two_positions(first_position,second_position)[1]})


                else:
                    whohas_position=str()
                    with_position=list()
                    ifcont=str()
                    for jdx in range(len(All[All[All[ivalue]['from'][0]]['from'][0]]['to'])):
                        with_position.append(All[All[All[All[ivalue]['from'][0]]['from'][0]]['to'][jdx]]['to'][0])
                        if 'position' in All[All[All[All[All[ivalue]['from'][0]]['from'][0]]['to'][jdx]]['to'][0]]:
                            ifcont='con'
                    if ifcont=='con':
                        continue

                    first_position=position_dict[with_position[0]]['candidate_position']
                    second_position=position_dict[with_position[1]]['candidate_position']
                    All[with_position[0]].update({'position':get_hpwl_by_two_positions(first_position,second_position)[0]})
                    All[with_position[1]].update({'position':get_hpwl_by_two_positions(first_position,second_position)[1]})
    
    return [All,position_dict]











def get_hpwl_by_two_positions(position_list1,position_list2):
    hpwl_info=dict()
    max_hpwl_length=float()
    max_hpwl_area=float()
    for idx in range(len(position_list1)):
        for kdx in range(len(position_list2)):
            aaa=max(position_list1[idx][0],position_list2[kdx][0])-min(position_list1[idx][0],position_list2[kdx][0])
            bbb=max(position_list1[idx][1],position_list2[kdx][1])-min(position_list1[idx][1],position_list2[kdx][1])
            hpwl_length=aaa+bbb
            hpwl_area=aaa*bbb
            hpwl_info.update({str(idx)+'-'+str(kdx):{'hpwl_length':hpwl_length,'hpwl_area':hpwl_area}})
            if max_hpwl_length<hpwl_length:
                max_hpwl_length=hpwl_length
            if max_hpwl_area<hpwl_area:
                max_hpwl_area=hpwl_area

    min_hpwl_length=max_hpwl_length
    min_hpwl_area=max_hpwl_area

    for ivalue in hpwl_info:
        if min_hpwl_length>hpwl_info[ivalue]['hpwl_length']:
            min_hpwl_length=hpwl_info[ivalue]['hpwl_length']
    
    temp_dict=copy.deepcopy(hpwl_info)
    for ivalue in temp_dict:
        if min_hpwl_length<hpwl_info[ivalue]['hpwl_length']:
            del hpwl_info[ivalue]

    final_positions=list()
    if len(hpwl_info)==1:
        for ivalue in hpwl_info:
            final_positions=[position_list1[int(ivalue.split('-')[0])],position_list2[int(ivalue.split('-')[1])]]
            return final_positions

    else:
        for ivalue in hpwl_info:
            if min_hpwl_area>hpwl_info[ivalue]['hpwl_area']:
                min_hpwl_area=hpwl_info[ivalue]['hpwl_area']

        temp_dict=copy.deepcopy(hpwl_info)

        list_of_name=list()
        for ivalue in temp_dict:
            if min_hpwl_length<hpwl_info[ivalue]['hpwl_length']:
                del hpwl_info[ivalue]
            else:
                list_of_name.append(ivalue)

        if len(hpwl_info)==1:
            for ivalue in hpwl_info:
                final_positions=[position_list1[int(ivalue.split('-')[0])],position_list2[int(ivalue.split('-')[1])]]
                return final_positions
        
        else:
            max_ivalue_1=int()

            for ivalue in list_of_name:
                if max_ivalue_1<int(ivalue.split('-')[0]):
                    max_ivalue_1=int(ivalue.split('-')[0])
            
            temp_list=copy.deepcopy(list_of_name)

            for ivalue in temp_list:
                if max_ivalue_1>int(ivalue.split('-')[0]):
                    list_of_name.remove(ivalue)
            
            if len(list_of_name)==1:
                final_positions=[position_list1[int(list_of_name[0].split('-')[0])],position_list2[int(list_of_name[0].split('-')[1])]]
                return final_positions

            else:
                max_ivalue_2=int()
                for ivalue in list_of_name:
                    if max_ivalue_2<int(ivalue.split('-')[1]):
                        max_ivalue_2=int(ivalue.split('-')[1])

                temp_list=copy.deepcopy(list_of_name)

                for ivalue in temp_list:
                    if max_ivalue_2>int(ivalue.split('-')[1]):
                        list_of_name.remove(ivalue)

                final_positions=[position_list1[int(list_of_name[0].split('-')[0])],position_list2[int(list_of_name[0].split('-')[1])]]
                return final_positions




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






def get_clk_pin_position(All,unit):
    listlist=list()
    listlist=[All['PIN clk']['position'][0]/unit,All['PIN clk']['position'][1]/unit]
    return listlist






def get_input_position(listlist,temp_macro):
    A_positionlist=list()
    if temp_macro=='CLKBUF_X1':
        A_positionlist=[listlist[0]-0.00017,listlist[1]-0.0004125]
    return A_positionlist






def get_type_of_CK_max_minus_two(All,die_Area,temp_macro):

    max_stage=int()

    for ivalue in All:
        if All[ivalue]['stage'][0]>max_stage:
            max_stage=All[ivalue]['stage'][0]


    list_4=list()
    list_5=list()
    for ivalue in All:
        if All[ivalue]['stage'][0]==max_stage-2 and All[ivalue]['direction']=='OUTPUT':
            first_OUTPUT11=All[All[ivalue]['to'][0]]['to'][0]
            second_OUTPUT11=All[All[ivalue]['to'][1]]['to'][0]
            if (len(All[first_OUTPUT11]['to'])==2 and len(All[second_OUTPUT11]['to'])==1) or (len(All[first_OUTPUT11]['to'])==1 and len(All[second_OUTPUT11]['to'])==2):
                list_5.append(ivalue)
            else:
                list_4.append(ivalue)


    list_4_count=int()
    who_has_midpoint=str()
    who_is_11OUTPUT=str()
    who_is_10OUTPUT=str()

    position_dict_for_4children=dict()
    for ivalue in list_4:
        
        first_OUTPUT11=All[All[ivalue]['to'][0]]['to'][0]
        second_OUTPUT11=All[All[ivalue]['to'][1]]['to'][0]
        
        first_OUTPUT12=All[All[first_OUTPUT11]['to'][0]]['to'][0]
        fO12=first_OUTPUT12
        second_OUTPUT12=All[All[second_OUTPUT11]['to'][0]]['to'][0]
        sO12=second_OUTPUT12

        fIfO12=All[first_OUTPUT12]['to'][0]
        fIsO12=All[first_OUTPUT12]['to'][1]
        sIfO12=All[second_OUTPUT12]['to'][0]
        sIsO12=All[second_OUTPUT12]['to'][1]

        position_dict_for_4children.update({ivalue:{first_OUTPUT12:[All[fIfO12]['position'],All[fIsO12]['position']],first_OUTPUT12+'_position':All[first_OUTPUT12]['position'],second_OUTPUT12:[All[sIfO12]['position'],All[sIsO12]['position']],second_OUTPUT12+'_position':All[second_OUTPUT12]['position']}})
        
        if (All[fO12]['position'][0]>All[fIfO12]['position'][0] and All[fO12]['position'][0]<All[fIsO12]['position'][0]) or (All[fO12]['position'][0]<All[fIfO12]['position'][0] and All[fO12]['position'][0]>All[fIsO12]['position'][0]):
            if (All[fO12]['position'][1]>All[fIfO12]['position'][1] and All[fO12]['position'][1]<All[fIsO12]['position'][1]) or (All[fO12]['position'][1]<All[fIfO12]['position'][1] and All[fO12]['position'][1]>All[fIsO12]['position'][1]):
                list_4_count=1
                who_has_midpoint=first_OUTPUT12
                who_is_11OUTPUT=first_OUTPUT11
                who_is_10OUTPUT=ivalue

        if (All[sO12]['position'][0]>All[sIfO12]['position'][0] and All[sO12]['position'][0]<All[sIsO12]['position'][0]) or (All[sO12]['position'][0]<All[sIfO12]['position'][0] and All[sO12]['position'][0]>All[sIsO12]['position'][0]):
            if (All[sO12]['position'][1]>All[sIfO12]['position'][1] and All[sO12]['position'][1]<All[sIsO12]['position'][1]) or (All[sO12]['position'][1]<All[sIfO12]['position'][1] and All[sO12]['position'][1]>All[sIsO12]['position'][1]):
                list_4_count=1
                who_has_midpoint=second_OUTPUT12
                who_is_11OUTPUT=second_OUTPUT11
                who_is_10OUTPUT=ivalue

    list_5_count=int()
    position_dict_for_5children=dict()
    for ivalue in list_5:
        candidate1=str()
        candidate2=str()
        first_OUTPUT11=All[All[ivalue]['to'][0]]['to'][0]
        second_OUTPUT11=All[All[ivalue]['to'][1]]['to'][0]


        single_OUTPUT12=str()
        not_single_withsingle_OUTPUT12=str()
        not_single_withoutsingle_OUTPUT12=str()

        
        if len(All[first_OUTPUT11]['to'])==2:
            candidate1=first_OUTPUT11
            candidate2=second_OUTPUT11
            for kdx in range(len(All[first_OUTPUT11]['to'])):
                temp_INPUT11=All[first_OUTPUT11]['to'][kdx]
                if len(All[All[temp_INPUT11]['to'][0]]['to'])==1:
                    single_OUTPUT12=All[temp_INPUT11]['to'][0]
                else:
                    not_single_withsingle_OUTPUT12=All[temp_INPUT11]['to'][0]
            not_single_withoutsingle_OUTPUT12=All[All[second_OUTPUT11]['to'][0]]['to'][0]


        elif len(All[second_OUTPUT11]['to'])==2:
            candidate1=second_OUTPUT11
            candidate2=first_OUTPUT11
            for kdx in range(len(All[second_OUTPUT11]['to'])):
                temp_INPUT11=All[second_OUTPUT11]['to'][kdx]
                if len(All[All[temp_INPUT11]['to'][0]]['to'])==1:
                    single_OUTPUT12=All[temp_INPUT11]['to'][0]
                else:
                    not_single_withsingle_OUTPUT12=All[temp_INPUT11]['to'][0]
            not_single_withoutsingle_OUTPUT12=All[All[first_OUTPUT11]['to'][0]]['to'][0]

        fIfO12=All[not_single_withsingle_OUTPUT12]['to'][0]
        fIsO12=All[not_single_withsingle_OUTPUT12]['to'][1]
        sIfO12=All[not_single_withoutsingle_OUTPUT12]['to'][0]
        sIsO12=All[not_single_withoutsingle_OUTPUT12]['to'][1]

        position_dict_for_5children.update({ivalue:{not_single_withsingle_OUTPUT12:[All[fIfO12]['position'],All[fIsO12]['position']],not_single_withsingle_OUTPUT12+'_position':All[not_single_withsingle_OUTPUT12]['position'],not_single_withoutsingle_OUTPUT12:[All[sIfO12]['position'],All[sIsO12]['position']],not_single_withoutsingle_OUTPUT12+'_position':All[not_single_withoutsingle_OUTPUT12]['position'],single_OUTPUT12:[All[All[single_OUTPUT12]['to'][0]]['position']],single_OUTPUT12+'_position':All[single_OUTPUT12]['position']}})

        if (All[not_single_withsingle_OUTPUT12]['position'][0]>min(All[fIfO12]['position'][0],All[fIsO12]['position'][0]) and All[not_single_withsingle_OUTPUT12]['position'][0]<max(All[fIfO12]['position'][0],All[fIsO12]['position'][0])):
            if (All[not_single_withsingle_OUTPUT12]['position'][1]>min(All[fIfO12]['position'][1],All[fIsO12]['position'][1]) and All[not_single_withsingle_OUTPUT12]['position'][1]<max(All[fIfO12]['position'][1],All[fIsO12]['position'][1])):
                list_5_count=1
                who_has_midpoint=not_single_withsingle_OUTPUT12
                who_is_11OUTPUT=candidate1
                who_is_10OUTPUT=ivalue

        if (All[not_single_withoutsingle_OUTPUT12]['position'][0]>min(All[sIfO12]['position'][0], All[sIsO12]['position'][0]) and All[not_single_withoutsingle_OUTPUT12]['position'][0]<max(All[sIfO12]['position'][0],All[sIsO12]['position'][0])):
            if (All[not_single_withoutsingle_OUTPUT12]['position'][1]>min(All[sIfO12]['position'][1], All[sIsO12]['position'][1]) and All[not_single_withoutsingle_OUTPUT12]['position'][1]<max(All[sIfO12]['position'][1],All[sIsO12]['position'][1])):
                list_5_count=1
                who_has_midpoint=not_single_withoutsingle_OUTPUT12
                who_is_11OUTPUT=candidate2
                who_is_10OUTPUT=ivalue
        
    position_dict_for_4children_candidates=dict()

    for ivalue in position_dict_for_4children:
        position_dict_for_4children_candidates.update({ivalue:{}})

        for kvalue in position_dict_for_4children[ivalue]:
            if '_position' not in kvalue:
                position_dict_for_4children_candidates[ivalue].update({kvalue:{'position':position_dict_for_4children[ivalue][kvalue+'_position'],'target_position':position_dict_for_4children[ivalue][kvalue]}})
    
    copy_of_4=copy.deepcopy(position_dict_for_4children_candidates)
    for ivalue in copy_of_4:
        all_position_group=list()
        for kvalue in copy_of_4[ivalue]:
            position_dict_for_4children_candidates[ivalue][kvalue].update({'type':'not_single'})
            all_position_group.append(position_dict_for_4children_candidates[ivalue][kvalue]['target_position'][0])
            all_position_group.append(position_dict_for_4children_candidates[ivalue][kvalue]['target_position'][1])
            
        
        
        for kvalue in copy_of_4[ivalue]:
            checking_position_group=copy.deepcopy(all_position_group)
            checking_position_group.remove(position_dict_for_4children_candidates[ivalue][kvalue]['target_position'][0])
            checking_position_group.remove(position_dict_for_4children_candidates[ivalue][kvalue]['target_position'][1])
            position_dict_for_4children_candidates[ivalue][kvalue]['target_position'].append(checking_position_group[0])
            position_dict_for_4children_candidates[ivalue][kvalue]['target_position'].append(checking_position_group[1])

    position_dict_for_5children_candidates=dict()

    for ivalue in position_dict_for_5children:
        position_dict_for_5children_candidates.update({ivalue:{}})

        for kvalue in position_dict_for_5children[ivalue]:
            if '_position' not in kvalue:
                position_dict_for_5children_candidates[ivalue].update({kvalue:{'position':position_dict_for_5children[ivalue][kvalue+'_position'],'target_position':position_dict_for_5children[ivalue][kvalue]}})
    

    copy_of_5=copy.deepcopy(position_dict_for_5children_candidates)
    for ivalue in copy_of_5:
        all_position_group=list()
        for kvalue in copy_of_5[ivalue]:
            
            if len(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'])==1:
                position_dict_for_5children_candidates[ivalue][kvalue].update({'type':'single'})
                all_position_group.append(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][0])

            elif len(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'])==2:

                position_dict_for_5children_candidates[ivalue][kvalue].update({'type':'not_single'})
                all_position_group.append(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][0])
                all_position_group.append(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][1])


        

        for kvalue in copy_of_5[ivalue]:
            proto_position=copy.deepcopy(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'])

            checking_position_group=copy.deepcopy(all_position_group)

            if len(proto_position)==1:
                checking_position_group.remove(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][0])
            elif len(proto_position)==2:
                checking_position_group.remove(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][1])
                checking_position_group.remove(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][0])


            for jjdx in range(len(checking_position_group)):
                position_dict_for_5children_candidates[ivalue][kvalue]['target_position'].append(checking_position_group[jjdx])

    


    ##print(json.dumps(position_dict_for_4children_candidates,indent=4))
    ttdx=int()

    max_minimum_wire_length=float()
    whohas_max_minimum_12OUTPUT=str()
    whohas_max_minimum_10OUTPUT=str()

    for ivalue in position_dict_for_5children_candidates:
        ttdx=ttdx+1
        ##die_Area
        for kvalue in position_dict_for_5children_candidates[ivalue]:
            if kvalue==who_has_midpoint:
                position_dict_for_5children_candidates[ivalue][kvalue]['position']=get_point_for_midpoint(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][0:2])

            from_max_output_position=position_dict_for_5children_candidates[ivalue][kvalue]['position']
            origin_target1=list()
            origin_target2=list()

            if position_dict_for_5children_candidates[ivalue][kvalue]['type']=='single':
                origin_target1=position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][0]
                origin_target2=position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][0]
            else:
                origin_target1=position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][0]
                origin_target2=position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][1]
                
            
            group_of_list=get_new_position_from_max_stage(from_max_output_position,origin_target1,origin_target2)


            if len(group_of_list[2])==0:
                del group_of_list[2]
            if len(group_of_list[1])==0:
                del group_of_list[1]
            if len(group_of_list[0])==0:
                del group_of_list[0]

            temp_group_of_list=list()
            for igdx in range(len(group_of_list)):
                if group_of_list[igdx]!=[]:
                    temp_x_coord=float()
                    temp_y_coord=float()
                    if type(group_of_list[igdx][0])==type(''):
                        temp_x_coord=float(group_of_list[igdx][0].split(' ')[0])
                        temp_group_of_list.append([temp_x_coord,group_of_list[igdx][1]])
                    
                    elif type(group_of_list[igdx][1])==type(''):
                        temp_y_coord=float(group_of_list[igdx][1].split(' ')[0])
                        temp_group_of_list.append([group_of_list[igdx][0],temp_y_coord])


            position_dict_for_5children_candidates[ivalue][kvalue].update({'group_of_list':group_of_list,'zero_group_of_list':temp_group_of_list})
            position_dict_for_5children_candidates[ivalue][kvalue].update({'star_length':[]})

            maximum_wire_length_among_us=float()

            for igdx in range(len(position_dict_for_5children_candidates[ivalue][kvalue]['zero_group_of_list'])):
                listlist=list()
                listlist.append(position_dict_for_5children_candidates[ivalue][kvalue]['zero_group_of_list'][igdx])
                
                for kigdx in range(len(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'])):
                    listlist.append(position_dict_for_5children_candidates[ivalue][kvalue]['target_position'][kigdx])
                position_dict_for_5children_candidates[ivalue][kvalue]['star_length'].append(get_new_wirelength_star(listlist))
                if maximum_wire_length_among_us<get_new_wirelength_star(listlist):
                    maximum_wire_length_among_us=get_new_wirelength_star(listlist)

            where_minimum=list()
            minimum_wire_length_among_us=maximum_wire_length_among_us
            for igdx in range(len(position_dict_for_5children_candidates[ivalue][kvalue]['star_length'])):
                if minimum_wire_length_among_us>position_dict_for_5children_candidates[ivalue][kvalue]['star_length'][igdx]:
                    minimum_wire_length_among_us=position_dict_for_5children_candidates[ivalue][kvalue]['star_length'][igdx]
                
                    where_minimum=[igdx]
                elif minimum_wire_length_among_us==position_dict_for_5children_candidates[ivalue][kvalue]['star_length'][igdx]:
                    where_minimum.append(igdx)

            position_dict_for_5children_candidates[ivalue][kvalue].update({'minimum_wire_length':minimum_wire_length_among_us,'where_is_minimum':where_minimum})
        
        for kvalue in position_dict_for_5children_candidates[ivalue]:
            if max_minimum_wire_length<position_dict_for_5children_candidates[ivalue][kvalue]['minimum_wire_length']:
                max_minimum_wire_length=position_dict_for_5children_candidates[ivalue][kvalue]['minimum_wire_length']
                whohas_max_minimum_12OUTPUT=kvalue
                whohas_max_minimum_10OUTPUT=ivalue



    ttdx=int()

    for ivalue in position_dict_for_4children_candidates:
        ttdx=ttdx+1

        for kvalue in position_dict_for_4children_candidates[ivalue]:
            if kvalue==who_has_midpoint:
                position_dict_for_4children_candidates[ivalue][kvalue]['position']=get_point_for_midpoint(position_dict_for_4children_candidates[ivalue][kvalue]['target_position'][0:2])

            from_max_output_position=position_dict_for_4children_candidates[ivalue][kvalue]['position']
            origin_target1=list()
            origin_target2=list()

            if position_dict_for_4children_candidates[ivalue][kvalue]['type']=='single':
                origin_target1=position_dict_for_4children_candidates[ivalue][kvalue]['target_position'][0]
                origin_target2=position_dict_for_4children_candidates[ivalue][kvalue]['target_position'][0]
            else:
                origin_target1=position_dict_for_4children_candidates[ivalue][kvalue]['target_position'][0]
                origin_target2=position_dict_for_4children_candidates[ivalue][kvalue]['target_position'][1]
            

            group_of_list=get_new_position_from_max_stage(from_max_output_position,origin_target1,origin_target2)

            if len(group_of_list[2])==0:
                del group_of_list[2]
            if len(group_of_list[1])==0:
                del group_of_list[1]
            if len(group_of_list[0])==0:
                del group_of_list[0]

            temp_group_of_list=list()
            for igdx in range(len(group_of_list)):
                if group_of_list[igdx]!=[]:
                    temp_x_coord=float()
                    temp_y_coord=float()
                    if type(group_of_list[igdx][0])==type(''):
                        temp_x_coord=float(group_of_list[igdx][0].split(' ')[0])
                        temp_group_of_list.append([temp_x_coord,group_of_list[igdx][1]])
                    
                    elif type(group_of_list[igdx][1])==type(''):
                        temp_y_coord=float(group_of_list[igdx][1].split(' ')[0])
                        temp_group_of_list.append([group_of_list[igdx][0],temp_y_coord])


            position_dict_for_4children_candidates[ivalue][kvalue].update({'group_of_list':group_of_list,'zero_group_of_list':temp_group_of_list})
            position_dict_for_4children_candidates[ivalue][kvalue].update({'star_length':[]})


            maximum_wire_length_among_us=float()
            for igdx in range(len(position_dict_for_4children_candidates[ivalue][kvalue]['zero_group_of_list'])):
                listlist=list()
                listlist.append(position_dict_for_4children_candidates[ivalue][kvalue]['zero_group_of_list'][igdx])
                
                for kigdx in range(len(position_dict_for_4children_candidates[ivalue][kvalue]['target_position'])):
                    listlist.append(position_dict_for_4children_candidates[ivalue][kvalue]['target_position'][kigdx])
                position_dict_for_4children_candidates[ivalue][kvalue]['star_length'].append(get_new_wirelength_star(listlist))
                if maximum_wire_length_among_us<get_new_wirelength_star(listlist):
                    maximum_wire_length_among_us=get_new_wirelength_star(listlist)

            where_minimum=list()
            minimum_wire_length_among_us=maximum_wire_length_among_us
            for igdx in range(len(position_dict_for_4children_candidates[ivalue][kvalue]['star_length'])):
                if minimum_wire_length_among_us>position_dict_for_4children_candidates[ivalue][kvalue]['star_length'][igdx]:
                    minimum_wire_length_among_us=position_dict_for_4children_candidates[ivalue][kvalue]['star_length'][igdx]
                
                    where_minimum=[igdx]
                elif minimum_wire_length_among_us==position_dict_for_4children_candidates[ivalue][kvalue]['star_length'][igdx]:
                    where_minimum.append(igdx)

            position_dict_for_4children_candidates[ivalue][kvalue].update({'minimum_wire_length':minimum_wire_length_among_us,'where_is_minimum':where_minimum})

        for kvalue in position_dict_for_4children_candidates[ivalue]:
            if max_minimum_wire_length<position_dict_for_4children_candidates[ivalue][kvalue]['minimum_wire_length']:
                max_minimum_wire_length=position_dict_for_4children_candidates[ivalue][kvalue]['minimum_wire_length']
                whohas_max_minimum_12OUTPUT=kvalue
                whohas_max_minimum_10OUTPUT=ivalue


    max_info=dict()
    for ivalue in position_dict_for_5children_candidates:
        if ivalue==whohas_max_minimum_10OUTPUT:
            max_info=position_dict_for_5children_candidates[ivalue][whohas_max_minimum_12OUTPUT]
            break

    for ivalue in position_dict_for_4children_candidates:
        if ivalue==whohas_max_minimum_10OUTPUT:
            max_info=position_dict_for_4children_candidates[ivalue][whohas_max_minimum_12OUTPUT]
            
            break

    new_5_candidate=dict()
    new_4_candidate=dict()
    ttt=int()
    for ivalue in position_dict_for_4children_candidates:
        targets=list()
        ttt=ttt+1
        for kvalue in position_dict_for_4children_candidates[ivalue]:
            targets=position_dict_for_4children_candidates[ivalue][kvalue]['target_position']
            break

        new_position=list()
        x_pos=float()
        y_pos=float()
        for jdx in range(4):
            x_pos=x_pos+targets[jdx][0]
            y_pos=y_pos+targets[jdx][1]
        new_position=[x_pos/4,y_pos/4]
        '''if targets[0]==targets[1]:
            print(ivalue)
            print(kvalue)
            print(position_dict_for_4children_candidates[ivalue][kvalue])
            print()'''
        '''if ttt==2:
            new_position=get_new_position_from_elements_4(targets)
            new_position=[(targets[1][0]+targets[0][0])/2,((targets[0][1]+targets[2][1])/2)]'''
        
        checking_wire_length_star=float()
        groups=list()
        groups.append(new_position)
        for jdx in range(4):
            groups.append(targets[jdx])
        checking_wire_length_star=get_new_wirelength_star(groups)
        
        '''if ttt==2:
            print(checking_wire_length_star)
            print('#############################')
            for kvalue in position_dict_for_4children_candidates[ivalue]:
                print(position_dict_for_4children_candidates[ivalue][kvalue]['minimum_wire_length'])
            print(targets)
            print(new_position)
            print()'''


    return 0






def get_new_position_from_elements_4(elements):
    target1=elements[0]
    target2=elements[1]
    target3=elements[2]
    target4=elements[3]
    new_group=list()

    if target1==target2 and target2==target3 and target3==target4:
        new_group=[{'minimum_wire_length':0},\
            [[str(target1),str(target1)],[str(target1),str(target1)],'dot']]

    elif target1==target2 or target3==target4:
        if target1[0]==target3[0]:
            new_group=[{'minimum_wire_length':max(target1[1],target3[1])-min(target1[1],target3[1])},\
            [[str(target1[0]),str(min(target1[1],target3[1]))],[str(target1[0]),str(max(target1[1],target3[1]))],'vertical_line']]

        elif target1[1]==target3[1]:
            new_group=[{'minimum_wire_length':max(target1[0],target3[0])-min(target1[0],target3[0])},\
            [[str(min(target1[0],target3[0])),str(target1[1])],[str(max(target1[0],target3[0])),str(target1[1])],'horizontal_line']]

        else:
            midpoint=[(max(target1[0],target3[0])+min(target1[0],target3[0]))/2,(max(target1[1],target3[1])+min(target1[1],target3[1]))/2]
            if (target1[0]<target3[0] and target1[1]<target3[1]) or (target3[0]<target1[0] and target3[1]<target1[1]):
                if (midpoint[0]-min(target1[0],target3[0]))>=(max(target1[1],target3[1])-midpoint[1]):
                    minimum_distance=max(target1[1],target3[1])-midpoint[1]
                    new_group=[{'minimum_wire_length':max(target1[0],target3[0])-min(target1[0],target3[0])+max(target1[1],target3[1])-min(target1[1],target3[1])},\
                    [[str(midpoint[0]-minimum_distance),str(midpoint[1]+minimum_distance)],[str(midpoint[0]+minimum_distance),str(midpoint[1]-minimum_distance)],'negative_diagonal_line']]

                else:
                    minimum_distance=max(target1[0],target3[0])-midpoint[0]
                    new_group=[{'minimum_wire_length':max(target1[0],target3[0])-min(target1[0],target3[0])+max(target1[1],target3[1])-min(target1[1],target3[1])},\
                    [[str(midpoint[0]-minimum_distance),str(midpoint[1]+minimum_distance)],[str(midpoint[0]+minimum_distance),str(midpoint[1]-minimum_distance)],'negative_diagonal_line']]
    
            
                
    return 0









def get_point_for_midpoint(two_points):
    point1=two_points[0]
    point2=two_points[1]
    new_position=list()

    if point1[0]==point2[0]:
        new_position=[point1[0],(point1[1]+point2[1])/2]

    elif point1[1]==point2[1]:
        new_position=[(point1[0]+point2[0])/2,point1[0]]



    else:
        min_x=min(point2[0],point1[0])
        max_x=max(point2[0],point1[0])
        min_y=min(point2[1],point1[1])
        max_y=max(point2[1],point1[1])

        cvalue=((max_x-min_x)+(max_y-min_y))/2
        if (point1[0]<point2[0] and point1[1]<point2[1]) or (point2[0]<point1[0] and point2[1]<point1[1]):
            if (max_x-min_x)<(max_y-min_y):
                new_position=[min_x,min_y+cvalue]
            else:
                new_position=[max_x-cvalue,max_y]
        else:
            if (max_x-min_x)<(max_y-min_y):
                new_position=[min_x,max_y-cvalue]
            else:
                new_position=[min_x+cvalue,max_y]

    return new_position






def get_new_position_from_max_stage(major_position,position1,position2):
    temp_position=list()
    if position1==position2:
        minor_position2=[str(position1[0])+' -x',position1[1]]
        minor_position3=[str(position1[0])+' +x',position1[1]]
        minor_position1=[position1[0],str(position1[1])+' -y']
        temp_position=[position1[0],str(position1[1])+' +y']

        return [minor_position1,minor_position2,minor_position3,temp_position]


    else:
        if position1[0]==position2[0]:
            minor_position1=[str(position1[0])+' +x',major_position[1]]
            temp_position=[str(position1[0])+' -x',major_position[1]]
            return [minor_position1,[],[],temp_position]

        
        elif position1[1]==position2[1]:

            minor_position1=[major_position[0],str(position1[1])+' +y']
            temp_position=[major_position[0],str(position1[1])+' -y']
            return [minor_position1,[],[],temp_position]
        

        else:
            if major_position[0]>min(position1[0],position2[0]) and major_position[0]<max(position1[0],position2[0]):


                x_coord=max(position1[0],position2[0])-(major_position[0]-min(position1[0],position2[0]))

                if major_position[1]>=max(position1[1],position2[1]):
                    y_coord=str(min(position1[1],position2[1]))+' -y'
                    minor_position1=[x_coord,y_coord]
                    temp_position=[major_position[0],str(major_position[1])+' +y']
                    return [minor_position1,[],[],temp_position]

                else:
                    y_coord=str(max(position1[1],position2[1]))+' +y'
                    minor_position1=[x_coord,y_coord]
                    temp_position=[major_position[0],str(major_position[1])+' -y']
                    return [minor_position1,[],[],temp_position]
            
            else:
                y_coord=max(position1[1],position2[1])-(major_position[1]-min(position1[1],position2[1]))

                if major_position[0]>=max(position1[0],position2[0]):
                    x_coord=str(min(position1[0],position2[0]))+' -x'
                    minor_position1=[x_coord,y_coord]
                    temp_position=[str(major_position[0])+' -x',major_position[1]]
                    return [minor_position1,[],[],temp_position]
                
                else:
                    x_coord=str(max(position1[0],position2[0]))+' -x'
                    minor_position1=[x_coord,y_coord]
                    temp_position=[str(major_position[0])+' +x',major_position[1]]
                    return [minor_position1,[],[],temp_position]





def get_type_of_CK_max_minus_one(All,die_area,temp_macro):
    
    max_stage=int()

    for ivalue in All:
        if All[ivalue]['stage'][0]>max_stage:
            max_stage=All[ivalue]['stage'][0]


    list_2=list()
    list_3=list()
    for ivalue in All:
        if All[ivalue]['stage'][0]==max_stage-1 and All[ivalue]['direction']=='OUTPUT':
            if len(All[ivalue]['to'])==2:
                list_3.append(ivalue)
            else:
                list_2.append(ivalue)

    checking_inintial_wire_length=dict()
    max_wire_length=float()
    for ivalue in list_3:
        if len(All[All[All[ivalue]['to'][0]]['to'][0]]['to'])==1:
            first_12OUTPUT=All[All[ivalue]['to'][0]]['to'][0]
            second_12OUTPUT=All[All[ivalue]['to'][1]]['to'][0]
        else:
            first_12OUTPUT=All[All[ivalue]['to'][1]]['to'][0]
            second_12OUTPUT=All[All[ivalue]['to'][0]]['to'][0]
        
        target_list=list()
        target_list.append(All[All[first_12OUTPUT]['to'][0]]['position'])
        target_list.append(All[All[second_12OUTPUT]['to'][0]]['position'])
        target_list.append(All[All[second_12OUTPUT]['to'][1]]['position'])
        
        new_position_with_minimum_length=get_minimum_length_and_candidate_3(target_list)
        new_position=new_position_with_minimum_length[0]
        minimum_wire_length=new_position_with_minimum_length[1]
        checking_inintial_wire_length.update({ivalue:{'new_position':new_position,'wire_length':minimum_wire_length,'type':'group3','targets':target_list}})
        if max_wire_length<minimum_wire_length:
            max_wire_length=minimum_wire_length

    for ivalue in list_2:
        INPUT11=All[ivalue]['to'][0]
        OUTPUT12=All[INPUT11]['to'][0]

        first_12INPUT=All[OUTPUT12]['to'][0]
        second_12INPUT=All[OUTPUT12]['to'][1]

        target_list=list()
        target_list.append(All[first_12INPUT]['position'])
        target_list.append(All[second_12INPUT]['position'])
        new_position_with_minimum_length=get_minimum_length_and_candidate_2(target_list)
        new_position=new_position_with_minimum_length[0]
        minimum_wire_length=new_position_with_minimum_length[1]
        checking_inintial_wire_length.update({ivalue:{'new_position':new_position,'wire_length':minimum_wire_length,'type':'group2','target':target_list}})
        if max_wire_length<minimum_wire_length:
            max_wire_length=minimum_wire_length

    for ivalue in checking_inintial_wire_length:
        temp_lines=list()
        if checking_inintial_wire_length[ivalue]['wire_length']!=max_wire_length:

            checking_inintial_wire_length[ivalue].update({'debt':max_wire_length-checking_inintial_wire_length[ivalue]['wire_length']})
            temp_lines=get_pay_off(checking_inintial_wire_length[ivalue])

        else:
            continue
            print(ivalue)
            print(checking_inintial_wire_length[ivalue])
            print()
    return 0



def get_pay_off(info):
    temp_lines=list()

    debt=info['debt']

    if info['type']=='group2':
        
        if info['new_position'][-1]=='dot':
            new_position=info['new_position'][0]
            
            temp_lines.append([new_position[0]-debt/2,new_position[1]])
            temp_lines.append([new_position[0],new_position[1]-debt/2])
            temp_lines.append([new_position[0]+debt/2,new_position[1]])
            temp_lines.append([new_position[0],new_position[1]+debt/2])


        elif info['new_position'][-1]=='horizontal_line':
            position1=list()
            position2=list()
            if info['new_position'][0][0]<info['new_position'][1][0]:
                position1=info['new_position'][0]
                position2=info['new_position'][1]
            else:
                position1=info['new_position'][1]
                position2=info['new_position'][0]

            mid_position=[(position1[0]+position2[0])/2,position1[1]]
            temp_lines.append([position1[0]-debt/2,position1[1]])
            temp_lines.append([mid_position[0],position1[1]-debt/2])
            temp_lines.append([position2[0]+debt/2,position1[1]])
            temp_lines.append([mid_position[0],position1[1]+debt/2])

        elif info['new_position'][-1]=='vertical_line':
            position1=list()
            position2=list()
            if info['new_position'][0][1]<info['new_position'][1][1]:
                position1=info['new_position'][0]
                position2=info['new_position'][1]
            else:
                position1=info['new_position'][1]
                position2=info['new_position'][0]

            mid_position=[position1[0],(position1[1]+position2[1])/2]

            temp_lines.append([position1[0]-debt/2,mid_position[1]])
            temp_lines.append([position1[0],position1[1]-debt/2])
            temp_lines.append([position1[0]+debt/2,mid_position[1]])
            temp_lines.append([position1[0],position2[1]+debt/2])


        else:
            position1=[min(info['new_position'][0][0],info['new_position'][1][0]),min(info['new_position'][0][1],info['new_position'][1][1])]
            position2=[min(info['new_position'][0][0],info['new_position'][1][0]),max(info['new_position'][0][1],info['new_position'][1][1])]
            position3=[max(info['new_position'][0][0],info['new_position'][1][0]),min(info['new_position'][0][1],info['new_position'][1][1])]
            position4=[max(info['new_position'][0][0],info['new_position'][1][0]),max(info['new_position'][0][1],info['new_position'][1][1])]

            temp_lines.append([position1[0]-debt/2,position1[1]])
            temp_lines.append([position1[0],position1[1]-debt/2])
            temp_lines.append([position2[0]-debt/2,position2[1]])
            temp_lines.append([position2[0],position2[1]+debt/2])
            temp_lines.append([position3[0]+debt/2,position3[1]])
            temp_lines.append([position3[0],position3[1]-debt/2])
            temp_lines.append([position4[0]+debt/2,position4[1]])
            temp_lines.append([position4[0],position4[1]+debt/2])
    
    else:
        target1=info['targets'][0]
        target2=info['targets'][1]
        target3=info['targets'][2]

        if target1==target2 and target3==target1:
            position=target1
            temp_lines.append([position[0]-debt/3,position[1]])
            temp_lines.append([position[0],position[1]-debt/3])
            temp_lines.append([position[0]+debt/3,position[1]])
            temp_lines.append([position[0],position[1]+debt/3])

        elif target3==target2 or 직사각형의 경우
            해당경우 타겟3과 타겟2가 같은 경우와, 직각삼각형의 경우의 target을 잘 잡아야된다.
            if target1[0]==target2[0] and target3==target2:
                if target1[1]>target2[1]:
                    temp_lines.append([target2[0]-debt/3,target2[1]])
                    temp_lines.append([target2[0],target2[1]-debt/3])
                    temp_lines.append([target2[0]+debt/3,target2[1]])

                    if (target1[1]-target2[1])>debt:
                        temp_lines.append([target2[0],target2[1]+debt])
                    
                    else:
                        debt=debt-(target1[1]-target2[1])
                        temp_lines.append([target2[0]+debt/3,target1[1]])
                        temp_lines.append([target2[0],target1[1]+debt/3])
                        temp_lines.append([target2[0]-debt/3,target1[1]])

                else:
                    temp_lines.append([target2[0]-debt/3,target2[1]])
                    temp_lines.append([target2[0],target2[1]+debt/3])
                    temp_lines.append([target2[0]+debt/3,target2[1]])

                    if (target2[1]-target1[1])>debt:
                        temp_lines.append([target2[0],target2[1]-debt])

                    else:
                        debt=debt-(target2[1]-target1[1])
                        temp_lines.append([target2[0]+debt/3,target1[1]])
                        temp_lines.append([target2[0],target1[1]-debt/3])
                        temp_lines.append([target2[0]-debt/3,target1[1]])


            elif target1[1]==target2[1] and target3==target2:
                if target1[0]>target2[0]:
                    temp_lines.append([target2[0],target2[1]+debt/3])
                    temp_lines.append([target2[0]-debt/3,target2[1]])
                    temp_lines.append([target2[0],target2[1]-debt/3])

                    if (target1[0]-target2[0])>debt:
                        temp_lines.append([target2[0]+debt,target2[1]])
                    
                    else:
                        debt=debt-(target1[0]-target2[0])
                        temp_lines.append([target1[0],target1[1]-debt/3])
                        temp_lines.append([target1[0]+debt/3,target1[1]])
                        temp_lines.append([target1[0],target1[1]+debt/3])
                else:
                    temp_lines.append([target2[0],target2[1]+debt/3])
                    temp_lines.append([target2[0]+debt/3,target2[1]])
                    temp_lines.append([target2[0],target2[1]-debt/3])
                
                    if (target2[0]-target1[0])>debt:
                        temp_lines.append([target2[0]-debt,target2[1]])
                    
                    else:
                        debt=debt-(target2[0]-target1[0])
                        temp_lines.append([target1[0],target2[1]-debt/3])
                        temp_lines.append([target1[0]-debt/3,target2[1]])
                        temp_lines.append([target1[0],target2[1]+debt/3])


            else:

                target4=list()
                target5=list()

                if target2[0]<target1[0] and target2[1]<target1[1]:

                    temp_lines.append([target2[0]-debt/3,target2[1]])
                    temp_lines.append([target2[0],target2[1]-debt/3])

                    if (target1[1]-target2[1])>debt:
                        temp_lines.append([target2[0],target2[1]+debt])
                    else:
                        temp1_debt=copy.deepcopy(debt)
                        temp1_debt=temp1_debt-(target1[1]-target2[1])

                        temp_lines.append([target2[0]-temp1_debt/3,target1[1]])
                        temp_lines.append([target2[0],target1[1]+temp1_debt/3])

                        if (target1[0]-target2[0])>temp1_debt:
                            temp_lines.append([target2[0]+temp1_debt,target1[1]])
                        else:
                            temp1_debt=temp1_debt-(target1[0]-target2[0])
                            temp_lines.append([target1[0],target1[1]+temp1_debt/3])

                    temptemp=list()

                    if (target1[0]-target2[0])>debt:
                        temptemp.append([target2[0]+debt,target2[1]])
                    else:
                        temp2_debt=copy.deepcopy(debt)
                        temp2_debt=temp2_debt-(target1[0]-target2[0])

                        temptemp.append([target1[0],target2[1]-temp2_debt/3])
                        temptemp.append([target1[0]+temp2_debt/3,target2[1]])

                        if (target1[0]-target2[0])>temp2_debt:
                            temptemp.append([target1[0],target2[1]+temp2_debt])
                        
                        else:
                            temp2_debt=temp2_debt-(target1[1]-target2[1])
                            temptemp.append([target1[0]+temp2_debt/3,target1[1]])

                    temptemp.reverse()
                    for igdxigdx in range(len(temptemp)):
                        temp_lines.append(temptemp[igdxigdx])

                elif target2[0]<target1[0] and target2[1]>target1[1]:

                    temp_lines.append([target2[0]-debt/3,target2[1]])
                    temp_lines.append([target2[0],target2[1]+debt/3])

                    if (target2[1]-target1[1])>debt:
                        temp_lines.append([target2[0],target2[1]-debt])

                    else:
                        temp1_debt=copy.deepcopy(debt)
                        temp1_debt=temp1_debt-(target2[1]-target1[1])

                        temp_lines.append([target2[0]-temp1_debt/3,target1[1]])
                        temp_lines.append([target2[0],target1[1]-temp1_debt/3])

                        if (target1[0]-target2[0])>temp1_debt:
                            temp_lines.append([target2[0]+temp1_debt,target1[1]])
                        
                        else:
                            temp1_debt=temp1_debt-(target1[0]-target2[0])
                            temp_lines.append([target1[0],target1[1]-temp1_debt/3])

                    temptemp=list()

                    if (target1[0]-target2[0])>debt:
                        temptemp.append([target2[0]+debt,target2[1]])
                    
                    else:
                        temp2_debt=copy.deepcopy(debt)
                        temp2_debt=temp2_debt-(target1[0]-target2[0])

                        temptemp.append([target1[0],target2[1]+temp2_debt/3])
                        temptemp.append([target1[0]+temp2_debt/3,target2[1]])

                        if (target1[0]-target2[0])>temp2_debt:
                            temptemp.append([target1[0],target2[1]-temp2_debt])
                        
                        else:
                            temp2_debt=temp2_debt-(target2[1]-target1[1])
                            temptemp.append([target1[0]+temp2_debt/3,target1[1]])

                    temptemp.reverse()
                    for igdxigdx in range(len(temptemp)):
                        temp_lines.append(temptemp[igdxigdx])
                
                elif target2[1]<target1[1]:
                    temp_lines.append([target2[0]+debt/3,target2[1]])
                    temp_lines.append([target2[0],target2[1]-debt/3])

                    if (target1[1]-target2[1])>debt:
                        temp_lines.append([target2[0],target2[1]+debt])
                    
                    else:
                        temp1_debt=copy.deepcopy(debt)
                        temp1_debt=temp1_debt-(target1[1]-target2[1])

                        temp_lines.append([target2[0]+temp1_debt/3,target1[1]])
                        temp_lines.append([target2[0],target1[1]+temp1_debt/3])
                    
                        if (target2[0]-target1[0])>temp1_debt:
                            temp_lines.append([target2[0]-temp1_debt,target1[1]])
                        
                        else:
                            temp1_debt=temp1_debt-(target2[0]-target1[0])
                            temp_lines.append([target1[0],target1[1]+temp1_debt/3])
                    
                    temptemp=list()

                    if (target2[0]-target1[0])>debt:
                        temptemp.append([target2[0]-debt,target2[1]])
                    
                    else:
                        temp2_debt=copy.deepcopy(debt)
                        temp2_debt=temp2_debt-(target2[0]-target1[0])

                        temptemp.append([target1[0],target2[1]-temp2_debt/3])
                        temptemp.append([target1[0]-temp2_debt/3,target2[1]])

                        if (target1[1]-target2[1])>temp2_debt:
                            temptemp.append([target1[0],target2[1]+temp2_debt])
                        
                        else:
                            temp2_debt=temp2_debt-(target1[1]-target2[1])
                            temptemp.append([target1[0]-temp2_debt/3,target1[1]])

                    temptemp.reverse()
                    for igdxigdx in range(len(temptemp)):
                        temp_lines.append(temptemp[igdxigdx])

                else:
                    temp_lines.append([target2[0]+debt/3,target2[1]])
                    temp_lines.append([target2[0],target2[1]+debt/3])
                
                    if (target2[1]-target1[1])>debt:
                        temp_lines.append([target2[0],target2[1]-debt])
                    
                    else:
                        temp1_debt=copy.deepcopy(debt)
                        temp1_debt=temp1_debt-(target2[1]-target1[1])

                        temp_lines.append([target2[0]+temp1_debt/3,target1[1]])
                        temp_lines.append([target2[0],target1[1]-temp1_debt/3])

                        if (target2[0]-target1[0])>temp1_debt:
                            temp_lines.append([target2[0]-temp1_debt,target1[1]])
                        
                        else:
                            temp1_debt=temp1_debt-(target2[0]-target1[0])
                            temp_lines.append([target1[0],target1[1]-temp1_debt/3])
                    
                    temptemp=list()

                    if (target2[0]-target1[0])>debt:
                        temptemp.append([target2[0]-debt,target2[1]])
                    
                    else:
                        temp2_debt=copy.deepcopy(debt)
                        temp2_debt=temp2_debt-(target2[0]-target1[0])
                        temptemp.append([target1[0],target2[1]+temp2_debt/3])
                        temptemp.append([target1[0]-temp2_debt/3,target2[1]])

                        if (target2[1]-target1[1])>temp2_debt:
                            temptemp.append([target1[0],target2[1]-temp2_debt])
                        
                        else:
                            temp2_debt=temp2_debt-(target2[1]-target1[1])
                            temptemp.append([target1[0]-temp2_debt/3,target1[1]])
                    temptemp.reverse()
                    for igdxigdx in range(len(temptemp)):
                        temp_lines.append(temptemp[igdxigdx])
            ################################################################################ 여기서부터
        else:
            if target1[0]==target2[0]==target3[0]:
                return 0
                print(info)
            elif target1[0]==target2[0] or target2[0]==target3[0] or target3[0]==target1[0]:
                return 0
                print(info)
                #############특수한 경우(직각 삼각형: elif target3==target2(직사각형) 인 경우와 매우 비슷하다.)
            elif target1[1]==target2[1]==target3[1]:
                return 0
            elif target1[1]==target2[1] or target2[1]==target3[1] or target3[1]==target1[1]:
                return 0
                print(info)
            else:
                return 0
                print(info)

    return 0









def get_minimum_length_and_candidate_2(listlist):
    not_single_1=listlist[0]
    not_single_2=listlist[1]

    new_position=list()
    minimum_length=float()
    additional_lines=list()


    if not_single_1==not_single_2:
        new_position=[not_single_1,'dot']
        minimum_length=0
        additional_lines=[[str(not_single_1[0])+' +k/2',str(not_single_1[1])],\
            ]
    
    elif not_single_1[1]==not_single_2[1]:
        new_position=[not_single_1,not_single_2,'horizontal_line']
    
    elif not_single_1[0]==not_single_2[0]:
        new_position=[not_single_1,not_single_2,'vertical_line']
    
    else:
        new_position=[not_single_1,not_single_2,'rectangle_plane']

    minimum_length=abs(not_single_1[0]-not_single_2[0])+abs(not_single_1[1]-not_single_2[1])

    return [new_position,minimum_length]






def get_minimum_length_and_candidate_3(listlist):
    single=listlist[0]
    not_single_1=listlist[1]
    not_single_2=listlist[2]

    new_position=list()
    minimum_length=float()

    if single==not_single_1 and not_single_1==not_single_2:
        new_position=[single,'dot']
        minimum_length=0

    elif not_single_1==not_single_2:
        new_position=[not_single_1,'dot']
        minimum_length=abs(not_single_1[0]-single[0])+abs(not_single_1[1]-single[1])
        
    else:
        max_x=float()
        for gdx in range(3):
            if max_x<listlist[gdx][0]:
                max_x=listlist[gdx][0]

        min_x=max_x
        counts_of_max_x=int()
        for gdx in range(3):
            if min_x>listlist[gdx][0]:
                min_x=listlist[gdx][0]
            if listlist[gdx][0]==max_x:
                counts_of_max_x=counts_of_max_x+1

        mid_x=float()
        counts_of_min_x=int()
        for gdx in range(3):
            if listlist[gdx][0]!=min_x and listlist[gdx][0]!=max_x:
                mid_x=listlist[gdx][0]
            if listlist[gdx][0]==min_x:
                counts_of_min_x=counts_of_min_x+1
        
        if mid_x==float():
            if counts_of_max_x>counts_of_min_x:
                mid_x=max_x
            else:
                mid_x=min_x
        
        midpoint1=(mid_x+min_x)/2
        midpoint2=(mid_x+max_x)/2
        midpoint=(midpoint1+midpoint2)/2

        abs_list=list()
        max_abs=float()
        for gdx in range(3):
            abs_list.append(abs(midpoint-listlist[gdx][0]))
            if max_abs<abs(midpoint-listlist[gdx][0]):
                max_abs=abs(midpoint-listlist[gdx][0])
        
        min_abs=max_abs
        index_of_min=int()
        result_x=float()
        for gdx in range(3):
            if min_abs>abs_list[gdx]:
                min_abs=abs_list[gdx]
                index_of_min=gdx
        result_x=listlist[index_of_min][0]
        result_x_x=result_x

        max_x=float()
        for gdx in range(3):
            if max_x<listlist[gdx][1]:
                max_x=listlist[gdx][1]

        min_x=max_x
        counts_of_max_x=int()
        for gdx in range(3):
            if min_x>listlist[gdx][1]:
                min_x=listlist[gdx][1]
            if listlist[gdx][1]==max_x:
                counts_of_max_x=counts_of_max_x+1

        mid_x=float()
        counts_of_min_x=int()
        for gdx in range(3):
            if listlist[gdx][1]!=min_x and listlist[gdx][1]!=max_x:
                mid_x=listlist[gdx][1]
            if listlist[gdx][1]==min_x:
                counts_of_min_x=counts_of_min_x+1
        
        if mid_x==float():
            if counts_of_max_x>counts_of_min_x:
                mid_x=max_x
            else:
                mid_x=min_x
        
        midpoint1=(mid_x+min_x)/2
        midpoint2=(mid_x+max_x)/2
        midpoint=(midpoint1+midpoint2)/2

        abs_list=list()
        max_abs=float()
        for gdx in range(3):
            abs_list.append(abs(midpoint-listlist[gdx][1]))
            if max_abs<abs(midpoint-listlist[gdx][1]):
                max_abs=abs(midpoint-listlist[gdx][1])
        
        min_abs=max_abs
        index_of_min=int()
        result_x=float()
        for gdx in range(3):
            if min_abs>abs_list[gdx]:
                min_abs=abs_list[gdx]
                index_of_min=gdx
        result_x=listlist[index_of_min][1]
        result_y=result_x
        new_position=[[result_x_x,result_y],'dot']

        checkinglist=list()
        checkinglist.append(new_position[0])
        for gdx in range(3):
            checkinglist.append(listlist[gdx])
        minimum_length=get_new_wirelength_star(checkinglist)

    return [new_position,minimum_length]
get_new_wirelength_star







if __name__ == "__main__":
    arguments=sys.argv
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
    die_area[0]=die_area[0][0]/def_unit,die_area[0][1]/def_unit
    die_area[1]=die_area[1][0]/def_unit,die_area[1][1]/def_unit





    
    '''typed_All=get_type_of_new_graph(netinfo,file_address)

    cutting_All=get_delnode_new_list(typed_All)
    CLK2reg_All=get_CLK2CK_new_graph(cutting_All)
    without_clk_All=get_new_del_related_with_CLK(cutting_All,CLK2reg_All)

    without_unconnected_All_clk=new_del_unconnected_nodes(CLK2reg_All)
    without_unconnected_All=new_del_unconnected_nodes(without_clk_All)



    stage_All_clk=get_new_stage_nodes_for_clk_nodes(without_unconnected_All_clk,netinfo_for_clk)

    stage_All=get_new_stage_nodes(without_unconnected_All)
    clk_All_with_wire_cap=get_new_wire_cap(stage_All_clk,default_wire_load_model)
    All_with_wire_cap=get_new_wire_cap(stage_All,default_wire_load_model)



    delay_with_clk_All=get_new_Delay_of_nodes_CLK(clk_All_with_wire_cap,CLK_mode,wire_mode,liberty_type)

    delay_only_first_stage_without_clk_All=get_new_Delay_of_nodes_stage0(All_with_wire_cap,delay_with_clk_All,wire_mode,liberty_type)
    delay_without_clk_All=get_new_all_Delay_Transition_of_nodes(delay_only_first_stage_without_clk_All,wire_mode,liberty_type)
    path=get_new_worst_path(delay_without_clk_All)


    if 'scratch' in def_name:
        file_pathpath='temp_scratch.json'
        with open(file_pathpath,'w') as f:
            json.dump(delay_without_clk_All,f,indent=4)

        file_pathpath='temp_for_clk_scratch.json'
        with open(file_pathpath,'w') as f:
            json.dump(stage_All_clk,f,indent=4)


    else:
        file_pathpath='temp_'+def_name.split('.def')[0]+'.json'
        with open(file_pathpath,'w') as f:
            json.dump(delay_without_clk_All,f,indent=4)

        file_pathpath='temp_for_clk_'+def_name.split('.def')[0]+'.json'
        with open(file_pathpath,'w') as f:
            json.dump(stage_All_clk,f,indent=4)'''



##################################################################################################################################################



    temp_macro='CLKBUF_X1'
    if wire_mode=='wire_load':
        file_pathtt='../data/deflef_to_graph_and_verilog/results/test_7800_wire_load_scratch_CTS/scratch_detailed.json'
        with open(file_pathtt,'r') as f:
            CTS_info=json.load(f)

    else:
        file_pathpath='../data/deflef_to_graph_and_verilog/results/'+file_address_name+'/test_7800_zfor_clk_'+wire_mode+'_with_skew/'+file_name.split('_revised')[0]+'.json'
        with open(file_pathpath,'r') as f:
            CTS_info=json.load(f)

    skew=CTS_info[1]
    clk_All_with_skew=CTS_info[0]



    qqq=get_type_of_CK_max_minus_one(clk_All_with_skew,die_area,temp_macro)
    ##rrr=get_type_of_CK_max_minus_two(clk_All_with_skew,die_area,temp_macro)

   ##print(idxidx)
    ##print(kdxkdx)
    ##print(sys.argv)