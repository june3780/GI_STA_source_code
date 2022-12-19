import pandas as pd
import os
import json
import numpy as np
import sys


def get_table(df1):
    dict_of_table=dict()

    load_capacitance_list=list(df1.columns)[1:]
    input_transition_list=list(df1['Unnamed: 0'])
    data_list=list()
    for idx in range(len(load_capacitance_list)):
        data_list.append(list(df1[load_capacitance_list[idx]]))
        load_capacitance_list[idx]=float(load_capacitance_list[idx])
    dict_of_table.update({'load_capacitance':load_capacitance_list,'input_transition':input_transition_list,'data_list':data_list})
    return dict_of_table






def get_lib_list(file_address):
    kkk=int()
    list_of_directory=list()
    dictionary_of_lib=dict()
    list_of_directory=os.listdir(file_address)

    if 'dictionary_of_lib.json' in list_of_directory:
        list_of_directory.remove('dictionary_of_lib.json')
    if 'dictionary_of_lib_without_input.json' in list_of_directory:
        list_of_directory.remove('dictionary_of_lib_without_input.json')


    for ivalue in list_of_directory:
        temp_ivalue=file_address+ivalue
        temp_list_of_os=os.listdir(temp_ivalue)




        temp_description_address=temp_ivalue+'/1_description.txt'

        if '1_description.txt' not in temp_list_of_os:
            continue
        temp_file=open(temp_description_address,'r')
        strings=temp_file.readline()
        temp_file.close()

        temp_input_list_of_macro=list()
        for kvalue in temp_list_of_os:
            if '2_input_' in kvalue:
                temp_input_list_of_macro.append(kvalue.split('2_input_')[1].split('.tsv')[0])
        
        temp_output_list_of_macro=dict()
        for kvalue in temp_list_of_os:
            if '3_output_' in kvalue:
                temp_output_list_of_macro.update({kvalue.split('3_output_')[1]:{}})

            
        dictionary_of_lib.update({ivalue:{'description':strings,'input':{},'output':{}}})
################################################################################################################################
        for kvalue in temp_output_list_of_macro:
            temp_output_kvalue_df=pd.read_csv(temp_ivalue+'/3_output_'+kvalue+'/0_info.tsv',sep='\t')
            temp_output_kvalue_df[kvalue]=temp_output_kvalue_df[kvalue].fillna(str(''))
            max_capa=list(temp_output_kvalue_df[kvalue])[0]
            dictionary_of_lib[ivalue]['output'].update({kvalue:{'max_capacitance':max_capa}})

            temp_function=str('')
            condition_list=list()
            if strings !='Constant cell':
                temp_function=list(temp_output_kvalue_df[kvalue])[1]
                condition_list=list(temp_output_kvalue_df[kvalue])[2:]
            else:
                condition_list=['condition : No condition, related_pin : nothing, unateness : non_unate']
                
            dictionary_of_lib[ivalue]['output'][kvalue].update({'function':temp_function})
            dictionary_of_lib[ivalue]['output'][kvalue].update({'conditionlist':condition_list})

            if strings !='Constant cell':
                if strings !='MACRO':
                    dictionary_of_lib[ivalue]['output'][kvalue].update({'type':'table'})
                    for jdx in range(len(dictionary_of_lib[ivalue]['output'][kvalue]['conditionlist'])):
                        kkk=kkk+1
                        fall_delay_df=pd.read_csv(temp_ivalue+'/3_output_'+kvalue+'/condition_'+str(jdx)+'_cell_fall.tsv',sep='\t')
                        fall_delay=get_table(fall_delay_df)
                        rise_delay_df=pd.read_csv(temp_ivalue+'/3_output_'+kvalue+'/condition_'+str(jdx)+'_cell_rise.tsv',sep='\t')
                        rise_delay=get_table(rise_delay_df)
                        fall_transition_df=pd.read_csv(temp_ivalue+'/3_output_'+kvalue+'/condition_'+str(jdx)+'_fall_transition.tsv',sep='\t')
                        fall_transition=get_table(fall_transition_df)
                        rise_transition_df=pd.read_csv(temp_ivalue+'/3_output_'+kvalue+'/condition_'+str(jdx)+'_rise_transition.tsv',sep='\t')
                        rise_transition=get_table(rise_transition_df)
                        dictionary_of_lib[ivalue]['output'][kvalue].update({'condition_'+str(jdx):{'fall_delay':fall_delay,'rise_delay':rise_delay}})
                        dictionary_of_lib[ivalue]['output'][kvalue]['condition_'+str(jdx)].update({'fall_transition':fall_transition,'rise_transition':rise_transition})

                else:
                    dictionary_of_lib[ivalue]['output'][kvalue].update({'type':'scalar'})
                    if 'unateness : complex' in dictionary_of_lib[ivalue]['output'][kvalue]['conditionlist'][0]:
                        dictionary_of_lib[ivalue]['output'][kvalue].update({'condition_'+str(0):{'fall_delay':float(0),'rise_delay':float(0)}})
                        dictionary_of_lib[ivalue]['output'][kvalue]['condition_'+str(0)].update({'fall_transition':float(0),'rise_transition':float(0)})

                    else:
                        file_fall_delay=temp_ivalue+'/3_output_'+kvalue+'/condition_'+str(0)+'_cell_fall.txt'
                        filefile=open(file_fall_delay,'r')
                        temp_text=filefile.readline()
                        fall_delay_df=float(temp_text)
                        filefile.close()

                        file_rise_delay=temp_ivalue+'/3_output_'+kvalue+'/condition_'+str(0)+'_cell_rise.txt'
                        filefile=open(file_rise_delay,'r')
                        temp_text=filefile.readline()
                        rise_delay_df=float(temp_text)
                        filefile.close()

                        file_fall_tran=temp_ivalue+'/3_output_'+kvalue+'/condition_'+str(0)+'_fall_transition.txt'
                        filefile=open(file_fall_tran,'r')
                        temp_text=filefile.readline()
                        fall_transition_df=float(temp_text)
                        filefile.close()

                        file_rise_tran=temp_ivalue+'/3_output_'+kvalue+'/condition_'+str(0)+'_rise_transition.txt'
                        filefile=open(file_rise_tran,'r')
                        temp_text=filefile.readline()
                        rise_transition_df=float(temp_text)
                        filefile.close()

                        dictionary_of_lib[ivalue]['output'][kvalue].update({'condition_'+str(0):{'fall_delay':fall_delay_df,'rise_delay':rise_delay_df}})
                        dictionary_of_lib[ivalue]['output'][kvalue]['condition_'+str(0)].update({'fall_transition':fall_transition_df,'rise_transition':rise_transition_df})
            
            else:
                dictionary_of_lib[ivalue]['output'][kvalue].update({'type':'scalar'})
                dictionary_of_lib[ivalue]['output'][kvalue].update({'condition_'+str(0):{'fall_delay':float(0),'rise_delay':float(0)}})
                dictionary_of_lib[ivalue]['output'][kvalue]['condition_'+str(0)].update({'fall_transition':float(0),'rise_transition':float(0)})

################################################################################################################################
        for kvalue in temp_input_list_of_macro:
            df1=pd.read_csv(temp_ivalue+'/2_input_'+kvalue+'.tsv',sep='\t')
            fall_capa=float(list(df1[kvalue])[0])
            rise_capa=float(list(df1[kvalue])[1])
            dictionary_of_lib[ivalue]['input'].update({kvalue:{'fall_capacitance':fall_capa,'rise_capacitance':rise_capa}})
            ##print(json.dumps(dictionary_of_lib,indent=4))




    return dictionary_of_lib




if __name__ == "__main__":
    ##os.chdir('Documents/PNR/timing/source/')
    temp_lib=sys.argv[1].split('.lib')[0]
    address_liberty_file='../data/deflef_to_graph_and_verilog/libs/'
    address_liberty_file=address_liberty_file+temp_lib+'/'
    dict_of_lib=get_lib_list(address_liberty_file)

    saving_lib_address='../data/deflef_to_graph_and_verilog/libs/'
    saving_lib_address=saving_lib_address+temp_lib+'/'
    saving_lib_address=saving_lib_address+'dictionary_of_lib.json'
    with open(saving_lib_address,'w') as filee:
        json.dump(dict_of_lib,filee,indent=4)