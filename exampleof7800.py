from ast import arguments
import os
import shutil
import sys





def get_file_and_make_directory(listlist,wiremode,file_type):
    '''for idx in range(50):
            os.mkdir('../data/deflef_to_graph_and_verilog/0. defs/a1_'+str(idx)+'bank.txt')
            shutil.copyfile('../data/a1_bank_def/'+str(idx)+'bank.txt.def','../data/deflef_to_graph_and_verilog/0. defs/a1_'+str(idx)+'bank.txt/a1_'+str(idx)+'bank.txt.def')'''
    defdef='scratch_detailed.def'
    os.system('python3 2_for_modifying_graph.py '+defdef+' '+wiremode+' '+file_type)

    '''idx=int()
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

        if file_type=='bank' and (idx==25 or idx==83):
            continue
        

        os.system('python3 2_for_modifying_graph.py '+defdef+' '+wiremode)


        if (file_type=='a1_bank' or file_type=='a1_rbank') and idx==49:
            break
        if (file_type=='bank' or file_type=='rbank' or file_type=='random') and idx==99:
            break
        if (file_type=='a2_bank' or file_type=='a2_rbank') and idx==199:
            break'''

    return 0





if __name__ == "__main__":
    listlist=list()

    deflist=['a1_bank', 'a1_rbank', 'bank', 'rbank', 'random', 'a2_bank', 'a2_rbank']
    wire_mod=['star','hpwl','clique','wire_load']

    for iddx in range(4):
        for kkiiddxx in range(7):
            get_file_and_make_directory(listlist,wire_mod[iddx],deflist[kkiiddxx])