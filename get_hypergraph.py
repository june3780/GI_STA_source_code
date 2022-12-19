import os
import json
import re
import time
import sys
import pickle
import pandas as pd
import copy
import gc

def get_each_cell(file,lib_file):
    new_cell_new_dict=dict()

    wire_dict=dict()
    ff=open(file)
    lines=ff.readlines()
    for idx in range(len(lines)):

        checking_str=lines[idx].strip()
        
        maybe_cell_name_or_input_or_output_or_wire=checking_str.replace('\n','').split(' ')[0]
        if maybe_cell_name_or_input_or_output_or_wire not in lib_file:
            if maybe_cell_name_or_input_or_output_or_wire=='input':

                new_cell_new_dict.update({checking_str.replace('\n','').split(' ')[1].replace(';',''):{'to':[],'type':'pin','pin_direction':'input','stage':0}})
                
            elif maybe_cell_name_or_input_or_output_or_wire=='output':
                new_cell_new_dict.update({checking_str.replace('\n','').split(' ')[1].replace(';',''):{'from':[],'type':'pin','pin_direction':'output','stage':0}})

            elif maybe_cell_name_or_input_or_output_or_wire=='wire':
                wire_dict.update({checking_str.replace('\n','').split(' ')[1].replace(';',''):{'to':[],'from':[]}})

        else:

            new_cell_new_dict.update({checking_str.replace('\n','').split(' ')[1]:{'macroID':maybe_cell_name_or_input_or_output_or_wire,'input':{},'output':{},'type':'cell','description':lib_file[maybe_cell_name_or_input_or_output_or_wire]['description']}})
            list_of_check=checking_str.split('.')[1:]
            for ddx in range(len(list_of_check)):
                temp_pin=list_of_check[ddx].split('(')[0]
                temp_net=list_of_check[ddx].split('(')[1]
                temp_net=temp_net.split(')')[0]
                list_of_check[ddx]='.'+temp_pin+'('+temp_net+')'

            for kdx in range(len(list_of_check)):
                pin_name=list_of_check[kdx].split('.')[1].split('(')[0]
                if pin_name in lib_file[maybe_cell_name_or_input_or_output_or_wire]['input']:
                    new_cell_new_dict[checking_str.replace('\n','').split(' ')[1]]['input'].update({pin_name:{'from':list_of_check[kdx].split('(')[1].split(')')[0]}})
                else:
                    new_cell_new_dict[checking_str.replace('\n','').split(' ')[1]]['output'].update({pin_name:{'to':[list_of_check[kdx].split('(')[1].split(')')[0]]}})
    ff.close()

    recursive_ivalue=dict()
    

    for ivalue in new_cell_new_dict:
        if new_cell_new_dict[ivalue]['type']=='cell':
            
            input_dict=new_cell_new_dict[ivalue]['input']
            for kvalue in input_dict:
                if input_dict[kvalue]['from'] in new_cell_new_dict and new_cell_new_dict[input_dict[kvalue]['from']]['pin_direction']=='input':
                    new_cell_new_dict[input_dict[kvalue]['from']]['to'].append(ivalue+' '+kvalue)

                elif input_dict[kvalue]['from'] in wire_dict and input_dict[kvalue]['from'] not in recursive_ivalue:
                    wire_dict[input_dict[kvalue]['from']]['to'].append(ivalue+' '+kvalue)
            
                else:
                    if input_dict[kvalue]['from'] not in wire_dict:
                        wire_dict.update({input_dict[kvalue]['from']:{'to':[],'from':[]}})
                    if input_dict[kvalue]['from'] not in recursive_ivalue:
                        recursive_ivalue.update({input_dict[kvalue]['from']:{'to':[],'from':[]}})
                    wire_dict[input_dict[kvalue]['from']]['to'].append(ivalue+' '+kvalue)
                    recursive_ivalue[input_dict[kvalue]['from']]['to'].append(ivalue+' '+kvalue)
            input_dict=dict()
            
    for ivalue in new_cell_new_dict:
        if new_cell_new_dict[ivalue]['type']=='cell':
            output_dict=new_cell_new_dict[ivalue]['output']
            for kvalue in output_dict:
                if output_dict[kvalue]['to'][0] in new_cell_new_dict and new_cell_new_dict[output_dict[kvalue]['to'][0]]['pin_direction']=='output':
                    new_cell_new_dict[output_dict[kvalue]['to'][0]]['from'].append(ivalue+' '+kvalue)

                elif output_dict[kvalue]['to'][0] in wire_dict:
                    wire_dict[output_dict[kvalue]['to'][0]]['from'].append(ivalue+' '+kvalue)
            output_dict=dict()
            

    for ivalue in recursive_ivalue:
        for kvalue in recursive_ivalue[ivalue]['to']:
            if kvalue not in new_cell_new_dict[new_cell_new_dict[ivalue]['from'][0].split(' ')[0]]['output'][new_cell_new_dict[ivalue]['from'][0].split(' ')[1]]['to']:
                new_cell_new_dict[new_cell_new_dict[ivalue]['from'][0].split(' ')[0]]['output'][new_cell_new_dict[ivalue]['from'][0].split(' ')[1]]['to'].append(kvalue)
            if new_cell_new_dict[ivalue]['from'][0] not in new_cell_new_dict[kvalue.split(' ')[0]]['input'][kvalue.split(' ')[1]]['from']:
                new_cell_new_dict[kvalue.split(' ')[0]]['input'][kvalue.split(' ')[1]]['from']=new_cell_new_dict[ivalue]['from'][0]
        del wire_dict[ivalue]
    ##print(json.dumps(recursive_ivalue,indent=4))
    recursive_ivalue=dict()



    for ivalue in wire_dict:
        output_one=wire_dict[ivalue]['from'][0]
        temp_one=str()
        if ' ' in output_one:
            temp_one=output_one.split(' ')[1]
            output_one=output_one.split(' ')[0]

        input_list=wire_dict[ivalue]['to']
        new_cell_new_dict[output_one]['output'][temp_one]['to']=input_list
        for kvalue in input_list:
            temp_input_port=str()
            input_one=kvalue
            if ' ' in input_one:
                temp_input_port=input_one.split(' ')[1]
                input_one=input_one.split(' ')[0]
            new_cell_new_dict[input_one]['input'][temp_input_port]['from']=wire_dict[ivalue]['from'][0]

    wire_dict=dict()

    for ivalue in new_cell_new_dict:
        if new_cell_new_dict[ivalue]['type']=='cell':
            if new_cell_new_dict[ivalue]['description']=='Combinational cell' or new_cell_new_dict[ivalue]['description']=='Pos.edge D-Flip-Flop':
                for kvalue in new_cell_new_dict[ivalue]['output']:
                    temp_wire_cap_fall=float()
                    temp_wire_cap_rise=float()
                    for jvalue in new_cell_new_dict[ivalue]['output'][kvalue]['to']:
                        temp_port=str()
                        one_input=jvalue
                        if ' ' in one_input:
                            temp_port=one_input.split(' ')[1]
                            one_input=one_input.split(' ')[0]
                        #print(ivalue)
                        #print(one_input)
                        #print()
                        if new_cell_new_dict[one_input]['type']=='cell':
                            temp_wire_cap_fall=temp_wire_cap_fall+lib_file[new_cell_new_dict[one_input]['macroID']]['input'][temp_port]['fall_capacitance']
                            temp_wire_cap_rise=temp_wire_cap_rise+lib_file[new_cell_new_dict[one_input]['macroID']]['input'][temp_port]['rise_capacitance']
                        else: ####################################################################################################### sdc 파일
                            if sys.argv[1]==str(1) or sys.argv[1]==str(2):
                                temp_wire_cap_fall=temp_wire_cap_fall+0
                                temp_wire_cap_rise=temp_wire_cap_rise+0
                            elif sys.argv[1]==str(3):
                                temp_wire_cap_fall=temp_wire_cap_fall+4
                                temp_wire_cap_rise=temp_wire_cap_rise+4

                    new_cell_new_dict[ivalue]['output'][kvalue].update({'load_cap_fall':temp_wire_cap_fall})
                    new_cell_new_dict[ivalue]['output'][kvalue].update({'load_cap_rise':temp_wire_cap_rise})
            else:
                for kvalue in new_cell_new_dict[ivalue]['output']:
                    new_cell_new_dict[ivalue]['output'][kvalue].update({'load_cap_fall':float(0)})
                    new_cell_new_dict[ivalue]['output'][kvalue].update({'load_cap_rise':float(0)}) 

    for ivalue in lib_file:
        if 'input' in lib_file[ivalue]:
            del lib_file[ivalue]['input']

    return [new_cell_new_dict,lib_file]






def get_unconnect(nets,lib):
    clk_groups=dict()
    ck_port_group=dict()

    for ivalue in nets:
        if nets[ivalue]['type']=='cell':
            if nets[ivalue]['description']=='Pos.edge D-Flip-Flop':
                for kvalue in nets[ivalue]['output']:
                    
                    for jvalue in lib[nets[ivalue]['macroID']]['output'][kvalue]['conditionlist']:  
                        if nets[ivalue]['macroID'] not in ck_port_group:
                            ck_port_group.update({nets[ivalue]['macroID']:[]})
                        if "unateness : non_unate" in jvalue:
                            if jvalue.split('related_pin : ')[1].split(', unateness')[0].strip() not in ck_port_group[nets[ivalue]['macroID']]:
                                ck_port_group[nets[ivalue]['macroID']].append(jvalue.split('related_pin : ')[1].split(', unateness')[0].strip())

    for ivalue in nets:
        if nets[ivalue]['type']=='cell':
            if nets[ivalue]['description']=='Pos.edge D-Flip-Flop':
                clk_groups.update({ivalue:{'macroID':nets[ivalue]['macroID'],'input':{},'output':{},'type':'cell','description':'Pos.edge D-Flip-Flop'}})
                for clk in nets[ivalue]['input']:
                    if clk in ck_port_group[nets[ivalue]['macroID']]:
                        clk_groups[ivalue]['input'].update({clk:nets[ivalue]['input'][clk]})

    
    kkk=int()
    temp_clk_group=list()
    for ivalue in clk_groups:
        kkk=kkk+1
        temp_clk=str()
        for kvalue in clk_groups[ivalue]['input']:
            del nets[ivalue]['input'][kvalue]
            temp_clk=kvalue
        checking_cell_with_port=clk_groups[ivalue]['input'][temp_clk]['from']

        if ' ' in checking_cell_with_port:
            checking_cell_with_port=checking_cell_with_port.split(' ')[0]

        while True:
            if checking_cell_with_port not in temp_clk_group:
                temp_clk_group.append(checking_cell_with_port)
            if nets[checking_cell_with_port]['type']=='pin':
                break
            temp_input=str()
            for tvalue in nets[checking_cell_with_port]['input']:
                temp_input=tvalue
            if ' ' in nets[checking_cell_with_port]['input'][temp_input]['from']:
                checking_cell_with_port=nets[checking_cell_with_port]['input'][temp_input]['from'].split(' ')[0]
            else:
                checking_cell_with_port=nets[checking_cell_with_port]['input'][temp_input]['from']


    for idx in range(len(temp_clk_group)):
        clk_groups.update({temp_clk_group[idx]:nets[temp_clk_group[idx]]})
        del nets[temp_clk_group[idx]]
    return [clk_groups,nets]



################################ cycle이 있는지 확인하는 함수 필요
def checking_input_list_new(All,dict_dict,cell_one):
    if All[cell_one]['macroID']=='DFF_X1':
        return dict_dict
    for ivalue in dict_dict[cell_one]['output']:
        for kvalue in dict_dict[cell_one]['output'][ivalue]['to']:
            if ' ' not in kvalue:
                continue
            if kvalue.split(' ')[0] not in dict_dict:
                dict_dict.update({kvalue.split(' ')[0]:{'input':{},'output':{},'macroID':All[kvalue.split(' ')[0]]['macroID']}})
                dict_dict[kvalue.split(' ')[0]]['input'].update({kvalue.split(' ')[1]:All[kvalue.split(' ')[0]]['input'][kvalue.split(' ')[1]]})
            
            else:
                if kvalue.split(' ')[1] in dict_dict[kvalue.split(' ')[0]]['input']:
                    for kkkvalue in dict_dict:
                        print(kkkvalue)
                        print(dict_dict[kkkvalue])
                        print()
                    print()
                    print('tpmglwsn1!!!!!')
                    print(kvalue.split(' ')[0]+' '+kvalue.split(' ')[1])
                    print()
                    print(cell_one)
                    print(All[cell_one])
                    return 'break'
                else:
                    dict_dict[kvalue.split(' ')[0]]['input'].update({kvalue.split(' ')[1]:All[kvalue.split(' ')[0]]['input'][kvalue.split(' ')[1]]})

            for jvalue in All[kvalue.split(' ')[0]]['output']:
                dict_dict[kvalue.split(' ')[0]]['output'].update({jvalue:All[kvalue.split(' ')[0]]['output'][jvalue]})

            
            dict_dict=checking_input_list_new(All,dict_dict,kvalue.split(' ')[0])


        return dict_dict
################################ cycle이 있는지 확인하는 함수 필요




def get_new_stage_nodes(All,lib):
    for ivalue in All:
        if All[ivalue]['type']=='cell':
            if All[ivalue]['description']=='Constant cell' or All[ivalue]['description']=='Pos.edge D-Flip-Flop':
                All[ivalue].update({'stage':0})
            elif All[ivalue]['description']=='MACRO':
                for kvalue in All[ivalue]['output']:
                    if 'unateness : complex' in lib[All[ivalue]['macroID']]['output'][kvalue]['conditionlist'][0]:
                        All[ivalue]['output'][kvalue].update({'stage':0})

        elif All[ivalue]['type']=='pin':
            if All[ivalue]['pin_direction']=='output':
                All[ivalue]['from']=All[ivalue]['from'][0]


    current_stage=1
    while True:
        rrr=int()
        for ivalue in All:
            if 'stage' not in All[ivalue]:
                continue_str=str()
                rrr=rrr+1
                if All[ivalue]['description']!='MACRO':
                        for kvalue in All[ivalue]['input']:
                            temp_from=All[ivalue]['input'][kvalue]['from']
                            if ' ' in temp_from:
                                temp_from=temp_from.split(' ')[0]
        
                            if 'stage' in All[temp_from] and All[temp_from]['type']=='pin':
                                if All[temp_from]['stage']<current_stage:
                                    continue
                                else:
                                    continue_str='continue'
                                    break

                            elif 'stage' in All[temp_from] and All[temp_from]['description']!='MACRO':
                                if All[temp_from]['stage']<current_stage:
                                    continue
                                else:
                                    continue_str='continue'
                                    break
                            
                            elif 'stage' in All[temp_from]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]] and All[temp_from]['description']=='MACRO':
                                if All[temp_from]['output'][All[ivalue]['input'][kvalue]['from'].split(' ')[1]]['stage']<current_stage:
                                    continue
                                else:
                                    continue_str='continue'
                                    break
                            
                            else:
                                continue_str='continue'
                                break

                        if continue_str=='continue':
                            continue

                        else:
                            All[ivalue].update({'stage':current_stage})

                else:
                    for kvalue in All[ivalue]['output']:
                        if 'stage' not in All[ivalue]['output'][kvalue]:
                            related_pin=lib[All[ivalue]['macroID']]['output'][kvalue]['conditionlist'][0].split('related_pin : ')[1].split(', unateness :')[0]
                            from_related=All[ivalue]['input'][related_pin]['from']

                            if ' ' in from_related:
                                from_related=from_related.split(' ')[0]


                            if 'stage' in All[from_related] and All[from_related]['type']=='pin':
                                if All[from_related]['stage']==current_stage-1:
                                    All[ivalue]['output'][kvalue].update({'stage':current_stage})
                                else:
                                    continue_str='continue'
                                    continue

                            elif 'stage' in All[from_related] and All[from_related]['description']!='MACRO':
                                if All[from_related]['stage']==current_stage-1:
                                    All[ivalue]['output'][kvalue].update({'stage':current_stage})
                                else:
                                    continue_str='continue'
                                    continue
                            elif 'stage' in All[from_related]['output'][All[ivalue]['input'][related_pin]['from'].split(' ')[1]] and All[from_related]['description']=='MACRO':
                                if All[from_related]['output'][All[ivalue]['input'][related_pin]['from'].split(' ')[1]]['stage']==current_stage-1:
                                    All[ivalue]['output'][kvalue].update({'stage':current_stage})
                                else:
                                    continue_str='continue'
                                    continue

                            else:
                                continue_str='continue'

                    if continue_str=='continue':
                        continue
                    else:
                        All[ivalue].update({'stage':0})
        if rrr==0:
            break
        
        else:
            current_stage=current_stage+1
            continue
########################################################################################## macro 재설정
    all_macro=dict()
    for ivalue in All:
        if All[ivalue]['type']=='cell':
            if All[ivalue]['description']=='MACRO':
                if_input_what_stage=dict()
                stage_dict=dict()
                input_to_output=dict()
                all_related_pins=list()
                for kvalue in All[ivalue]['output']:
                    if str(All[ivalue]['output'][kvalue]['stage']) not in stage_dict:
                        stage_dict.update({str(All[ivalue]['output'][kvalue]['stage']):{'input':[],'output':[]}})
                    if kvalue not in stage_dict[str(All[ivalue]['output'][kvalue]['stage'])]['output']:
                        stage_dict[str(All[ivalue]['output'][kvalue]['stage'])]['output'].append(kvalue)
                    related_pin=lib[All[ivalue]['macroID']]['output'][kvalue]['conditionlist'][0].split('related_pin : ')[1].split(', unateness :')[0]
                    

                    if related_pin !='all':
                        if related_pin not in stage_dict[str(All[ivalue]['output'][kvalue]['stage'])]['input']:
                            stage_dict[str(All[ivalue]['output'][kvalue]['stage'])]['input'].append(related_pin)
                        if related_pin not in all_related_pins:
                            all_related_pins.append(related_pin)
                        if_input_what_stage.update({related_pin:str(All[ivalue]['output'][kvalue]['stage'])})
                    
                    else:
                        if str(0) not in stage_dict:
                            stage_dict.update({str(0):{'input':[],'output':[]}})
                        if kvalue not in stage_dict[str(0)]['output']:
                            stage_dict[str(0)]['output'].append(kvalue)

                for kvalue in All[ivalue]['input']:
                    if kvalue not in all_related_pins:
                        if str(0) not in stage_dict:
                            stage_dict.update({str(0):{'input':[],'output':[]}})
                        if kvalue not in stage_dict[str(0)]['input']:
                            stage_dict[str(0)]['input'].append(kvalue)

                for stage_number in stage_dict:
                    for macro_input in stage_dict[stage_number]['input']:
                        temp_input_from=All[ivalue]['input'][macro_input]['from']
                        if ' ' in temp_input_from:
                            temp_input_from=temp_input_from.split(' ')[0]
                        if '_stage' in temp_input_from:
                            temp_input_from=temp_input_from.split(' ')[0].split('_stage')[0]
                        if All[temp_input_from]['type']=='pin':
                            All[temp_input_from]['to'].remove(ivalue+' '+macro_input)
                            All[temp_input_from]['to'].append(ivalue+'_stage'+stage_number+' '+macro_input)
                        else:
                            All[temp_input_from]['output'][All[ivalue]['input'][macro_input]['from'].split(' ')[1]]['to'].remove(ivalue+' '+macro_input)
                            All[temp_input_from]['output'][All[ivalue]['input'][macro_input]['from'].split(' ')[1]]['to'].append(ivalue+'_stage'+stage_number+' '+macro_input)

                    for macro_output in stage_dict[stage_number]['output']:
                            temp_output_to_list=All[ivalue]['output'][macro_output]['to']
                            for kvalue in temp_output_to_list:
                                temp_output_to=kvalue
                                if ' ' in temp_output_to:
                                    temp_output_to=temp_output_to.split(' ')[0]
                                
                                if '_stage' in temp_output_to:
                                    temp_output_to=temp_output_to.split(' ')[0].split('_stage')[0]
                                
                                if All[temp_output_to]['type']=='pin':
                                    All[temp_output_to]['from']=ivalue+'_stage'+stage_number+' '+macro_output
                                else:
                                    All[temp_output_to]['input'][kvalue.split(' ')[1]]['from']=ivalue+'_stage'+stage_number+' '+macro_output

                all_macro.update({ivalue:stage_dict})


    for ivalue in all_macro:
        for kvalue in all_macro[ivalue]:
            All.update({ivalue+'_stage'+kvalue:{'input':{},'output':{},'macroID':All[ivalue]['macroID'],'description':'MACRO','stage':int(kvalue),'type':'cell'}})
            for temp_input in all_macro[ivalue][kvalue]['input']:
                All[ivalue+'_stage'+kvalue]['input'].update({temp_input:All[ivalue]['input'][temp_input]})
            for temp_output in all_macro[ivalue][kvalue]['output']:
                All[ivalue+'_stage'+kvalue]['output'].update({temp_output:All[ivalue]['output'][temp_output]})
        del All[ivalue]

    

    return All







if __name__ == "__main__":
    ##os.chdir('Documents/PNR/timing/source/')
    ## sys.argv[v, lib]
    argv1='scratch_detailed_temp.v'
    argv2='OPENSTA_example1_slow.lib'
    if sys.argv[1]==str(1):
        argv1='gcd.v'
        argv2='OPENSTA_example1_slow.lib'
    elif sys.argv[1]==str(2):
        argv1='scratch_detailed.v'
        argv2='OPENSTA_example1_slow.lib'
    elif sys.argv[1]==str(3):
        argv1='superblue16.v'
        argv2='superblue16_Late.lib'
    argv1=sys.argv[1]
    argv2=sys.argv[2]

    where_the_verilog='../data/deflef_to_graph_and_verilog/verilog/'+argv1
    where_the_lib='../data/deflef_to_graph_and_verilog/libs/'+argv2.split('.lib')[0]+'/'
    liibb_file='../data/deflef_to_graph_and_verilog/libs/'+argv2.split('.lib')[0]+'/dictionary_of_lib.json'
    without_input_lib=liibb_file.split('.json')[0]+'_without_input.json'
    where_the_hypergraph='../data/deflef_to_graph_and_verilog/hypergraph/'

    directory_name=where_the_verilog.split('/')[-1].split('.v')[0]+'_'+argv2.split('.lib')[0]


    file_save_address_stage_without_clk=where_the_hypergraph+directory_name+'/stage_without_clk(temp).pickle'
    file_save_address_stage_with_clk=where_the_hypergraph+directory_name+'/stage_with_clk(temp).pickle'

    with open(liibb_file, 'r') as file:
        lib_file = json.load(file)
    file.close()

    net_info=dict()
    unconnect_graph=list()
    net_infgo=get_each_cell(where_the_verilog,lib_file)
    net_info=net_infgo[0]
    ##print(json.dumps(net_info,indent=4))
    ##print()
    new_lib=net_infgo[1]


    unconnect_graph=get_unconnect(net_info,new_lib)

    stage_without_clk=get_new_stage_nodes(unconnect_graph[1],new_lib)
    stage_with_clk=get_new_stage_nodes(unconnect_graph[0],new_lib)

    if directory_name not in os.listdir(where_the_hypergraph):
        os.mkdir(where_the_hypergraph+directory_name)

    with open(file_save_address_stage_without_clk,'wb') as fw:
        pickle.dump(stage_without_clk, fw)
    fw.close()

    with open(file_save_address_stage_with_clk,'wb') as fw:
        pickle.dump(stage_with_clk, fw)
    fw.close()

    with open(without_input_lib, 'w') as file:
        json.dump(new_lib,file,indent=4)
    file.close()

