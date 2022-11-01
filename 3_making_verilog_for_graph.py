import json
import os


def get_whoareclk(All):
    clklist=list()
    whoareclk=list()
    for idx,ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'net_name' in All[ivalue][kdx]:
                if All[ivalue][kdx]['net_name']=='clk':
                    whoareclk.append(ivalue)

    for idx in range(len(whoareclk)):
        for kdx,kvalue in enumerate(All):
            if kvalue ==whoareclk[idx]:

                for tdx in range(len(All[kvalue])):
                    if 'cell_name' in All[kvalue][tdx]:
                        All[kvalue][tdx]['used_clk']='clk'+str(tdx)
    
    for idx in range(len(whoareclk)):
        for kdx,kvalue in enumerate(All):
            if kvalue ==whoareclk[idx]:

                for tdx in range(len(All[kvalue])):
                    if 'cell_name' in All[kvalue][tdx]:
                        clklist.append(All[kvalue][tdx]['used_clk'])
    return clklist






def get_whoareinput(All):
    inputlist=list()

    whoareclk=list()
    for idx,ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'net_name' in All[ivalue][kdx]:
                if All[ivalue][kdx]['net_name']=='clk':
                    whoareclk.append(ivalue)

    whoareinput=list()
    for idx, ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'net_name' in All[ivalue][kdx] and All[ivalue][kdx]['direction']=='INPUT' and ivalue not in whoareclk:
                whoareinput.append(ivalue)
                inputlist.append(All[ivalue][kdx]['net_name'])

    return inputlist






def get_whoareoutput(All):
    outputlist=list()

    whoareclk=list()
    for idx,ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'net_name' in All[ivalue][kdx]:
                if All[ivalue][kdx]['net_name']=='clk':
                    whoareclk.append(ivalue)

    whoareoutput=list()
    for idx, ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'net_name' in All[ivalue][kdx] and All[ivalue][kdx]['direction']=='OUTPUT' and ivalue not in whoareclk:
                whoareoutput.append(ivalue)
                outputlist.append(All[ivalue][kdx]['net_name'])
    
    return outputlist






def get_whoarewire(All):
    wirelist=list()

    whoareclk=list()
    for idx,ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'net_name' in All[ivalue][kdx]:
                if All[ivalue][kdx]['net_name']=='clk':
                    whoareclk.append(ivalue)

    whoareinput=list()
    for idx, ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'net_name' in All[ivalue][kdx] and All[ivalue][kdx]['direction']=='INPUT' and ivalue not in whoareclk:
                whoareinput.append(ivalue)

    whoareoutput=list()
    for idx, ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'net_name' in All[ivalue][kdx] and All[ivalue][kdx]['direction']=='OUTPUT' and ivalue not in whoareclk:
                whoareoutput.append(ivalue)

    for idx,ivalue in enumerate(All):
        if ivalue not in whoareinput and ivalue not in whoareoutput and ivalue not in whoareclk:
            wirelist.append(ivalue)



    return wirelist






def making_verilog_file(All):
    info=dict()

    whoareclk=list()
    for idx,ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'net_name' in All[ivalue][kdx]:
                if All[ivalue][kdx]['net_name']=='clk':
                    whoareclk.append(ivalue)

    whoareinput=list()
    for idx, ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'net_name' in All[ivalue][kdx] and All[ivalue][kdx]['direction']=='INPUT' and ivalue not in whoareclk:
                whoareinput.append(ivalue)

    whoareoutput=list()
    for idx, ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'net_name' in All[ivalue][kdx] and All[ivalue][kdx]['direction']=='OUTPUT' and ivalue not in whoareclk:
                whoareoutput.append(ivalue)

    whoarewire=list()
    for idx,ivalue in enumerate(All):
        if ivalue not in whoareinput and ivalue not in whoareoutput and ivalue not in whoareclk:
            whoarewire.append(ivalue)

    components_list=list()
    for idx,ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if 'cell_name' in All[ivalue][kdx]:
                components_list.append([All[ivalue][kdx]['macroID'], All[ivalue][kdx]['cell_name'], All[ivalue][kdx]['used_port'], All[ivalue][kdx]['direction'], ivalue])
                info.update({All[ivalue][kdx]['macroID']+' '+All[ivalue][kdx]['cell_name']:list()})

    for idx in range(len(components_list)):
        if components_list[idx][4] in whoarewire:
            for kdx,kvalue in enumerate(info):
                if components_list[idx][0]+' '+components_list[idx][1] == kvalue:
                    info[kvalue].append([components_list[idx][2],components_list[idx][4],components_list[idx][3]])
    

    for idx,ivalue in enumerate(All):
        if ivalue in whoareoutput or ivalue in whoareinput:

            pin_name=str()
            for kdx in range(len(All[ivalue])):
                if 'net_name' in All[ivalue][kdx]:
                    pin_name=All[ivalue][kdx]['net_name']

            for kdx in range(len(All[ivalue])):
                if 'cell_name' in All[ivalue][kdx]:
                    
                    for tdx,tvalue in enumerate(info):
                        if tvalue==(All[ivalue][kdx]['macroID']+' '+All[ivalue][kdx]['cell_name']):
                            info[tvalue].append([All[ivalue][kdx]['used_port'],pin_name,All[ivalue][kdx]['direction']])

    for idx in range(len(whoareclk)):
        for kdx,kvalue in enumerate(All):
            if kvalue ==whoareclk[idx]:

                for tdx in range(len(All[kvalue])):
                    if 'cell_name' in All[kvalue][tdx]:
                        All[kvalue][tdx]['used_clk']='clk'+str(tdx)

    for idx in range(len(whoareclk)):
        for kdx,kvalue in enumerate(All):
            if kvalue ==whoareclk[idx]:

                for tdx in range(len(All[kvalue])):
                    if 'cell_name' in All[kvalue][tdx]:
                        for jdx,jvalue in enumerate(info):
                            if All[kvalue][tdx]['macroID']+' '+All[kvalue][tdx]['cell_name']==jvalue:
                                info[jvalue].append(['CK',All[kvalue][tdx]['used_clk'],All[kvalue][tdx]['direction']])

    return info





def get_verilog_file(All):
    
    for idx, ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            if kdx != 0:
                if All[ivalue][kdx][2]=='INPUT' and All[ivalue][kdx-1][2]=='OUTPUT':
                    temp=All[ivalue][kdx-1]
                    All[ivalue][kdx-1]=All[ivalue][kdx]
                    All[ivalue][kdx]=temp

    for idx, ivalue in enumerate(All):
        for kdx in range(len(All[ivalue])):
            All[ivalue][kdx]='.'+All[ivalue][kdx][0]+'('+All[ivalue][kdx][1]+')'
    
    for idx,ivalue in enumerate(All):

        list_in_one_str=str()
        for kdx in range(len(All[ivalue])):
            list_in_one_str=list_in_one_str+All[ivalue][kdx]+' '
        All[ivalue]='('+list_in_one_str.strip().replace(' ',', ')+');'

    return All



if __name__ == "__main__":
    nbetinfo=dict()
    def_name='ac97_ctrl_revised_by_june(temp).def'


    def_name=def_name.split('.def')[0]
    net_info='../data/deflef_to_graph_and_verilog/3. graphs/'+def_name+'/temporary_net_info_'+def_name+'.json'

    list_of_data_directory=list()
    targetdir=r'/home/june/Documents/PNR/timing/data/deflef_to_graph_and_verilog/5. verilogs_with_tcl'
    files = os.listdir(targetdir)
    for i in files :
            if os.path.isdir(targetdir+r"//"+i):
                list_of_data_directory.append(i)
    if def_name not in list_of_data_directory:
        os.mkdir('../data/deflef_to_graph_and_verilog/5. verilogs_with_tcl/'+def_name)


    verilog_file='../data/deflef_to_graph_and_verilog/5. verilogs_with_tcl/'+def_name+'/not_yet_verilog.v'
    tcl_file='../data/deflef_to_graph_and_verilog/5. verilogs_with_tcl/'+def_name+'/txt_for_tcl_.txt'


    with open(net_info, 'r') as f:

       nbetinfo = json.load(f)

    clklist=get_whoareclk(nbetinfo)
    ##print(clklist)
    inputlist=get_whoareinput(nbetinfo)
    ##print(inputlist)
    outputlist=get_whoareoutput(nbetinfo)
    ###print(outputlist)
    wirelist=get_whoarewire(nbetinfo)
    ##print(wirelist)

    netnet_info=making_verilog_file(nbetinfo)
    RRR=get_verilog_file(netnet_info)

    clks=str()
    for idx in range(len(clklist)):
        clks=clks+clklist[idx]+', '
    clks=clks.rstrip(', ')

    inputs=str()
    for idx in range(len(inputlist)):
        inputs=inputs+inputlist[idx]+', '
    only_inputs=inputs.rstrip(', ')
    inputs=inputs+clks
    
    outputs=str()
    for idx in range(len(outputlist)):
        outputs=outputs+outputlist[idx]+', '
    outputs=outputs.rstrip(', ')

    wires=str()
    for idx in range(len(wirelist)):
        wires=wires+wirelist[idx]+', '
    wires=wires.rstrip(', ')

    for idx, ivalue in enumerate(RRR):
        RRR[ivalue]=ivalue+' '+RRR[ivalue]
    
    DATAlist=list()
    for idx,ivalue in enumerate(RRR):
        DATAlist.append('  '+RRR[ivalue])

    for idx in range(len(DATAlist)):
        if '\\' in DATAlist[idx]:
            DATAlist[idx]=DATAlist[idx].replace('\\','__')
    
    for idx in range(len(DATAlist)):
        if '[' in DATAlist[idx]:
            DATAlist[idx]=DATAlist[idx].replace('[','')
    
    for idx in range(len(DATAlist)):
        if ']' in DATAlist[idx]:
            DATAlist[idx]=DATAlist[idx].replace(']','')


    MODULE_TOP='module top ('+inputs+', '+outputs+');'
    MODULE_TOP=MODULE_TOP.replace('[','').replace(']','')
    INPUT='  input '+inputs+';'
    INPUT=INPUT.replace('[','').replace(']','')
    OUTPUT='  output '+outputs+';'
    OUTPUT=OUTPUT.replace('[','').replace(']','')
    WIRE='  wire '+wires+';'
    WIRE=WIRE.replace('[','').replace(']','')




    fff=open(verilog_file,'w')
    fff.close()

    ddd=open(tcl_file,'w')
    ddd.close

    ddd=open(tcl_file,'a')
    ddd.write(clks.replace(',',''))
    ddd.close

    ddd=open(tcl_file,'a')
    ddd.write('\n')
    ddd.write(only_inputs.replace("[",'').replace("]",'').replace(',',''))
    ddd.close

    fff=open(verilog_file,'a')
    fff.write(MODULE_TOP)
    fff.close()

    fff=open(verilog_file,'a')
    fff.write('\n')
    fff.write(INPUT)
    fff.close()

    fff=open(verilog_file,'a')
    fff.write('\n')
    fff.write(OUTPUT)
    fff.close()

    fff=open(verilog_file,'a')
    fff.write('\n')
    fff.write(WIRE)
    fff.close()

    fff=open(verilog_file,'a')
    fff.write('\n') 
    fff.close()   

    for idx in range(len(DATAlist)):
        fff=open(verilog_file,'a')
        fff.write('\n')
        fff.write(DATAlist[idx])
        fff.close()


    fff=open(verilog_file,'a')
    fff.write('\n')
    fff.write('endmodule // top\n')
    fff.close()



