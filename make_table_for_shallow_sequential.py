
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
    
    
    
            if type_of_macro=='Sequential':
                all_macro_info=list()
                print(macro_file)
                all_ports=list()
                for ktem in os.listdir(macro_file):
                
                    ##if (ktem.split(". ")[0]) == '3':
                    if (ktem.split(". ")[0]) == '5':    
                        delaytable_path=macro_file+"/"+ktem

                        clock_transition=list()
                        all_data_list=list()
                        fall_data=list()
                        rise_data=list()
                        fall_or_rise_list=list()
                        port_to_port=str()
                        portlist=list()

                        df=pd.read_csv(delaytable_path, sep='\t')
                        for jdx in range(len(list(df.values))):

                            if jdx ==0:
                                    clock_transition.append(list(df.values[jdx])[4:7])
                            elif jdx <= 3:
                                fall_data.append(list(df.values[jdx])[4:7])
                            else:
                                rise_data.append(list(df.values[jdx])[4:7])
                                fall_rise_of_clk=list(df.values[jdx])[1]


                        clock_transition=clock_transition[0]  
                        
                        port_to_port=list(df.values)[1][0]
                        all_ports.append(port_to_port)
                        

                        for tdx in range(3):
                            data_list=list()
                            for rdx in range(3):
                                if fall_data[tdx][rdx]<rise_data[tdx][rdx]:
                                    data_list.append(rise_data[tdx][rdx])
                                else:
                                    data_list.append(fall_data[tdx][rdx])
                            all_data_list.append(list(data_list))

                        for ddix in range(3):
                            portlist.append(port_to_port)

                    
                        for tidx in range(3):
                            fall_or_rise_list.append(fall_rise_of_clk)


                        df2=pd.DataFrame(data=all_data_list, index=[portlist,fall_or_rise_list,['data_transition','data_transition','data_transition'],clock_transition], columns=[['clock_transition / setup_time','clock_transition / setup_time','clock_transition / setup_time'],clock_transition])
                        saving=macro_file+"/11. approximate_Setup_Time: "+port_to_port+".tsv"

                        df2.to_csv(saving,sep='\t')

    return 0




def get_ttype_of_macro(file_address):
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
    
    
    
            if type_of_macro=='Sequential':
                all_macro_info=list()
                print(macro_file)
                all_ports=list()
                for ktem in os.listdir(macro_file):
                
                    ##if (ktem.split(". ")[0]) == '3':
                    if (ktem.split(". ")[0]) == '6':    
                        delaytable_path=macro_file+"/"+ktem

                        clock_transition=list()
                        all_data_list=list()
                        fall_data=list()
                        rise_data=list()
                        fall_or_rise_list=list()
                        port_to_port=str()
                        portlist=list()

                        df=pd.read_csv(delaytable_path, sep='\t')
                        for jdx in range(len(list(df.values))):

                            if jdx ==0:
                                    clock_transition.append(list(df.values[jdx])[4:7])
                            elif jdx <= 3:
                                fall_data.append(list(df.values[jdx])[4:7])
                            else:
                                rise_data.append(list(df.values[jdx])[4:7])
                                fall_rise_of_clk=list(df.values[jdx])[1]


                        clock_transition=clock_transition[0]  
                        
                        port_to_port=list(df.values)[1][0]
                        all_ports.append(port_to_port)
                        

                        for tdx in range(3):
                            data_list=list()
                            for rdx in range(3):
                                if fall_data[tdx][rdx]<rise_data[tdx][rdx]:
                                    data_list.append(rise_data[tdx][rdx])
                                else:
                                    data_list.append(fall_data[tdx][rdx])
                            all_data_list.append(list(data_list))

                        for ddix in range(3):
                            portlist.append(port_to_port)

                    
                        for tidx in range(3):
                            fall_or_rise_list.append(fall_rise_of_clk)


                        df2=pd.DataFrame(data=all_data_list, index=[portlist,fall_or_rise_list,['data_transition','data_transition','data_transition'],clock_transition], columns=[['clock_transition / hold_time','clock_transition / hold_time','clock_transition / hold_time'],clock_transition])
                        saving=macro_file+"/12. approximate_Hold_Time: "+port_to_port+".tsv"
                        

                        df2.to_csv(saving,sep='\t')
    return 0




if __name__ == "__main__":
    file='../data/macro_info_nangate_fast'

    two=get_type_of_macro(file)
    three=get_ttype_of_macro(file)



