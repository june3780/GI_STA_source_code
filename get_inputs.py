import json





def get_input_list():
    file_adrress='../data/superblue16/superblue16.v'
    input_lists=str()
    f=open(file_adrress,'r')
    line_num=1
    line=f.readline()
    while line:
        if line.startswith('input ') and 'iccad_clk' not in line:
            
            input_lists=input_lists+' '+line.split(';')[0].split('input ')[1]
            print(line.split(';')[0].split('input ')[1])
        line=f.readline()
        line_num+=1
    f.close()
    
    print(input_lists)
    return 0


if __name__ == "__main__":
    get_input_list()