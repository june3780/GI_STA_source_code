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
        if idx >= start_idx and idx < end_idx:
            if line.endswith(";") and line.startswith(";")==False:
                    line=line.replace(';','\n;')
                    will_change_index.append(idx)


    idx=int()

    number_of_change=len(will_change_index)

    with open(file_Address,'r') as qq:
        lines=qq.readlines()
        for i,l in enumerate(lines):
            if idx ==number_of_change:
                with open(file_Address.split('.def')[0]+'(revised).def','a') as ee:
                    ee.write('END NETS\nEND DESIGN\n')
                break
            elif i==will_change_index[idx]:
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

    number_of_change=len(will_change_index)

    with open(file_Address.split('.def')[0]+'(revised).def','r') as qq:
        lines=qq.readlines()
        for i,l in enumerate(lines):
            if idx ==number_of_change:
                with open(file_Address.split('.def')[0]+'__(revised).def','a') as ee:
                    ee.write(' ;\nEND NETS\nEND DESIGN\n')
                break                    
            elif i==will_change_index[idx]:

                idx=idx+1

                new_string=l.split(' (')[0]+'\n '+l.split(l.split(' (')[0])[1]
                
                with open(file_Address.split('.def')[0]+'__(revised).def','a') as ee:
                    ee.write(new_string)
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

    number_of_change=len(will_change_index)

    with open(file_Address.split('.def')[0]+'__(revised).def','r') as qq:
        lines=qq.readlines()
        for i,l in enumerate(lines):
            if idx ==number_of_change:
                    break
            elif i==will_change_index[idx]:
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
    with open(file_Address.split('.def')[0]+'__(revised).def','r') as qq:
        lines=qq.readlines()
        for i,l in enumerate(lines):
            if i>will_change_index[-1]:
                with open(file_Address.split('.def')[0]+'_revised.def','a') as ee:
                    ee.write(l)
                    ee.close()
        os.remove(file_Address.split('.def')[0]+'__(revised).def')
        os.remove(file_Address.split('.def')[0]+'(revised).def')
    return 0









if __name__ == "__main__":
    arguments=sys.argv

    def_name=arguments[1]




    defdef='../data/deflef_to_graph_and_verilog/0. defs/'+def_name.split('.def')[0]+'/'+def_name

    rrr=get_revised_components(defdef)
    ttt=get_getget(defdef)
    kkk=get_revised_nets(defdef)

