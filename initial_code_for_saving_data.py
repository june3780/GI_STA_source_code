import os
import sys
import shutil




def do_printing(wirewire,checking):
    lalala='../data/deflef_to_graph_and_verilog/results/'+checking+'/test_7800_'+wirewire
    gagaga='../data/deflef_to_graph_and_verilog/results/a1_bank/test_7800_'+wirewire+'/scratch_detailed.json'
    if 'scratch_detailed.json' not in os.listdir(lalala):
        shutil.copyfile(gagaga,lalala+'/scratch_detailed.json')



    checkinglist=checking
    os.system('python3 printing_path.py '+wirewire+' '+str(1)+' '+checkinglist+' 5 Pass')
    os.system('python3 printing_path.py '+wirewire+' '+str(1)+' '+checkinglist+' 0')

    return 0

if __name__ == "__main__":
    wirewire=sys.argv[1]
    checking1=sys.argv[2]
    do_printing(wirewire,checking1)