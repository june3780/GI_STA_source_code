import json
import sys
import os
import shutil





def get_temp_buffer_def(defname, wire, file_type):
    file_address='../data/deflef_to_graph_and_verilog/with_CTS_buffer_RGM/'+file_type
    if file_type not in os.listdir('../data/deflef_to_graph_and_verilog/with_CTS_buffer_RGM/'):
        os.mkdir(file_address)
    
    defdirectroy=defname.split('.def')[0]
    origin='../data/deflef_to_graph_and_verilog/0. defs/'+defdirectroy+'/'+defname
    if defdirectroy+'_TB.def' in os.listdir(file_address):
        os.remove(file_address+'/'+defdirectroy+'_TB.def')
    shutil.copyfile(origin,file_address+'/'+defdirectroy+'_TB.def')

    will_be_change=file_address+'/'+defdirectroy+'_TB.def'

    if defname.split('.def')[0]+'.json' in os.listdir('../data/deflef_to_graph_and_verilog/results/'+file_type+'/test_7800_zfor_clk_'+wire+'_with_skew_RGM/'):
        address_of_cts='../data/deflef_to_graph_and_verilog/results/'+file_type+'/test_7800_zfor_clk_'+wire+'_with_skew_RGM/'+defname.split('.def')[0]+'.json'
        with open(address_of_cts,'r') as ff:
            cts_info=json.load(ff)

        cts=cts_info[0]
        skew=cts_info[1]

        revised_directory=defdirectroy+'_revised'
        file_path='../data/deflef_to_graph_and_verilog/3. graphs/'+revised_directory+'(temp)/temporary_net_info_'+revised_directory+'(temp).json'
        with open(file_path, 'r')as file:
            netinfo_for_clk=json.load(file)
        file.close()
        def_unit=netinfo_for_clk['def_unit_should_divide_distance']



        idx=int()

        nets=list()
        components=list()
        for ivalue in cts:
            if cts[ivalue]['direction']=='OUTPUT' and cts[ivalue]['type']=='cell' and 'temp_buffer_' in ivalue:
                netlist=list()
                for kdx in range(len(cts[ivalue]['to'])):
                    netlist.append(cts[ivalue]['to'][kdx])
                onenet='    - CTS_'+str(idx)+' ( '+ivalue+' ) '

                for kdx in range(len(netlist)):
                    onenet=onenet+'( '+netlist[kdx]+' ) '
                onenet=onenet+'+ USE SIGNAL ;'
                nets.append(onenet)
                idx=idx+1

                cell_pos=get_cell_position(cts[ivalue]['macroID'],cts[ivalue]['position'],def_unit)
                one_position='    - '+ivalue.split(' ')[0]+' '+cts[ivalue]['macroID']+' FIXED ( '+str(cell_pos[0])+' '+str(cell_pos[1])+' ) FS ;'
                components.append(one_position)
        nets.append('END NETS')
        components.append('END COMPONENTS')

        ############# nets, components


        file = open(will_be_change)
        for idx, line in enumerate(file):
            if line.startswith("END NETS"):
                for kdx in range(len(nets)):
                    f=open(will_be_change.split('.def')[0]+'temp.def','a')
                    f.write(nets[kdx]+'\n')
                    f.close()

            else:
                if idx==0:
                    f=open(will_be_change.split('.def')[0]+'temp.def','w')
                    f.write(line)
                    f.close()
                else:
                    f=open(will_be_change.split('.def')[0]+'temp.def','a')
                    f.write(line)
                    f.close()
        file.close() 
        os.remove(will_be_change)
        
        whereisclk=int()
        file = open(will_be_change.split('.def')[0]+'temp.def')
        for idx, line in enumerate(file):
            if line.startswith("END COMPONENTS"):
                for kdx in range(len(components)):
                    f=open(will_be_change.split('.def')[0]+'__temp__temp.def','a')
                    f.write(components[kdx]+'\n')
                    f.close()

            else:
                if idx==0:
                    f=open(will_be_change.split('.def')[0]+'__temp__temp.def','w')##############
                    f.write(line)
                    f.close()
                else:
                    f=open(will_be_change.split('.def')[0]+'__temp__temp.def','a')#############
                    f.write(line)
                    f.close()
        file.close() 
        os.remove(will_be_change.split('.def')[0]+'temp.def')

        file = open(will_be_change.split('.def')[0]+'__temp__temp.def')###############
        for idx, line in enumerate(file):
            if line.startswith("    - clk") or line.startswith("- clk"):
                whereisclk=idx
        file.close() 



        list_after_clk_net=list()
        file = open(will_be_change.split('.def')[0]+'__temp__temp.def')###############
        for idx, line in enumerate(file):
            if (line.startswith("    -") or line.startswith("-"))and idx>whereisclk:
                list_after_clk_net.append(idx)
        file.close()
        
        max_idx=int()
        min_idx=int()
        
        for idx in range(len(list_after_clk_net)):
            if max_idx<list_after_clk_net[idx]:
                max_idx=list_after_clk_net[idx]
        min_idx=max_idx

        for idx in range(len(list_after_clk_net)):
            if min_idx>list_after_clk_net[idx]:
                min_idx=list_after_clk_net[idx]


        file = open(will_be_change.split('.def')[0]+'__temp__temp.def')
        for idx, line in enumerate(file):

            if idx<whereisclk or idx>=min_idx:
                if idx==0:
                    f=open(will_be_change.split('.def')[0]+'_RGM.def','w')
                    f.write(line)
                    f.close()

                else:
                    f=open(will_be_change.split('.def')[0]+'_RGM.def','a')
                    f.write(line)
                    f.close()
        file.close()
        os.remove(will_be_change.split('.def')[0]+'__temp__temp.def')
    
    else:
        os.remove(file_address+'/'+defdirectroy+'_TB.def')
        f=open('temp_RGM.txt','a')
        f.write(defname+' '+wire+' '+file_type+' '+'failed'+'\n')
        f.close()
        print('CTS_failed')
    return 0





def get_cell_position(macroIDD,pin_position,def_unit):
    cell_position=list()
    if macroIDD=='CLKBUF_X1':
        cell_position=[pin_position[0]*def_unit-0.475,pin_position[1]*def_unit-0.695]


    return cell_position




if __name__ == "__main__":
    defdef=sys.argv[1]
    wire_mode=sys.argv[2]
    file_type=sys.argv[3]
    
    get_temp_buffer_def(defdef,wire_mode, file_type)