from ast import arguments
import os
import shutil
import sys





def get_file_and_make_directory(wiremode,file_type):
    '''for idx in range(200):
        if idx==3:
            
            os.mkdir('../data/deflef_to_graph_and_verilog/0. defs/rbank'+str(idx)+'_detailed')
            shutil.copyfile('../data/7809cells_groups/Rbank2/rbank'+str(idx)+'_detailed.def','../data/deflef_to_graph_and_verilog/0. defs/rbank'+str(idx)+'_detailed/rbank'+str(idx)+'_detailed.def')'''


    idx=int()
    for idx in range(200):
        defdef=str()
        if file_type=='a1_bank':
            defdef='a1_'+str(idx)+'bank.txt.def'
        elif file_type=='a1_rbank':
            defdef='a1_'+str(idx)+'rbank.txt.def'        
        elif file_type=='a2_rbank':
            defdef='a2_'+str(idx)+'rbank.txt.def'        
        elif file_type=='a2_bank':
            defdef='a2_'+str(idx)+'bank.txt.def'        
        elif file_type=='rbank':
            defdef=str(idx)+'rbank_detailed.def'        
        elif file_type=='bank':
            defdef=str(idx)+'bank_detailed.def'        
        elif file_type=='random':
            defdef='random'+str(idx)+'_detailed.def'
        elif file_type=='Rbank':
            defdef='rbank'+str(idx)+'.def'
        elif file_type=='random3':
            defdef='3_random_'+str(idx)+'.def'
        elif file_type=='Rbank2':
            defdef='rbank'+str(idx)+'_detailed.def'



        if file_type=='bank' and (idx==25 or idx==83):
            continue
        if (file_type=='Rbank' or file_type=='Rbank2') and (idx==0 or idx==1 or idx==2):
            continue

        if wiremode=='star':
            os.system('python3 0_revise_def_file.py '+defdef)
            os.system('python3 1_test.py '+defdef)
            os.system('python3 2_for_modifying_graph.py '+defdef+' '+wiremode+' '+file_type) 
        else:
            os.system('python3 2_for_modifying_graph.py '+defdef+' '+wiremode+' '+file_type)


        if (file_type=='a1_bank' or file_type=='a1_rbank') and idx==49:
            break
        if (file_type=='bank' or file_type=='rbank' or file_type=='random' or file_type=='random3') and idx==99:
            break
        if (file_type=='a2_bank' or file_type=='a2_rbank') and idx==199:
            break

        if (file_type=='Rbank' or file_type=='Rbank2') and idx==102:
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


    return 0


if __name__ == "__main__":
    listlist=list()

    deflist=['Rbank2','Rbank','random3','a1_rbank','a2_bank','a2_rbank','bank','rbank','random']
    wire_mod=['star','hpwl','clique','wire_load']

    for iddx in range(len(wire_mod)):
        for kkiiddxx in range(len(deflist)):
            get_file_and_make_directory(wire_mod[iddx],deflist[kkiiddxx])
            copy_scratch(wire_mod[iddx],deflist[kkiiddxx])