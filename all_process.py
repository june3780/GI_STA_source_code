import os
import time
import sys

def get_all_process():
    '''start=time.time()
    os.chdir('../data/deflef_to_graph_and_verilog/verilog/')
    os.system('pwd')
    os.system('sta gcd_temp.tcl')
    print('시간 :',time.time()-start)'''

    ##os.system('python3 get_verilog_file_from_def.py')
    start=time.time()
    checking=sys.argv[1]
    '''if sys.argv[2]==str(0):
        os.system('python3 get_lib_directory.py '+'superblue'+checking+'_Late.lib ')
        os.system('python3 get_hypergraph.py '+'superblue'+checking+'.v superblue'+checking+'_Late.lib 3')'''
    print(checking)
    if sys.argv[2]==str(0) or sys.argv[2]==str(1):    
        os.system('python3 get_position_by_v.py superblue'+checking+'.lef superblue'+checking+'.def superblue'+checking+'.v superblue'+checking+'_Late.lib '+sys.argv[2])
    elif sys.argv[2]==str(2):
        os.system('python3 comparing_temp.py '+checking)
    print()
    print('시간 :',time.time()-start)


    return 0




if __name__ == "__main__":
    get_all_process()