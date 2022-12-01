import os
import json
import re
import time
import sys
import pickle
import pandas as pd
import copy


def get_each_cell(file,libAdrress):
    
    cell_dict=dict()
    input_pins=dict()
    output_pins=dict()
    nets=dict()
    ff=open(file)
    lines=ff.readlines()
    not_use_output_pin=list()
    for idx in range(len(lines)):
        checking_str=lines[idx].strip()
        maybe_cell_name_or_input_or_output_or_wire=checking_str.replace('\n','').split(' ')[0]

        if maybe_cell_name_or_input_or_output_or_wire not in os.listdir(libAdrress):
            
            if maybe_cell_name_or_input_or_output_or_wire=='input':
                input_pins.update({checking_str.replace('\n','').split(' ')[1].replace(';',''):{'to':[],'from':[]}})
                
            elif maybe_cell_name_or_input_or_output_or_wire=='output':
                output_pins.update({checking_str.replace('\n','').split(' ')[1].replace(';',''):{'to':[],'from':[]}})
            elif maybe_cell_name_or_input_or_output_or_wire=='wire':
                nets.update({checking_str.replace('\n','').split(' ')[1].replace(';',''):{'to':[],'from':[]}})

        else:
            cell_dict.update({maybe_cell_name_or_input_or_output_or_wire+' '+checking_str.replace('\n','').split(' ')[1]:{}})
            in_lib_inffo=libAdrress+maybe_cell_name_or_input_or_output_or_wire
            file_list_of_the_macro=os.listdir(in_lib_inffo)

            

            p=re.findall('[.]\w*[(]\w*[)]',checking_str)
            for kdx in range(len(p)):
                pin_name=p[kdx].split('.')[1].split('(')[0]
                direction=str()
                cell_dict[maybe_cell_name_or_input_or_output_or_wire+' '+checking_str.replace('\n','').split(' ')[1]].update({pin_name:{}})


                if '2_input_'+pin_name+'.tsv' in file_list_of_the_macro:
                    direction='INPUT'
                elif '3_output_'+pin_name in file_list_of_the_macro:
                    direction='OUTPUT'

                cell_dict[maybe_cell_name_or_input_or_output_or_wire+' '+checking_str.replace('\n','').split(' ')[1]][pin_name].update({'direction':direction})

                if direction=='INPUT':
                    cell_dict[maybe_cell_name_or_input_or_output_or_wire+' '+checking_str.replace('\n','').split(' ')[1]][pin_name].update({'from':p[kdx].split('(')[1].split(')')[0]})
                else:
                    cell_dict[maybe_cell_name_or_input_or_output_or_wire+' '+checking_str.replace('\n','').split(' ')[1]][pin_name].update({'to':p[kdx].split('(')[1].split(')')[0]})
    ff.close()
    
    new_cell_dict=dict()

    recursive_ivalue=dict()
    for ivalue in cell_dict:

        output_list=list()
        input_list=list()
        for kvalue in cell_dict[ivalue]:
            if cell_dict[ivalue][kvalue]['direction']=='OUTPUT':
                output_list.append(ivalue.split(' ')[1]+' '+kvalue)
            else:
                input_list.append(ivalue.split(' ')[1]+' '+kvalue)

        if len(output_list)==0:
            not_use_output_pin.append(ivalue)

        for kvalue in cell_dict[ivalue]:
            new_cell_dict.update({ivalue.split(' ')[1]+' '+kvalue:{'direction':cell_dict[ivalue][kvalue]['direction'],'type':'cell','cell_type':str(),'macroID':ivalue.split(' ')[0]}})

            if new_cell_dict[ivalue.split(' ')[1]+' '+kvalue]['direction']=='INPUT':
                if cell_dict[ivalue][kvalue]['from'] in nets:
                    nets[cell_dict[ivalue][kvalue]['from']]['to'].append(ivalue.split(' ')[1]+' '+kvalue)
                elif cell_dict[ivalue][kvalue]['from'] in input_pins:
                    input_pins[cell_dict[ivalue][kvalue]['from']]['to'].append(ivalue.split(' ')[1]+' '+kvalue)
                else:
                    if cell_dict[ivalue][kvalue]['from'] in recursive_ivalue:
                        recursive_ivalue[cell_dict[ivalue][kvalue]['from']]['to'].append(ivalue.split(' ')[1]+' '+kvalue)
                    else:
                        recursive_ivalue.update({cell_dict[ivalue][kvalue]['from']:{'to':[],'from':[]}})
                        recursive_ivalue[cell_dict[ivalue][kvalue]['from']]['to'].append(ivalue.split(' ')[1]+' '+kvalue)

                new_cell_dict[ivalue.split(' ')[1]+' '+kvalue].update({'to':output_list})

            else:
                if cell_dict[ivalue][kvalue]['to'] in nets:
                    nets[cell_dict[ivalue][kvalue]['to']]['from'].append(ivalue.split(' ')[1]+' '+kvalue)
                else:
                    output_pins[cell_dict[ivalue][kvalue]['to']]['from'].append(ivalue.split(' ')[1]+' '+kvalue)


                new_cell_dict[ivalue.split(' ')[1]+' '+kvalue].update({'from':input_list})

            macro_info=libAdrress+ivalue.split(' ')[0]+'/1_description.txt'
            filefile=open(macro_info,'r')
            strings=filefile.readlines()
            filefile.close()
            new_cell_dict[ivalue.split(' ')[1]+' '+kvalue]['cell_type']=strings[0]
        



    for ivalue in output_pins:
        if ivalue in recursive_ivalue:
            recursive_ivalue[ivalue]['from'].append(output_pins[ivalue]['from'][0])


    for ivalue in input_pins:
        new_cell_dict.update({ivalue:{'direction':'OUTPUT','type':'pin','from':[],'to':[]}})
        for kdx in range(len(input_pins[ivalue]['to'])):
            new_cell_dict[ivalue]['to'].append(input_pins[ivalue]['to'][kdx])
            new_cell_dict[input_pins[ivalue]['to'][kdx]].update({'from':[ivalue]})


    for ivalue in output_pins:
        new_cell_dict.update({ivalue:{'direction':'INPUT','type':'pin','from':[output_pins[ivalue]['from'][0]],'to':[]}})
        new_cell_dict[output_pins[ivalue]['from'][0]].update({'to':[ivalue]})

        if ivalue in recursive_ivalue:
            new_cell_dict.update({ivalue:{'direction':'INPUT','type':'pin','from':[recursive_ivalue[ivalue]['from'][0]],'to':[]}})
            nets.update({ivalue:recursive_ivalue[ivalue]})


    for ivalue in nets:

        for kdx in range(len(nets[ivalue]['to'])):
            new_cell_dict[nets[ivalue]['to'][kdx]].update({'from':[nets[ivalue]['from'][0]]})

        if 'to' in new_cell_dict[nets[ivalue]['from'][0]]:
            for kdx in range(len(nets[ivalue]['to'])):
                new_cell_dict[nets[ivalue]['from'][0]]['to'].append(nets[ivalue]['to'][kdx])
        else:
            new_cell_dict[nets[ivalue]['from'][0]].update({'to':nets[ivalue]['to']})





    return new_cell_dict     






def get_unconnect(nets,lib):
    clk_groups=dict()
    group_of_clk=list()
    ck_port_group=list()

    for ivalue in nets:
        if nets[ivalue]['type']=='cell':
            if nets[ivalue]['cell_type']=='Pos.edge D-Flip-Flop':
                if nets[ivalue]['direction']=='OUTPUT':
                    nets[ivalue]['from']=[]
                    df_output=pd.read_csv(lib+nets[ivalue]['macroID']+'/3_output_'+ivalue.split(' ')[1]+'/0_info.tsv',sep='\t')
                    conditionlist=list(df_output[ivalue.split(' ')[1]])
                    for jdx in range(len(conditionlist)):
                        if 'unateness : non_unate' in conditionlist[jdx]:
                            if conditionlist[jdx].split('related_pin : ')[1].split(', unateness')[0] not in ck_port_group:
                                ck_port_group.append(conditionlist[jdx].split('related_pin : ')[1].split(', unateness')[0])


    for ivalue in nets:
        if nets[ivalue]['type']=='cell':
            if nets[ivalue]['cell_type']=='Pos.edge D-Flip-Flop':
                if nets[ivalue]['direction']=='INPUT':
                    nets[ivalue]['to']=[]
                    if ivalue.split(' ')[1] in ck_port_group:
                        group_of_clk.append(ivalue)
                        checking_clk=nets[ivalue]['from'][0]
                        while len(nets[checking_clk]['from'])!=0:
                            if checking_clk not in group_of_clk:
                                group_of_clk.append(checking_clk)
                            input__checking=nets[checking_clk]['from'][0]
                            if input__checking not in group_of_clk:
                                group_of_clk.append(input__checking)
                            checking_clk=nets[input__checking]['from'][0]
                        if checking_clk not in group_of_clk:
                            group_of_clk.append(checking_clk)



            elif nets[ivalue]['cell_type']=='MACRO':
                if nets[ivalue]['direction']=='OUTPUT':

                    nets[ivalue]['from']=[]
                else:
                    nets[ivalue]['to']=[]


    for idx in range(len(group_of_clk)):
        clk_groups.update({group_of_clk[idx]:nets[group_of_clk[idx]]})
        del nets[group_of_clk[idx]]
    return [clk_groups,nets]



################################ cycle이 있는지 확인하는 함수 필요
def checking_input_list_new(All,dict_dict,input_one):
    if input_one in dict_dict:
        print()
        print('비상비상비상_______사이클_존재_______비상비상비상')
        print(dict_dict)
        print('비상비상비상_______사이클_존재_______비상비상비상')
        print()

        return 0
    
    temp_dict=dict()
    temp_dict.update({input_one:{}})

    for ivalue in All[input_one]['to']:
        temp_dict[input_one].update({ivalue:[]})
        for kvalue in All[ivalue]['to']:

            if len(All[kvalue]['to'])!=0:
                temp_dict[input_one][ivalue].append(kvalue)

        if len(temp_dict[input_one][ivalue])==0:
            del temp_dict[input_one][ivalue]

    if len(temp_dict[input_one])==0:
        temp_dict=dict()

        checking_input=copy.deepcopy(input_one)
        temptemp=copy.deepcopy(dict_dict)

        for idx in range(len(temptemp)):
            for ivalue in temptemp:
                
                if ivalue in dict_dict:

                    for kvalue in temptemp[ivalue]:

                        if kvalue in dict_dict[ivalue]:

                            for jvalue in temptemp[ivalue][kvalue]:

                                if jvalue in dict_dict[ivalue][kvalue]:

                                    if jvalue==checking_input:
                                        dict_dict[ivalue][kvalue].remove(jvalue)
                                
                            if len(dict_dict[ivalue][kvalue])==0:
                                del dict_dict[ivalue][kvalue]
                    
                    if len(dict_dict[ivalue])==0:
                        checking_input=ivalue
                        del dict_dict[ivalue]
    
    else:
        remain_list=list()
        for ivalue in temp_dict[input_one]:
            for kvalue in temp_dict[input_one][ivalue]:
                remain_list.append(kvalue)
        
        kkk=int()
        for ivalue in remain_list:
            kkk=kkk+1
            for kvalue in dict_dict:
                if ivalue.split(' ')[0]==kvalue.split(' ')[0]:
                    print()
                    print('비상비상비상_______사이클_존재_______비상비상비상')
                    print(dict_dict)
                    print('비상비상비상_______사이클_존재_______비상비상비상')
                    print()
                    return 0

        if kkk==len(remain_list):
            dict_dict.update(temp_dict)
            for idx in range(len(remain_list)):
                dict_dict=checking_input_list_new(All,dict_dict,remain_list[idx])

    return dict_dict
################################ cycle이 있는지 확인하는 함수 필요




def get_new_stage_nodes(TAll):
    All=copy.deepcopy(TAll)

    for ivalue in All:
        All[ivalue]['stage']=[None,None]
        if len(All[ivalue]['from'])==0:
            All[ivalue]['stage']=[0,'OUTPUT']


    for ivalue in All:
        if All[ivalue]['stage']==[0,'OUTPUT']:
            for kdx in range(len(All[ivalue]['to'])):
                All[All[ivalue]['to'][kdx]]['stage']=[0,'INPUT']
    

    current_stage=1
    while True:
        rrr=int()
        willget_stage_input=list()

        for ivalue in All:
            if All[ivalue]['stage']==[None,None]:
                rrr=rrr+1

            
            if (All[ivalue]['direction']=='OUTPUT' and All[ivalue]['stage']==[None,None]):
                check_number_of_stage=int()
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






if __name__ == "__main__":
    where_the_verilog='../data/deflef_to_graph_and_verilog/verilog/'+sys.argv[1]
    where_the_lib='../data/deflef_to_graph_and_verilog/libs/'+sys.argv[2].split('.lib')[0]+'/'

    where_the_hypergraph='../data/deflef_to_graph_and_verilog/hypergraph/'

    directory_name=where_the_verilog.split('/')[-1].split('.v')[0]+'_'+sys.argv[2].split('.lib')[0]

    if directory_name not in os.listdir(where_the_hypergraph):
        os.mkdir(where_the_hypergraph+directory_name)
    file_save_address_stage_without_clk=where_the_hypergraph+directory_name+'/stage_without_clk.pickle'
    file_save_address_stage_with_clk=where_the_hypergraph+directory_name+'/stage_with_clk.pickle'

    net_info=dict()
    unconnect_graph=list()

    start = time.time()
    
    net_info=get_each_cell(where_the_verilog,where_the_lib)
    unconnect_graph=get_unconnect(net_info,where_the_lib)
    stage_without_clk=get_new_stage_nodes(unconnect_graph[1])
    stage_with_clk=get_new_stage_nodes(unconnect_graph[0])

    with open(file_save_address_stage_without_clk,'wb') as fw:
        pickle.dump(stage_without_clk, fw)
    fw.close()

    with open(file_save_address_stage_with_clk,'wb') as fw:
        pickle.dump(stage_with_clk, fw)
    fw.close()

    print("time :", time.time() - start)