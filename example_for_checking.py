from ast import arguments
import os
import shutil
import sys
import copy
import time


def get_file_and_make_directory(wiremode,file_type):

    idx=int()
    while True:
        defdef=str()
        defdef=get_limitation(file_type,idx)
        start=time.time()
        if defdef=='continue':
            idx=idx+1
            continue
    
        if defdef=='break':
            break
        defdef='gcd.def'
        if wiremode=='wire_load':
            print()
            print('revising')
            print()
            ##os.system('python3 0_revise_checking.py '+defdef)
            print()
            print('parsing')
            print()
            ##os.system('python3 1_for_check.py '+defdef)
        print()
        print('calculating')
        print()
        os.system('python3 2_for_modifying_graph.py '+defdef+' '+wiremode+' '+file_type)

        print(defdef,file_type,wiremode)
        ##print()
        idx=idx+1
        print()
        print('시간 :',time.time()-start)
        if idx>=1:
            break
    

    return 0






def copy_scratch(wirewire,defdef):
    file_path='../data/deflef_to_graph_and_verilog/results/'+defdef+'/test_7800_'+wirewire
    file_path_a1_bank='../data/deflef_to_graph_and_verilog/results/a1_bank/test_7800_'+wirewire+'/scratch_detailed.json'
    if 'scratch_detailed.json' not in os.listdir(file_path):
        shutil.copyfile(file_path_a1_bank,file_path+'/scratch_detailed.json')


    file_path='../data/deflef_to_graph_and_verilog/results/'+defdef+'/test_7800_without_clk_'+wirewire
    file_path_a1_bank='../data/deflef_to_graph_and_verilog/results/a1_bank/test_7800_without_clk_'+wirewire+'/scratch_detailed.json'
    if 'scratch_detailed.json' not in os.listdir(file_path):
        shutil.copyfile(file_path_a1_bank,file_path+'/scratch_detailed.json')


    file_path='../data/deflef_to_graph_and_verilog/results/'+defdef+'/test_7800_zfor_clk_'+wirewire
    file_path_a1_bank='../data/deflef_to_graph_and_verilog/results/a1_bank/test_7800_zfor_clk_'+wirewire+'/scratch_detailed.json'
    if 'scratch_detailed.json' not in os.listdir(file_path):
        shutil.copyfile(file_path_a1_bank,file_path+'/scratch_detailed.json')


    file_path='../data/deflef_to_graph_and_verilog/results/'+defdef+'/test_7800_'+wirewire+'_with_skew'
    file_path_a1_bank='../data/deflef_to_graph_and_verilog/results/a1_bank/test_7800_'+wirewire+'_with_skew/scratch_detailed.json'
    if 'scratch_detailed.json' not in os.listdir(file_path):
        shutil.copyfile(file_path_a1_bank,file_path+'/scratch_detailed.json')

    file_path='../data/deflef_to_graph_and_verilog/results/'+defdef+'/test_7800_zfor_clk_'+wirewire+'_with_skew'
    file_path_a1_bank='../data/deflef_to_graph_and_verilog/results/a1_bank/test_7800_zfor_clk_'+wirewire+'_with_skew/scratch_detailed.json'
    if 'scratch_detailed.json' not in os.listdir(file_path): 
        shutil.copyfile(file_path_a1_bank,file_path+'/scratch_detailed.json')

    return 0




def get_def_files(origin_of_def):
    kkiiddxx=int()
    doesnt_exist=list()
    while True:
        list_of_defs=os.listdir('../data/deflef_to_graph_and_verilog/0. defs')
        list_of_origins=os.listdir('../data/7809cells_groups/'+origin_of_def)

        checking=get_limitation(origin_of_def,kkiiddxx)

        target_in_origin=get_target_name(origin_of_def,kkiiddxx)

        if checking =='break':
            break
        
        elif checking =='continue':
            kkiiddxx=kkiiddxx+1
            continue

        elif checking.split('.def')[0] not in list_of_defs:
            if target_in_origin not in list_of_origins:
                print(target_in_origin+' does not exist')
                doesnt_exist.append(kkiiddxx)
            else:
                os.mkdir('../data/deflef_to_graph_and_verilog/0. defs/'+checking.split('.def')[0])
                shutil.copyfile('../data/7809cells_groups/'+origin_of_def+'/'+target_in_origin,'../data/deflef_to_graph_and_verilog/0. defs/'+checking.split('.def')[0]+'/'+checking)
                kkiiddxx=kkiiddxx+1
                continue


        kkiiddxx=kkiiddxx+1
    return doesnt_exist







def get_limitation(file_type,number):

        if get_file_name(file_type,number)[1]=='continue':
            return 'continue'

        elif get_file_name(file_type,number)[1]=='break':
            return 'break'

        else:
            return  get_file_name(file_type,number)[0]+'.def'







def get_target_name(checking,number):
    string1=str()
    if checking=='bank':
        string1=str(number)+'bank_detailed.def'
    elif checking=='rbank':
        string1=str(number)+'bank_detailed.def'
    elif checking=='random':
        string1='random'+str(number)+'_detailed.def'
    elif checking=='a1_bank':
        string1=str(number)+'bank.txt.def'
    elif checking=='a1_rbank':
        string1=str(number)+'rbank.txt.def'
    elif checking=='a2_bank':
        string1=str(number)+'bank.txt.def'
    elif checking=='a2_rbank':
        string1=str(number)+'rbank.txt.def'
    elif checking=='Rbank':
        string1='rbank'+str(number)+'.def'
    elif checking=='Rbank2':
        string1='rbank'+str(number)+'_detailed.def'
    elif checking=='random3':
        string1='random'+str(number)+'_detailed.def'
    elif checking=='Random':
        string1='random'+str(number)+'_detailed.def'
    elif checking=='Random2':
        string1='random'+str(number)+'_detailed.def'
    elif checking=='Random2_detailed':
        string1='random'+str(number)+'_detailed_detailed.def'

    return string1









def get_file_name(checking,number):
    

    file_name_of_path=str()
    if checking=='bank':
        file_name_of_path=str(number)+'bank_detailed'
    elif checking=='rbank':
        file_name_of_path=str(number)+'rbank_detailed'
    elif checking=='random':
        file_name_of_path='random'+str(number)+'_detailed'
    elif checking=='a1_bank':
        file_name_of_path='a1_'+str(number)+'bank.txt'
    elif checking=='a1_rbank':
        file_name_of_path='a1_'+str(number)+'rbank.txt'
    elif checking=='a2_bank':
        file_name_of_path='a2_'+str(number)+'bank.txt'
    elif checking=='a2_rbank':
        file_name_of_path='a2_'+str(number)+'rbank.txt'
    elif checking=='Rbank':
        file_name_of_path='rbank'+str(number)
    elif checking=='Rbank2':
        file_name_of_path='rbank'+str(number)+'_detailed'
    elif checking=='random3':
        file_name_of_path='3_random_'+str(number)
    elif checking=='Random':
        file_name_of_path='Random'+str(number)+'_detailed'
    elif checking=='Random2':
        file_name_of_path='Random1103_oneiter_'+str(number)+'_detailed'
    elif checking=='Random2_detailed':
        file_name_of_path='Random1103_oneiter_'+str(number)+'_detailed_detailed'


    strstr=str()
    if checking=='bank' and (number==25 or number==83):
        strstr='continue'

    elif (checking=='Rbank' or checking=='Rbank2') and (number==0 or number==1 or number==2):
        strstr='continue'


    if (number==103 and (checking=='Rbank' or checking=='Rbank2')):
        strstr='break'

    elif (number==100 and (checking=='bank' or checking=='rbank' or checking=='random' or checking=='random3' or checking=='Random' or checking=='Random2'or checking=='Random2_detailed')):
        strstr='break'

    elif (number==50 and (checking=='a1_bank' or checking=='a1_rbank')):
        strstr='break'

    elif (number==200 and (checking=='a2_bank' or checking=='a2_rbank')):
        strstr='break'



    return [file_name_of_path,strstr]






def get_CTS(set_of_file_types,wire_mode):
    list_of_file=list()
    start_end_list=list()
    rrr=int()
    start_end_list.append(rrr)
    for qqdd in range(len(set_of_file_types)):
        idx=int()
        while True:
            defdef=str()
            defdef=get_limitation(set_of_file_types[qqdd],idx)
            if defdef=='continue':
                idx=idx+1
                continue

            if defdef=='break':
                break

            list_of_file.append(defdef+' '+wire_mode+' '+set_of_file_types[qqdd])
            rrr=rrr+1
            idx=idx+1
        start_end_list.append(rrr-1)
        start_end_list.append(rrr)


    new_list=list()


    del start_end_list[-1]


    new_list=copy.deepcopy(list_of_file)

    for idx in range (len(new_list)):
        print(new_list[idx])
        os.system('python3 CTS.py '+new_list[idx])
        os.system('python3 making_def_with_cts.py '+new_list[idx])
        ##print()

    return 0





if __name__ == "__main__":
    listlist=list()
    if_not_zero=sys.argv[1]

    deflist=['Rbank','bank','rbank','random','random3','Random','Random2','Random2_detailed','a1_bank','a1_rbank','a2_bank','a2_rbank','Rbank2']

    ### deflist=['bank','rbank','random','random3','Random']
    ### deflist=['Random2','Random2_detailed','a1_bank','a1_rbank']
    ### deflist=['a2_bank','a2_rbank','Rbank','Rbank2']

    ##deflist=['Rbank2']

    wire_mod=['wire_load']

    if if_not_zero==str(0):
        for kkiiddxx in range(len(deflist)):
            get_def_files(deflist[kkiiddxx])



    if if_not_zero==str(1):
        for iddx in range(len(wire_mod)):
            for kkiiddxx in range(len(deflist)):
                print(deflist[kkiiddxx])
                get_file_and_make_directory(wire_mod[iddx],deflist[kkiiddxx])
                if iddx==0:
                    break
            if iddx==0:
                break
                ##copy_scratch(wire_mod[iddx],deflist[kkiiddxx])



    deflist=[['a2_bank','a2_rbank','Random2']]
    ##deflist=[['a1_bank','a1_rbank','bank','rbank','random','Random2_detailed']]
    ##deflist=[['Rbank','random3','Rbank2','Random']]

    ##deflist=[['random','Random','Rbank2']]

    if if_not_zero==str(2):
        for iddx in range(len(wire_mod)):
            for kkiiddxx in range(len(deflist)):
                list_of_set=deflist[kkiiddxx]
                print(deflist[kkiiddxx])
                get_CTS(list_of_set,wire_mod[iddx])
