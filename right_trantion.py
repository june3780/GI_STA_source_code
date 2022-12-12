import shutil
import os






def get_right_transition(file_add):
    listlist=os.listdir(file_add)
    if 'dictionary_of_lib.json' in listlist:
        listlist.remove('dictionary_of_lib.json')
    if 'dictionary_of_lib_without_input.json' in listlist:
        listlist.remove('dictionary_of_lib_without_input.json')
    for ivalue in listlist:
        temp_x=file_add+ivalue+'/'
        temp_list=os.listdir(temp_x)
        for kvalue in temp_list:
            if '3_output' in kvalue:
                temptemp_list=os.listdir(temp_x+kvalue+'/')
                for tvalue in temptemp_list:
                    if 'transtion' in tvalue:
                        origin=temp_x+kvalue+'/'+tvalue
                        master=origin.replace('transtion','transition')
                        shutil.copy(origin,master)
                        #print(temp_x+kvalue+'/'+tvalue)
                    #print(tvalue)
                ##print(temptemp_list)


    return 0


if __name__ == "__main__":
    example_sta='../data/deflef_to_graph_and_verilog/libs/OPENSTA_example1_'
    example_sta=example_sta+'typ/'
    get_right_transition(example_sta)