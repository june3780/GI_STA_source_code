import pandas as pd
import os



def change_conditionlist(file_address):
    print(file_address)
    os_list=os.listdir(file_address)
    if 'dictionary_of_lib.json' in os_list:
        os_list.remove('dictionary_of_lib.json')
    if 'dictionary_of_lib_without_input.json' in os_list:
        os_list.remove('dictionary_of_lib_without_input.json')
    
    for ivalue in os_list:
        temp_address=file_address+ivalue+'/'
        k_os_list=os.listdir(temp_address)
        for kvalue in k_os_list:
            if '3_output_' in kvalue:
                temp_output=temp_address+kvalue+'/'
                t_os_list=os.listdir(temp_output)
                df1=pd.DataFrame()
                if '0_info.tsv' in t_os_list:
                    df1=pd.read_csv(temp_output+'0_info.tsv',sep='\t')
                    temp_index=list(df1['Unnamed: 0'])
                    temp_columns=[kvalue.split('3_output_')[1]]
                    temp_data_list=list(df1[temp_columns[0]])
                    for jdx in range(len(temp_data_list)):
                        if 'condition :' in temp_data_list[jdx]:
                            
                            temp_data_list[jdx]=temp_data_list[jdx].split(' , unateness :')[0]+', unateness :'+temp_data_list[jdx].split(' unateness :')[1]
                    df2=pd.DataFrame(columns=temp_columns,index=temp_index,data=temp_data_list)
                    os.remove(temp_output+'0_info.tsv')
                    df2.to_csv(temp_output+'0_info.tsv',sep='\t')
                    ##print(df2)


    return 0



if __name__ == "__main__":
    os.chdir('Documents/PNR/timing/source/')
    opensta='../data/deflef_to_graph_and_verilog/libs/OPENSTA_example1_'
    opensta=opensta+'typ/'

    change_conditionlist(opensta)