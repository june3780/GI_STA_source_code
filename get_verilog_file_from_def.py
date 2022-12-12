import json
import os
import re















def get_components_macroID(def_file):
    start_idx_components=int()
    end_idx_components=int()
    start_idx_pins=int()
    end_idx_pins=int()
    start_idx_nets=int()
    end_idx_nets=int()

    ff=open(def_file)
    lines=ff.readlines()
    for idx in range(len(lines)):
        checking=lines[idx].strip()
        if 'COMPONENTS' in checking and 'END' not in checking:
            start_idx_components=idx
        elif 'END COMPONENTS' in checking:
            end_idx_components=idx
        elif 'PINS' in checking and 'END' not in checking:
            start_idx_pins=idx
        elif 'END PINS' in checking:
            end_idx_pins=idx
        elif 'NETS' in checking and 'END' not in checking and 'SPECIAL' not in checking:
            start_idx_nets=idx
        elif 'END NETS' in checking and 'SPECIAL' not in checking:
            end_idx_nets=idx

    ff.close()

    components_list=list()
    pins_list=list()
    nets_list=list()

    ff=open(def_file)
    lines=ff.readlines()
    for idx in range(len(lines)):
        checking=lines[idx].strip()
        if idx>start_idx_components and idx<end_idx_components:
            components_list.append(checking)

        elif idx>start_idx_pins and idx<end_idx_pins:
            pins_list.append(checking)
            
        elif idx>start_idx_nets and idx<end_idx_nets:
            nets_list.append(checking)
    ff.close()

    re_components_list=list()
    for ivalue in components_list:
        if ivalue.startswith('-'):
            re_components_list.append(ivalue)
        else:
            re_components_list[-1]=re_components_list[-1]+' '+ivalue

    re_pins_list=list()
    for ivalue in pins_list:
        if ivalue.startswith('-'):
            re_pins_list.append(ivalue)
        else:
            re_pins_list[-1]=re_pins_list[-1]+' '+ivalue

    re_nets_list=list()
    for ivalue in nets_list:
        if ivalue.startswith('-'):
            re_nets_list.append(ivalue)
        else:
            re_nets_list[-1]=re_nets_list[-1]+' '+ivalue
    

    components_dict=dict()
    for ivalue in re_components_list:
        components_dict.update({ivalue.split('- ')[1].split(' ')[0]:{'macroID':ivalue.split('- ')[1].split(' ')[1]}})

    pins_dict=dict()
    for ivalue in re_pins_list:
        temp_line=ivalue.split(' ')
        temp_direciton_idx=int()
        for kdx in range(len(temp_line)):
            if temp_line[kdx]=='DIRECTION':
                temp_direciton_idx=kdx+1
        if temp_line[temp_direciton_idx]=='OUTPUT' or temp_line[temp_direciton_idx]=='INPUT':
            pins_dict.update({temp_line[1]:{'direction':temp_line[temp_direciton_idx]}})

    nets_dict=dict()
    for ivalue in re_nets_list:
        nets_dict.update({ivalue.split(' ')[1]:{}})
        checking_str=ivalue.split('- '+ivalue.split(' ')[1])[1]
        if '+' in checking_str:
            checking_str=checking_str.split('+')[0].strip()
        if ';' in checking_str:
            checking_str=checking_str.split(';')[0].strip()
        p=re.findall('\([^)]*\)',checking_str)

        for kvalue in p:
            temp_name=kvalue
            if 'PIN' in temp_name:
                continue
            temp_name=temp_name.split('(')[1].split(')')[0].strip()
            cell_name=temp_name.split(' ')[0]
            pin_name=temp_name.split(' ')[1]
            if cell_name not in nets_dict[ivalue.split(' ')[1]]:
                nets_dict[ivalue.split(' ')[1]].update({cell_name:[pin_name]})
            else:
                nets_dict[ivalue.split(' ')[1]][cell_name].append(pin_name)
    return [components_dict,pins_dict,nets_dict]




def get_verilog(file_add,info,module_name):
    f=open(file_add,'w')
    f.write('module '+module_name+' (\n')
    f.close()
    components=info[0]
    pins=info[1]
    nets=info[2]
    outpins=list()
    inpins=list()
    for idx,ivalue in enumerate(pins):
        if pins[ivalue]['direction']=='INPUT':
           inpins.append(ivalue)
        else:
            outpins.append(ivalue)
        f=open(file_add,'a')
        f.write(ivalue)
        if idx<len(pins)-1:
            f.write(',\n')
            f.close()
        else:
            f.write(');\n')
            f.close()
    f=open(file_add,'a')
    f.write('\n// Start PIs\n')
    f.close()

    for ivalue in inpins:
        f=open(file_add,'a')
        f.write('input '+ivalue+';\n')
        f.close()
    f=open(file_add,'a')
    f.write('\n// Start POs\n')
    f.close()

    for ivalue in outpins:
        f=open(file_add,'a')
        f.write('output '+ivalue+';\n')
        f.close()
    f=open(file_add,'a')
    f.write('\n// Start wires\n')
    f.close()

    for ivalue in nets:
        for kvalue in nets[ivalue]:
            for jvalue in nets[ivalue][kvalue]:
                components[kvalue].update({jvalue:ivalue})

            

        if ivalue not in outpins and ivalue not in inpins:
            f=open(file_add,'a')
            f.write('wire '+ivalue+';\n')
            f.close()
    f=open(file_add,'a')
    f.write('\n\n// Start cells\n')
    f.close()

    for ivalue in components:
        temp_line=components[ivalue]['macroID']+' '+ivalue
        del components[ivalue]['macroID']
        if len(components[ivalue])==0:
            continue
        temp_line=temp_line+' ( '
        ##print(temp_line)
        for kdx,kvalue in enumerate(components[ivalue]):
            temp_line=temp_line+'.'+kvalue+'('+components[ivalue][kvalue]+')'
            if kdx !=len(components[ivalue])-1:
                temp_line=temp_line+', '
            else:
                temp_line=temp_line+' );'
        f=open(file_add,'a')
        f.write(temp_line+'\n')
        f.close()
    f=open(file_add,'a')
    f.write('\nendmodule\n')
    f.close()
        #print(components[ivalue]['macroID']+' '+ivalue)
    ##for ivalue in nets:
    ##    print(ivalue,nets[ivalue])
    return 0












if __name__ == "__main__":
    ##os.chdir('Documents/PNR/timing/source/')
    sample='gcd'
    sample='scratch_detailed'
    file_address_def='../data/deflef_to_graph_and_verilog/defs/'
    file_address_def=file_address_def+sample+'.def'
    file_address_verilog='../data/deflef_to_graph_and_verilog/verilog/'
    file_address_verilog=file_address_verilog+sample+'.v'
    ##file_address_def=file_address_def+'gcd.def'



    dict_of_component=dict()
    dict_of_component=get_components_macroID(file_address_def)
    saving_verilog=get_verilog(file_address_verilog,dict_of_component,sample)