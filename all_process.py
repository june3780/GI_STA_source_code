import os
import time
import sys

def get_all_process(numbers):
    '''start=time.time()
    os.chdir('../data/deflef_to_graph_and_verilog/verilog/')
    os.system('pwd')
    os.system('sta gcd_temp.tcl')
    print('시간 :',time.time()-start)'''

    ##os.system('python3 get_verilog_file_from_def.py')
    start=time.time()
    ##os.system('python3 get_lib_directory.py '+str(numbers))
    ##os.system('python3 get_hypergraph.py '+str(numbers))
    os.system('python3 get_position_by_v.py '+str(numbers))
    print()
    print('시간 :',time.time()-start)


    return 0




if __name__ == "__main__":
    numbers=sys.argv[1]
    get_all_process(numbers)