
import json
from optparse import check_choice
from re import sub
from turtle import update
from unicodedata import name
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import json
import copy
import scipy
import pickle
from networkx.drawing.nx_pydot import graphviz_layout
from networkx.algorithms import tournament
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph
import pygraphviz as pgv
import pandas as pd
import plotly.express as px

import os
import pathlib



######################################################## idx=[51,52], [151,152], [154,155]
def get_type_of_macro(file_address):
    count=0
    for item in os.listdir(file_address):
        sub_folder = os.path.join(file_address,item)
        if os.path.isdir(sub_folder):
            macro_file=sub_folder
            path_of_macro_info=macro_file+'/1. macro_info.tsv'
            df=pd.read_csv(path_of_macro_info,sep='\t')
            for kdx in range(df.shape[0]):
                if 'macro_type' in df.values[kdx]:
                    type_of_macro=str(df.values[kdx]).split(" '")[1].split("']")[0]
                if 'macro_id' in df.values[kdx]:
                    name_of_macro=str(df.values[kdx]).split(" '")[1].split("']")[0]
                if 'Input' in df.values[kdx]:
                    input_list=((df.values[kdx])[1].replace(',',"").replace("['","").replace("']","").split(" "))
                if 'Output' in df.values[kdx]:
                    output_list=((df.values[kdx])[1].replace(',',"").replace("['","").replace("']","").split(" "))
            if type_of_macro=='Combinational':

                all_macro_info=list()
                for ktem in os.listdir(macro_file):
                    ##if (ktem.split(". ")[0]) == '3':
                    if (ktem.split(". ")[0]) == '4':    
                        delaytable_path=macro_file+"/"+ktem
                        info_of_table=dict()
                        load_capacitance=list()
                        all_data_list=list()
                        fall_data=list()
                        rise_data=list()
                        input_transition=list()
                        port_to_port=str()
                        df=pd.read_csv(delaytable_path, sep='\t')
                        for jdx in range(len(list(df.values))):
                            if jdx ==0:
                                if list(df.values[jdx]) in load_capacitance:
                                    continue
                                else:
                                    load_capacitance.append(list(df.values[jdx]))
                            elif jdx <= 7:
                                fall_data.append(list(df.values[jdx]))
                            else:
                                rise_data.append(list(df.values[jdx]))
                        port_to_port=list(df.values)[1][0]
                        load_capacitance=load_capacitance[0][4:11]
                        
                        for tdx in range(7):
                            data_list=list()
                            for rdx in range(7):
                                if fall_data[tdx][rdx+4]<rise_data[tdx][rdx+4]:
                                    data_list.append(rise_data[tdx][rdx+4])
                                else:
                                    data_list.append(fall_data[tdx][rdx+4])
                            
                            
                            
                            all_data_list.append(list(data_list))
                            
                    
                        for tidx in range(7):
                            input_transition.append(list(df.values)[tidx+1][3])


                        info_of_table={ktem:[port_to_port,input_transition,load_capacitance,all_data_list]}
                        all_macro_info.append(info_of_table)
            

            
                group_of_number=list()
                update_list=list()
                ppport_to=list()
                for qdx in range(len(input_list)):
                    for wdx in range(len(output_list)):
                        number_of_port_to_port=int()
                        for edx in range(len(all_macro_info)):
                            if list(all_macro_info[edx].values())[0][0] == input_list[qdx]+" to "+output_list[wdx]:
                                number_of_port_to_port=number_of_port_to_port+1
                                update_list.append(list(all_macro_info[edx].values())[0][3])
                        ppport_to.append(input_list[qdx]+" to "+output_list[wdx])
                        group_of_number.append(number_of_port_to_port)


            


                num=int()
                checking_table1=list()
                checking_table2=list()
                data_tables=list()
                for groupidx in range(len(group_of_number)):

                        for one_portidx in range(group_of_number[groupidx]):
                            if group_of_number[groupidx] !=1:
                                checking_table1=update_list[num]
                                if one_portidx ==0:
                                    continue
                                else:
                                    checking_table2=update_list[num+one_portidx]
                                    for zxcv in range(7):
                                        for vczx in range(7):
                                            if checking_table1[vczx][zxcv] > checking_table2[vczx][zxcv]:
                                                continue
                                            else:
                                                checking_table1[vczx][zxcv] = checking_table2[vczx][zxcv]
                            else:
                                checking_table1=update_list[num+one_portidx]

                        num=num+group_of_number[groupidx]
                        data_tables.append(checking_table1)


                for asdfidx in range(len(data_tables)):
                    multi_index0=list()
                    multi_index1=list()
                    multi_index2=list()
                    for dddidx in range(7):
                        multi_index0.append(ppport_to[asdfidx])
                        multi_index1.append('input_transition')
                    multi_index2=input_transition
                    multi_columns=list()
                    for dddidx in range(7):
                        ##multi_columns.append('load_capacitacne / propagation_delay')
                        multi_columns.append('load_capacitacne / output_transition')
                    df2=pd.DataFrame(data_tables[asdfidx],index=[multi_index0,multi_index1,multi_index2],columns=multi_columns)
                    ##new_file=macro_file+'/9. Apporximate_Delay: '+ppport_to[asdfidx]+'.tsv'
                    new_file=macro_file+'/10. approximate_Output_Transition: '+ppport_to[asdfidx]+'.tsv'
                    df2.to_csv(new_file,sep="\t")
                

            if name_of_macro=='DFF_X1' or name_of_macro=='DFF_X2':
                all_macro_info=list()
                for ktem in os.listdir(macro_file):
                    if (ktem.split(". ")[0]) == '4':  
                        delaytable_path=macro_file+"/"+ktem
                        info_of_table=dict()
                        load_capacitance=list()
                        all_data_list=list()
                        fall_data=list()
                        rise_data=list()
                        input_transition=list()
                        port_to_port=str()
                        realdatalist=list()
                        df=pd.read_csv(delaytable_path, sep='\t')
                        for jdx in range(len(list(df.values))):
                            if jdx ==0:
                                if list(df.values[jdx]) in load_capacitance:
                                    continue
                                else:
                                    load_capacitance.append(list(df.values[jdx]))
                            elif jdx <= 7:
                                fall_data.append(list(df.values[jdx]))
                            else:
                                rise_data.append(list(df.values[jdx]))
                        port_to_port=list(df.values)[1][0]
                        load_capacitance=load_capacitance[0][4:11]


                        for ddffaa in range(7):
                            for ddffbb in range(7):
                                if rise_data[ddffaa][ddffbb+4]>fall_data[ddffaa][ddffbb+4]:
                                    realdatalist.append(rise_data[ddffaa][ddffbb+4])
                                else:
                                    realdatalist.append(fall_data[ddffaa][ddffbb+4])

                        data_list=list()
                        for ddffaa in range(7):
                            data_list.append(realdatalist[ddffaa*7:ddffaa*7+7])


                        for tidx in range(7):
                            input_transition.append(list(df.values)[tidx+1][3])





                        multi_index0=list() 
                        multi_index1=list()
                        multi_index2=list()
                        for dddidx in range(7):
                            multi_index0.append(port_to_port+' (rise)')
                            multi_index1.append('input_transition')
                        multi_index2=input_transition
                        multi_columns=list()
                        for dddidx in range(7):
                            multi_columns.append('load_capacitacne / output_transition')
                        df2=pd.DataFrame(data_list,index=[multi_index0,multi_index1,multi_index2],columns=[multi_columns,list(df.iloc[0,4:11])])
                        new_file=macro_file+'/10. approximate_Output_Transition: '+port_to_port+'.tsv'
                        df2.to_csv(new_file,sep="\t")

    return 0









def get_type_of_macro22(file_address):
    count=0
    for item in os.listdir(file_address):
        sub_folder = os.path.join(file_address,item)
        if os.path.isdir(sub_folder):
            macro_file=sub_folder
            path_of_macro_info=macro_file+'/1. macro_info.tsv'
            df=pd.read_csv(path_of_macro_info,sep='\t')
            for kdx in range(df.shape[0]):
                if 'macro_type' in df.values[kdx]:
                    type_of_macro=str(df.values[kdx]).split(" '")[1].split("']")[0]
                if 'macro_id' in df.values[kdx]:
                    name_of_macro=str(df.values[kdx]).split(" '")[1].split("']")[0]
                if 'Input' in df.values[kdx]:
                    input_list=((df.values[kdx])[1].replace(',',"").replace("['","").replace("']","").split(" "))
                if 'Output' in df.values[kdx]:
                    output_list=((df.values[kdx])[1].replace(',',"").replace("['","").replace("']","").split(" "))
            if type_of_macro=='Combinational':

                all_macro_info=list()
                for ktem in os.listdir(macro_file):
                    if (ktem.split(". ")[0]) == '3':
  
                        delaytable_path=macro_file+"/"+ktem
                        info_of_table=dict()
                        load_capacitance=list()
                        all_data_list=list()
                        fall_data=list()
                        rise_data=list()
                        input_transition=list()
                        port_to_port=str()
                        df=pd.read_csv(delaytable_path, sep='\t')
                        for jdx in range(len(list(df.values))):
                            if jdx ==0:
                                if list(df.values[jdx]) in load_capacitance:
                                    continue
                                else:
                                    load_capacitance.append(list(df.values[jdx]))
                            elif jdx <= 7:
                                fall_data.append(list(df.values[jdx]))
                            else:
                                rise_data.append(list(df.values[jdx]))
                        port_to_port=list(df.values)[1][0]
                        load_capacitance=load_capacitance[0][4:11]
                        
                        for tdx in range(7):
                            data_list=list()
                            for rdx in range(7):
                                if fall_data[tdx][rdx+4]<rise_data[tdx][rdx+4]:
                                    data_list.append(rise_data[tdx][rdx+4])
                                else:
                                    data_list.append(fall_data[tdx][rdx+4])
                            
                            
                            
                            all_data_list.append(list(data_list))
                            
                    
                        for tidx in range(7):
                            input_transition.append(list(df.values)[tidx+1][3])


                        info_of_table={ktem:[port_to_port,input_transition,load_capacitance,all_data_list]}
                        all_macro_info.append(info_of_table)
            

            
                group_of_number=list()
                update_list=list()
                ppport_to=list()
                for qdx in range(len(input_list)):
                    for wdx in range(len(output_list)):
                        number_of_port_to_port=int()
                        for edx in range(len(all_macro_info)):
                            if list(all_macro_info[edx].values())[0][0] == input_list[qdx]+" to "+output_list[wdx]:
                                number_of_port_to_port=number_of_port_to_port+1
                                update_list.append(list(all_macro_info[edx].values())[0][3])
                        ppport_to.append(input_list[qdx]+" to "+output_list[wdx])
                        group_of_number.append(number_of_port_to_port)


            


                num=int()
                checking_table1=list()
                checking_table2=list()
                data_tables=list()
                for groupidx in range(len(group_of_number)):

                        for one_portidx in range(group_of_number[groupidx]):
                            if group_of_number[groupidx] !=1:
                                checking_table1=update_list[num]
                                if one_portidx ==0:
                                    continue
                                else:
                                    checking_table2=update_list[num+one_portidx]
                                    for zxcv in range(7):
                                        for vczx in range(7):
                                            if checking_table1[vczx][zxcv] > checking_table2[vczx][zxcv]:
                                                continue
                                            else:
                                                checking_table1[vczx][zxcv] = checking_table2[vczx][zxcv]
                            else:
                                checking_table1=update_list[num+one_portidx]

                        num=num+group_of_number[groupidx]
                        data_tables.append(checking_table1)


                for asdfidx in range(len(data_tables)):
                    multi_index0=list()
                    multi_index1=list()
                    multi_index2=list()
                    for dddidx in range(7):
                        multi_index0.append(ppport_to[asdfidx])
                        multi_index1.append('input_transition')
                    multi_index2=input_transition
                    multi_columns=list()
                    for dddidx in range(7):
                        multi_columns.append('load_capacitacne / propagation_delay')
                    df2=pd.DataFrame(data_tables[asdfidx],index=[multi_index0,multi_index1,multi_index2],columns=multi_columns)
                    new_file=macro_file+'/9. approximate_Delay: '+ppport_to[asdfidx]+'.tsv'
                    df2.to_csv(new_file,sep="\t")
                



            if name_of_macro=='DFF_X1' or name_of_macro=='DFF_X2':
                all_macro_info=list()
                for ktem in os.listdir(macro_file):
                    if (ktem.split(". ")[0]) == '3':  
                        delaytable_path=macro_file+"/"+ktem
                        info_of_table=dict()
                        load_capacitance=list()
                        all_data_list=list()
                        fall_data=list()
                        rise_data=list()
                        input_transition=list()
                        port_to_port=str()
                        realdatalist=list()
                        df=pd.read_csv(delaytable_path, sep='\t')
                        
                        for jdx in range(len(list(df.values))):
                            if jdx ==0:
                                if list(df.values[jdx]) in load_capacitance:
                                    continue
                                else:
                                    load_capacitance.append(list(df.values[jdx]))
                            elif jdx <= 7:
                                fall_data.append(list(df.values[jdx]))
                            else:
                                rise_data.append(list(df.values[jdx]))
                        port_to_port=list(df.values)[1][0]
                        load_capacitance=load_capacitance[0][4:11]




                        for ddffaa in range(7):
                            for ddffbb in range(7):
                                if rise_data[ddffaa][ddffbb+4]>fall_data[ddffaa][ddffbb+4]:
                                    realdatalist.append(rise_data[ddffaa][ddffbb+4])
                                else:
                                    realdatalist.append(fall_data[ddffaa][ddffbb+4])

                        data_list=list()
                        for ddffaa in range(7):
                            data_list.append(realdatalist[ddffaa*7:ddffaa*7+7])


                        for tidx in range(7):
                            input_transition.append(list(df.values)[tidx+1][3])



                        multi_index0=list() 
                        multi_index1=list()
                        multi_index2=list()
                        for dddidx in range(7):
                            multi_index0.append(port_to_port+' (rise)')
                            multi_index1.append('input_transition')
                        multi_index2=input_transition
                        multi_columns=list()
                        for dddidx in range(7):
                            multi_columns.append('load_capacitacne / propagation_delay')
                        df2=pd.DataFrame(data_list,index=[multi_index0,multi_index1,multi_index2],columns=[multi_columns,list(df.iloc[0,4:11])])
                        new_file=macro_file+'/9. approximate_Delay: '+port_to_port+'.tsv'
                        df2.to_csv(new_file,sep="\t")

    return 0




def get_FA_X1_right(file_address):
    for item in os.listdir(file_address):
        sub_folder = os.path.join(file_address,item)
        if os.path.isdir(sub_folder):
            macro_file=sub_folder
            path_of_macro_info=macro_file+'/1. macro_info.tsv'
            df=pd.read_csv(path_of_macro_info,sep='\t')
            for kdx in range(df.shape[0]):
                if 'macro_type' in df.values[kdx]:
                    type_of_macro=str(df.values[kdx]).split(" '")[1].split("']")[0]
                if 'macro_id' in df.values[kdx]:
                    name_of_macro=str(df.values[kdx]).split(" '")[1].split("']")[0]
            if type_of_macro=='Combinational':
                if name_of_macro != "FA_X1":
                    continue
                else:
                    new_file=macro_file+'/1. macro_info.tsv'
                    ddff=copy.deepcopy(df)
                    ddff['info'][3]="['A, B, CI']"
                    indexindex=list(ddff['Unnamed: 0'])
                    datadata=list()
                    for idx in range(len(list(ddff['info']))):
                        datadata.append([list(ddff['info'])[idx]])

                    columnscolumns=['info']
                    dddfff=pd.DataFrame(data=datadata, index=indexindex, columns=columnscolumns)
                    dddfff.to_csv(new_file,sep="\t")


    return 0



def get_del(file_address):
    for item in os.listdir(file_address):
        sub_folder = os.path.join(file_address,item)
        if os.path.isdir(sub_folder):
            macro_file=sub_folder
            path_of_macro_info=macro_file+'/1. macro_info.tsv'
            df=pd.read_csv(path_of_macro_info,sep='\t')
            for kdx in range(df.shape[0]):
                if 'macro_type' in df.values[kdx]:
                    type_of_macro=str(df.values[kdx]).split(" '")[1].split("']")[0]
                if 'macro_id' in df.values[kdx]:
                    name_of_macro=str(df.values[kdx]).split(" '")[1].split("']")[0]
                if 'Input' in df.values[kdx]:
                    input_list=((df.values[kdx])[1].replace(',',"").replace("['","").replace("']","").split(" "))
                if 'Output' in df.values[kdx]:
                    output_list=((df.values[kdx])[1].replace(',',"").replace("['","").replace("']","").split(" "))
            if type_of_macro=='Combinational':

                all_macro_info=list()
                for ktem in os.listdir(macro_file):
                    if ktem.split(" ")[1]=='Apporximate_Output_Transition:' or ktem.split(" ")[1]=='approrximate_Delay:':
                
                        os.remove(macro_file+"/"+ktem)
    
    return 0

if __name__ == "__main__":
    file='../data/macro_info_nangate_fast'
    one=get_FA_X1_right(file)
    two=get_type_of_macro(file)
    three=get_type_of_macro22(file)
    deldel=get_del(file)


