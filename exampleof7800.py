from ast import arguments
import os
import shutil
import sys





def get_file_and_make_directory(listlist,wiremode,file_type):
    '''for idx in range(104):
        if idx<=102:
            continue
        os.mkdir('../data/deflef_to_graph_and_verilog/0. defs/rbank'+str(idx))
        shutil.copyfile('/tmp/Rbank/rbank'+str(idx)+'.def','../data/deflef_to_graph_and_verilog/0. defs/rbank'+str(idx)+'/rbank'+str(idx)+'.def')'''


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

        if file_type=='bank' and (idx==25 or idx==83):
            continue
        if file_type=='Rbank' and (idx==0 or idx==1 or idx==2):
            continue

        if wiremode=='star':
            os.system('python3 0_revise_def_file.py '+defdef)
            os.system('python3 1_test.py '+defdef)
            os.system('python3 2_for_modifying_graph.py '+defdef+' '+wiremode+' '+file_type) 
        else:
            os.system('python3 2_for_modifying_graph.py '+defdef+' '+wiremode+' '+file_type)


        if (file_type=='a1_bank' or file_type=='a1_rbank') and idx==49:
            break
        if (file_type=='bank' or file_type=='rbank' or file_type=='random') and idx==99:
            break
        if (file_type=='a2_bank' or file_type=='a2_rbank') and idx==199:
            break

        if (file_type=='Rbank') and idx==102:
            break
    '''defdef='scratch_detailed.def'
    os.system('python3 2_for_modifying_graph.py '+defdef+' '+wiremode+' '+file_type)'''
    
    return 0





if __name__ == "__main__":
    listlist=list()

    deflist=['Rbank']
    wire_mod=['star','hpwl','clique','wire_load']

    for iddx in range(len(wire_mod)):
        for kkiiddxx in range(len(deflist)):
            get_file_and_make_directory(listlist,wire_mod[iddx],deflist[kkiiddxx])