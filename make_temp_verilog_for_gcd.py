import json
import pandas as pd




def get_temp(file_add):
    file=open(file_add,'r')
    strings=file.readlines()
    file.close()
    for idx in range(len(strings)):
        temp_ivalue=strings[idx]
        if '$' in temp_ivalue:
            temp_ivalue=temp_ivalue.replace('$','__')
        if '[' in temp_ivalue:
            temp_ivalue=temp_ivalue.replace('[','__')
        if ']' in temp_ivalue:
            temp_ivalue=temp_ivalue.replace(']','__')
        if '\\' in temp_ivalue:
            temp_ivalue=temp_ivalue.replace('\\','__')
        if idx==0:
            with open(file_add,'w') as fw:
                fw.write(temp_ivalue)
            fw.close()
        else:
            with open(file_add,'a') as fw:
                fw.write(temp_ivalue)
            fw.close()

    return 0



def get_sdc(file_sdc,verilog):
    file=open(verilog,'r')
    strings=file.readlines()
    file.close()
    inputs_list=list()
    for ivalue in strings:
        if 'input ' in ivalue and 'clk' not in ivalue:
            inputs_list.append(ivalue.split('input ')[1].split(';')[0].replace('\n',''))
    
    get_delay_of_input=list()
    get_delay_of_input.append('# Synopsys Design Constraints Format')
    get_delay_of_input.append('# Copyright © 2011, Synopsys, Inc. and others. All Rights reserved.')
    get_delay_of_input.append(str())
    get_delay_of_input.append('# clock definition')
    get_delay_of_input.append('create_clock -name mclk -period 10.0 [get_ports clk]')
    get_delay_of_input.append(str())
    get_delay_of_input.append('#input delays')
    for ivalue in inputs_list:
        temp_ivalue=ivalue
        temp_ivalue='set_input_delay 0.0 [get_ports {'+temp_ivalue+'}] -clock mclk'
        get_delay_of_input.append(temp_ivalue)

    df2=pd.DataFrame(index=get_delay_of_input)
    df2.to_csv(file_sdc,sep='\t')

    return 0


if __name__ == "__main__":
    file_address='../data/deflef_to_graph_and_verilog/verilog/scratch_detailed_temp.v'
    sdc_address='../data/deflef_to_graph_and_verilog/verilog/scratch_detailed_temp.sdc'
    get_temp(file_address)
    get_sdc(sdc_address,file_address)