import os
import json
import re
import time


def get_each_cell(file,libAdrress):
    start=time.time()
    cell_dict=dict()
    input_pins=dict()
    output_pins=dict()
    nets=dict()
    ff=open(file)
    lines=ff.readlines()
    for idx in range(len(lines)):

        maybe_cell_name_or_input_or_output_or_wire=lines[idx].replace('\n','').split(' ')[0]

        if maybe_cell_name_or_input_or_output_or_wire not in os.listdir(libAdrress):
            
            if maybe_cell_name_or_input_or_output_or_wire=='output':
                input_pins.update({lines[idx].replace('\n','').split(' ')[1].replace(';',''):{'to':[],'from':[]}})
                
            elif maybe_cell_name_or_input_or_output_or_wire=='input':
                output_pins.update({lines[idx].replace('\n','').split(' ')[1].replace(';',''):{'to':[],'from':[]}})
            elif maybe_cell_name_or_input_or_output_or_wire=='wire':
                nets.update({lines[idx].replace('\n','').split(' ')[1].replace(';',''):{'to':[],'from':[]}})

        else:
            cell_dict.update({maybe_cell_name_or_input_or_output_or_wire+' '+lines[idx].replace('\n','').split(' ')[1]:{}})
            in_lib_info=libAdrress+maybe_cell_name_or_input_or_output_or_wire
            file_list_of_the_macro=os.listdir(in_lib_info)

            

            p=re.findall('[.]\w*[(]\w*[)]',lines[idx])
            for kdx in range(len(p)):
                pin_name=p[kdx].split('.')[1].split('(')[0]
                direction=str()
                cell_dict[maybe_cell_name_or_input_or_output_or_wire+' '+lines[idx].replace('\n','').split(' ')[1]].update({pin_name:{}})

                for jdx in range(len(file_list_of_the_macro)):
                    if pin_name in file_list_of_the_macro[jdx]:
                        if 'input' in file_list_of_the_macro[jdx]:
                            direction='INPUT'
                        else:
                            direction='OUTPUT'

                cell_dict[maybe_cell_name_or_input_or_output_or_wire+' '+lines[idx].replace('\n','').split(' ')[1]][pin_name].update({'direction':direction})

                if direction=='INPUT':
                    cell_dict[maybe_cell_name_or_input_or_output_or_wire+' '+lines[idx].replace('\n','').split(' ')[1]][pin_name].update({'from':p[kdx].split('(')[1].split(')')[0]})
                else:
                    cell_dict[maybe_cell_name_or_input_or_output_or_wire+' '+lines[idx].replace('\n','').split(' ')[1]][pin_name].update({'to':p[kdx].split('(')[1].split(')')[0]})
    ff.close()
    print('time :',time.time()-start)
    ttt=int()
    
    new_cell_dict=dict()

    for ivalue in cell_dict:
        ttt=ttt+1

        output_list=list()
        input_list=list()
        for kvalue in cell_dict[ivalue]:
            if cell_dict[ivalue][kvalue]['direction']=='OUTPUT':
                output_list.append(kvalue)
            else:
                input_list.append(kvalue)
        
        for kvalue in cell_dict[ivalue]:
            new_cell_dict.update({ivalue.split(' ')[1]+' '+kvalue:{'direction':cell_dict[ivalue][kvalue]['direction'],'macroID':ivalue.split(' ')[0],'cell_type':str()}})

            if new_cell_dict[ivalue.split(' ')[1]+' '+kvalue]['direction']=='INPUT':
                if cell_dict[ivalue][kvalue]['from'] in nets:
                    nets[cell_dict[ivalue][kvalue]['from']]['to'].append(ivalue.split(' ')[1]+' '+kvalue)
                else:
                    input_pins[cell_dict[ivalue][kvalue]['from']]['to'].append(ivalue.split(' ')[1]+' '+kvalue)
                new_cell_dict[ivalue.split(' ')[1]+' '+kvalue].update({'to':output_list})

            else:
                if cell_dict[ivalue][kvalue]['from'] in nets:
                    nets[cell_dict[ivalue][kvalue]['to']]['from'].append(ivalue.split(' ')[1]+' '+kvalue)
                else:
                    output_pins[cell_dict[ivalue][kvalue]['to']]['from'].append(ivalue.split(' ')[1]+' '+kvalue)
                new_cell_dict[ivalue.split(' ')[1]+' '+kvalue].update({'from':input_list})

            macro_info=libAdrress+ivalue.split(' ')[0]+'/1_description.txt'
            filefile=open(macro_info,'r')
            strings=filefile.readlines()
            filefile.close()
            new_cell_dict[ivalue.split(' ')[1]+' '+kvalue]['cell_type']=strings[0]



    print(ttt)

    return 0




if __name__ == "__main__":
    verilog_file='../data/superblue16/superblue16.v'
    lib_info='../data/superblue16/superblue16_Late/'
    get_each_cell(verilog_file,lib_info)