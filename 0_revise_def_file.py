from hashlib import new
import json
import os
import sys

def get_revised_components(file_Address):
    file = open(file_Address)
    netIdxRange = dict()

### NETS 목록의 index 범위 지정
    for idx, line in enumerate(file):
        if line.startswith("NETS"):
            start_idx = idx+1
        elif line.startswith("END NETS"):
            end_idx = idx
            break
    file.close() 

    will_change_index=list()

    file = open(file_Address)
    for idx, line in enumerate(file):
        line = line.replace("\n", "")
        if idx >= start_idx and idx <= end_idx:
            if line.endswith(";") and line.startswith(";")==False:
                    line=line.replace(';','\n;')
                    will_change_index.append(idx)


    idx=int()

    number_of_change=len(will_change_index)-1

    with open(file_Address,'r') as qq:
        lines=qq.readlines()
        for i,l in enumerate(lines):
            if i==will_change_index[idx]:
                if idx ==number_of_change:
                    continue
                else:
                    idx=idx+1

                new_string=l.split(';')[0]+'\n'+' ;'
                
                with open(file_Address.split('.def')[0]+'(revised).def','a') as ee:
                    ee.write(new_string.lstrip()+'\n')

                    ee.close()

            elif i==0:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'(revised).def','w') as ee:
                        ee.write(l.lstrip())
                        ee.close()
            else:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'(revised).def','a') as ee:
                        ee.write(l.lstrip())

                        ee.close()

        file.close()
    return 0


def get_getget(file_Address):
    file = open(file_Address.split('.def')[0]+'(revised).def')
    netIdxRange = dict()

### NETS 목록의 index 범위 지정
    for idx, line in enumerate(file):
        if line.startswith("NETS"):
            start_idx = idx+1
        elif line.startswith("END NETS"):
            end_idx = idx
            break
    file.close() 

    will_change_index=list()

    file = open(file_Address.split('.def')[0]+'(revised).def')
    for idx, line in enumerate(file):
        line = line.replace("\n", "")
        if idx >= start_idx and idx <= end_idx:
            if line.startswith("-"):
                    line=line.replace(';','\n;')
                    will_change_index.append(idx)
                    ##print(line.split(' (')[0]+'\n'+line.split(line.split(' (')[0])[1])



    idx=int()

    number_of_change=len(will_change_index)-1

    with open(file_Address.split('.def')[0]+'(revised).def','r') as qq:
        lines=qq.readlines()
        for i,l in enumerate(lines):
            if i==will_change_index[idx]:
                if idx ==number_of_change:
                    continue
                else:
                    idx=idx+1

                new_string=l.split(' (')[0]+'\n '+l.split(l.split(' (')[0])[1]
                
                with open(file_Address.split('.def')[0]+'__(revised).def','a') as ee:
                    ee.write(new_string+'\n')

                    ee.close()

            elif i==0:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'__(revised).def','w') as ee:
                        ee.write(l)
                        ee.close()
            else:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'__(revised).def','a') as ee:
                        ee.write(l)

                        ee.close()

        file.close()

    return 0





def get_revised_nets(file_Address):
    file = open(file_Address.split('.def')[0]+'(revised).def')
    netIdxRange = dict()

### NETS 목록의 index 범위 지정
    for idx, line in enumerate(file):
        if line.startswith("COMPONENTS"):
            start_idx = idx+1
        elif line.startswith("END COMPONENTS"):
            end_idx = idx
            break
    file.close() 
    will_change_index=list()

    file = open(file_Address.split('.def')[0]+'__(revised).def')
    for idx, line in enumerate(file):
        line = line.replace("\n", "")
        if idx >= start_idx and idx <= end_idx:
            if line.endswith(";") and line.startswith(";")==False:
                    line=line.replace(';','\n;')
                    will_change_index.append(idx)


    idx=int()

    number_of_change=len(will_change_index)-1

    with open(file_Address.split('.def')[0]+'__(revised).def','r') as qq:
        lines=qq.readlines()
        for i,l in enumerate(lines):
            if i==will_change_index[idx]:

                if idx ==number_of_change:
                    continue
                else:
                    idx=idx+1

                new_string=l.split(';')[0]+'\n'+' ;'
                
                with open(file_Address.split('.def')[0]+'_revised.def','a') as ee:
                    ee.write(new_string+'\n')
                    ee.close()

            elif i==0:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'_revised.def','w') as ee:
                        ee.write(l)
                        ee.close()
            else:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'_revised.def','a') as ee:
                        ee.write(l)
                        ee.close()

        file.close()
        os.remove(file_Address.split('.def')[0]+'__(revised).def')
        os.remove(file_Address.split('.def')[0]+'(revised).def')
    return 0








def get_revised_nets_for_7800_cells(file_Address):
    file = open(file_Address.split('.def')[0]+'_revised.def')
    netIdxRange = dict()

### NETS 목록의 index 범위 지정
    for idx, line in enumerate(file):
        if line.startswith("PINS"):
            start_idx = idx+1
        elif line.startswith("END PINS"):
            end_idx = idx
            break
    file.close() 


    with open(file_Address.split('.def')[0]+'_revised.def','r') as qq:
        lines=qq.readlines()
        for i,l in enumerate(lines):
            if i==end_idx:

                new_string='- temporary_net0 + NET temporary_net0 + DIRECTION INPUT + USE SIGNAL\n \
+ LAYER metal6 ( -140 0 ) ( 140 280 )\n \
+ FIXED ( 28381 53201 ) E ;\n \
- temporary_net1 + NET temporary_net1 + DIRECTION INPUT + USE SIGNAL\n \
+ LAYER metal6 ( -140 0 ) ( 140 280 )\n \
+ FIXED ( 284881 134401 ) E ;\n \
- temporary_net2 + NET temporary_net2 + DIRECTION INPUT + USE SIGNAL\n \
+ LAYER metal6 ( -140 0 ) ( 140 280 )\n \
+ FIXED ( 302741 86801 ) E ;\n \
END PINS\n'
                
                with open(file_Address.split('.def')[0]+'__(revised).def','a') as ee:
                    ee.write(new_string+'\n')

                    ee.close()

            elif i==0:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'__(revised).def','w') as ee:
                        ee.write(l)
                        ee.close()
            else:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'__(revised).def','a') as ee:
                        ee.write(l)

                        ee.close()

        file.close()
        os.remove(file_Address.split('.def')[0]+'_revised.def')
    return 0






def get_revised_nets_for_7800_cells22(file_Address):
    file = open(file_Address.split('.def')[0]+'__(revised).def')
    netIdxRange = dict()

### NETS 목록의 index 범위 지정
    for idx, line in enumerate(file):
        if line.startswith("  ( l1549 D ) ( t0 Z )"):
            start_idx1 = idx
            end_idx1 = idx-1
    file.close() 


    with open(file_Address.split('.def')[0]+'__(revised).def','r') as qq:
        lines=qq.readlines()
        for i,l in enumerate(lines):
            if i==end_idx1:
                new_string='- temporary_net0'

                
                with open(file_Address.split('.def')[0]+'___revised.def','a') as ee:
                    ee.write(new_string+'\n')

                    ee.close()

            elif i==start_idx1:
                new_string=' ( l1549 D ) ( PIN temporary_net0 )'
                
                with open(file_Address.split('.def')[0]+'___revised.def','a') as ee:
                    ee.write(new_string+'\n')

                    ee.close()           
            elif i==0:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'___revised.def','w') as ee:
                        ee.write(l)
                        ee.close()
            else:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'___revised.def','a') as ee:
                        ee.write(l)

                        ee.close()

        file.close()
        os.remove(file_Address.split('.def')[0]+'__(revised).def')
    return 0




def get_revised_nets_for_7800_cells2233(file_Address):
    file = open(file_Address.split('.def')[0]+'___revised.def')
    netIdxRange = dict()

### NETS 목록의 index 범위 지정
    for idx, line in enumerate(file):
        if line.startswith("NETS"):
            start_idx = idx
        elif line.startswith("END PINS"):
            end_idx = idx
            break
    file.close() 


    with open(file_Address.split('.def')[0]+'___revised.def','r') as qq:
        lines=qq.readlines()
        for i,l in enumerate(lines):
            if i==start_idx:

                new_string='NETS 7894 ;\n\
- temporary_net1\n\
 ( PIN temporary_net1 ) ( g4672 A2 ) \n\
 ;\n\
- temporary_net2\n\
 ( PIN temporary_net2 ) ( g2663 A ) \n\
 ;'
                
                with open(file_Address.split('.def')[0]+'_revised.def','a') as ee:
                    ee.write(new_string+'\n')

                    ee.close()

            elif i==0:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'_revised.def','w') as ee:
                        ee.write(l)
                        ee.close()
            else:
                if l.strip()!='':
                    with open(file_Address.split('.def')[0]+'_revised.def','a') as ee:
                        ee.write(l)

                        ee.close()

        file.close()
        os.remove(file_Address.split('.def')[0]+'___revised.def')
    return 0


if __name__ == "__main__":
    arguments=sys.argv

    def_name=arguments[1]




    defdef='../data/deflef_to_graph_and_verilog/0. defs/'+def_name.split('.def')[0]+'/'+def_name

    rrr=get_revised_components(defdef)
    ttt=get_getget(defdef)
    kkk=get_revised_nets(defdef)
    qqq=get_revised_nets_for_7800_cells(defdef)
    aaa=get_revised_nets_for_7800_cells22(defdef)
    www=get_revised_nets_for_7800_cells2233(defdef)
