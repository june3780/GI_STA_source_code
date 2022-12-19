import pandas as pd
import os



def change_nor_condition(add):
    nor_group=list()
    for ivalue in os.listdir(add):
        if 'NOR' in ivalue:
            nor_group.append(ivalue)

    for ivalue in nor_group:
        df1=pd.read_csv(add+ivalue+'/3_output_o/0_info.tsv',sep='\t')
        #print(list(df1['o']))
        new_columns=['max_capacitance','function']
        for kdx in range(len(list(df1['o']))-2):
            new_columns.append('condition_list')
        new_index=['o']
        new_data=list()
        new_data.append(list(df1['o'])[0:2])
        newnew_conditions=list(df1['o'])[2:]
        #print(new_data)
        #print(newnew_conditions)
        for kdx in range(len(newnew_conditions)):
            other_pins_list=list()
            other_pins=newnew_conditions[kdx].split('condition :')[1].split(', related_pin :')[0].strip()
            if '&' in other_pins:
                other_pins_list=other_pins.split(' & ')
            else:
                other_pins_list.append(other_pins)
            #print(other_pins_list)
            new_other_pins=str()
            if '!' in other_pins_list[0]:
                continue
            new_other_pins='!'+other_pins_list[0]
            
            for tdx in range(len(other_pins_list)-1):
                temp_new=' & !'+other_pins_list[tdx+1]
                new_other_pins=new_other_pins+temp_new
            ##print(new_other_pins)
            #print(newnew_conditions[kdx])
            newnew_conditions[kdx]='condition : '+new_other_pins+', related_pin :'+newnew_conditions[kdx].split(', related_pin :')[1]
            #print(newnew_conditions[kdx])
        new_data[0].extend(newnew_conditions)

        #print(new_data)
        new_df1=pd.DataFrame(columns=new_index,index=new_columns,data=new_data[0])
        new_df1.to_csv(add+ivalue+'/3_output_o/0_info.tsv',sep='\t')
    return 0

if __name__ == "__main__":
    checking='superblue16_Early'
    fileadd='../data/deflef_to_graph_and_verilog/libs/'
    fileadd=fileadd+checking+'/'
    change_nor_condition(fileadd)