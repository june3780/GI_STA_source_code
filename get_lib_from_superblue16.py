import readline
import pandas as pd
import json
import os
import csv
import copy
import sys


def get_dataframe_10(listlist):
    df1=pd.DataFrame()
    load_capa=listlist[0].replace('index_1 (\"','').replace('\") ;','').split(',')
    input_transition=listlist[1].replace('index_2 (\"','').replace('\") ;','').split(',')

    for jdx in range(len(load_capa)):
        load_capa[jdx]=float(load_capa[jdx])

    for jdx in range(len(input_transition)):
        input_transition[jdx]=float(input_transition[jdx])
    
    Data1=listlist[3].replace('\"','').replace(',\\','').split(', ')


    data_need_transform=list()
    for jdx in range(6):
        Data1=listlist[3+jdx].replace('\"','').replace(',\\','').split(', ')
        for jjdx in range(len(Data1)):
            Data1[jjdx]=float(Data1[jjdx])
        data_need_transform.append(Data1)

    last_data=listlist[9].replace('\"','').replace('\\','').split(', ')
    for jdx in range(len(last_data)):
        last_data[jdx]=float(last_data[jdx])
    data_need_transform.append(last_data)

    temp_data=list()
    for jdx in range(len(input_transition)):
        temp_data_0=list()
        for jjdx in range(len(load_capa)):
            temp_data_0.append(data_need_transform[jjdx][jdx])
        temp_data.append(temp_data_0)


    df1=pd.DataFrame(temp_data,columns=load_capa,index=input_transition)
    ##print(df1)
    ##df1.to_csv('temp_df1.tsv',sep='\t')
    
    return df1



def getMACROname(fileAddress,saving_dir):
    

    cell_descriptidx=list()
    block_list=list()
    file = open(fileAddress, 'r')
    for idx,iline in enumerate(file):
        iline=iline.strip().replace('\n','')
        if '/* Begin cell: ' in iline:
            cell_descriptidx.append(idx)
        elif '/* End cell:' in iline:
            cell_descriptidx.append(idx)
        elif 'cell ("block' in iline:
            block_list.append(idx-1)
            block_list.append(idx)
    file.close()


    del block_list[0]
    cell_descriptidx.extend(block_list)
    cell_descriptidx.append(idx)
    
    counts=int(len(cell_descriptidx)/2)

    macro_info=dict()
    for idx in range(counts):
        startindex=cell_descriptidx[idx*2]
        endindex=cell_descriptidx[idx*2+1]

        one_macro_info=dict()
        one_macro_info_list=list()

        file = open(fileAddress, 'r')
        for idx,iline in enumerate(file):
            if idx>startindex-1 and idx<endindex+1:
                iline=iline.strip().replace('\n','')
                one_macro_info_list.append(iline)
        file.close()
        where_the_name=int()
        temp1=str()
        for idx in range(len(one_macro_info_list)):
            if '/* Begin cell: ' in one_macro_info_list[idx] or 'cell ("block' in one_macro_info_list[idx]:
                temp1=one_macro_info_list[idx]
                one_macro_info.update({one_macro_info_list[idx]:[]})
                where_the_name=idx

        del one_macro_info_list[where_the_name]
        
        for idx in range(len(one_macro_info_list)):
            one_macro_info[temp1].append(one_macro_info_list[idx])

        macro_info.update(one_macro_info)

    temp2=copy.deepcopy(macro_info)
    for ivalue in temp2:
        if 'Begin cell' in ivalue:
            temp3=ivalue.split('Begin cell: ')[1].split(' */')[0]
            macro_info.update({ivalue.split('Begin cell: ')[1].split(' */')[0]:macro_info[ivalue]})
            del macro_info[ivalue]

            if temp3!='TIEH_X1':

                pins_list=list()
                outputindex=int()
                for idx in range(len(macro_info[temp3])):
                    if 'pin (' in macro_info[temp3][idx]:
                        pins_list.append(idx)

                    if 'direction : output ;' in macro_info[temp3][idx]:
                        outputindex=idx

                pindict=dict()
                temp4=list()
                for idx in range(len(pins_list)-1):
                    if pins_list[idx]<outputindex and pins_list[idx+1]>outputindex:
                        pindict.update({macro_info[temp3][pins_list[idx]].split('(\"')[1].split('\")')[0]:{'direction':'OUTPUT','info':macro_info[temp3][pins_list[idx]:pins_list[idx+1]]}})
                    else:
                        pindict.update({macro_info[temp3][pins_list[idx]].split('(\"')[1].split('\")')[0]:{'direction':'INPUT','info':macro_info[temp3][pins_list[idx]:pins_list[idx+1]]}})

                pindict.update({macro_info[temp3][pins_list[idx+1]].split('(\"')[1].split('\")')[0]:{'direction':'INPUT','info':macro_info[temp3][pins_list[idx+1]:]}})

                for kvalue in pindict:
                    if pindict[kvalue]['direction']=='INPUT':
                        for idx in range(len(pindict[kvalue]['info'])):
                            if 'capacitance' in pindict[kvalue]['info'][idx]:
                                pindict[kvalue].update({'capacitance':pindict[kvalue]['info'][idx].split(': ')[1].split(' ;')[0]})
                        del pindict[kvalue]['info']
                    
                    else:
                        for idx in range(len(pindict[kvalue]['info'])):
                            if 'timing() {' in pindict[kvalue]['info'][idx]:
                                temp4.append(idx)
                            elif 'max_capacitance' in pindict[kvalue]['info'][idx]:
                                    pindict[kvalue].update({'max_capacitance':pindict[kvalue]['info'][idx].split(': ')[1].split(' ;')[0]})
                
                temp5=list()
                for idx in range(len(temp4)-1):
                    temp6=list()
                    for kvalue in pindict:
                        if pindict[kvalue]['direction']=='OUTPUT':
                            for jdx in range(len(pindict[kvalue]['info'])):
                                if jdx>=temp4[idx] and jdx<=temp4[idx+1]:
                                    temp6.append(pindict[kvalue]['info'][jdx])
                            temp5.append(temp6)

                temp6=list()
                for kvalue in pindict:
                    if pindict[kvalue]['direction']=='OUTPUT':
                        for jdx in range(len(pindict[kvalue]['info'])):
                            if len(temp4)==1:
                                if jdx >=temp4[0]:
                                    temp6.append(pindict[kvalue]['info'][jdx])
                                    continue
                            else:
                                if jdx>=temp4[idx+1]:
                                    temp6.append(pindict[kvalue]['info'][jdx])
                temp5.append(temp6)


                ##print(json.dumps(temp5,indent=4))
                all_pins=list()
                output_dataframes=dict()
                for idx in range(len(temp5)):
                    for jdx in range(len(temp5[idx])):
                        if 'related_pin' in temp5[idx][jdx]:
                            output_dataframes.update({'related_pin : '+temp5[idx][jdx].split(': \"')[1].split('\" ;')[0]:temp5[idx]})
                            all_pins.append(temp5[idx][jdx].split(': \"')[1].split('\" ;')[0])
                ##print(json.dumps(output_dataframes,indent=4))
                temp7=dict()
                for kkdx,kvalue in enumerate(output_dataframes):
                    temp7.update({kvalue:{}})
                    temp7[kvalue].update({'delay_fall':get_dataframe_10(output_dataframes[kvalue][2:12])})
                    temp7[kvalue].update({'transition_fall':get_dataframe_10(output_dataframes[kvalue][15:25])})
                    temp7[kvalue].update({'delay_rise':get_dataframe_10(output_dataframes[kvalue][28:38])})
                    temp7[kvalue].update({'transition_rise':get_dataframe_10(output_dataframes[kvalue][41:51])})
                    temp7[kvalue].update({'unateness':output_dataframes[kvalue][53].split(': ')[1].split(' ;')[0]})

                if kkdx ==0:
                    for kkdx,kvalue in enumerate(output_dataframes):
                        temp7[kvalue].update({'condition_list':'condition : No condition, '+kvalue+', unateness : '+temp7[kvalue]['unateness']})
                else:
                    for kkdx,kvalue in enumerate(output_dataframes):
                        all_pins.remove(kvalue.split(': ')[1])
                        temp8=copy.deepcopy(all_pins)
                        temp9=temp8[0]
                        for jtdx in range(len(temp8)-1):
                            temp9=temp9+' & '+temp8[jtdx+1]
                        temp7[kvalue].update({'condition_list':'condition : '+temp9+', '+kvalue+', unateness : '+temp7[kvalue]['unateness']})
                        all_pins.append(kvalue.split(': ')[1])

                conditionlist=list()
                for kvalue in temp7:
                    conditionlist.append(temp7[kvalue]['condition_list'])

                whois_output=str()
                max_capa=float()
                for kvalue in pindict:
                    if pindict[kvalue]['direction']=='OUTPUT':
                        whois_output=kvalue
                        max_capa=pindict[kvalue]['max_capacitance']
                        del pindict[kvalue]['info']

                info_data=list()
                info_data.append(float(max_capa))

                function_str=str()
                if 'NAND' in temp3:
                    function_str='!'
                    counts_input=int(temp3.split('NAND')[1].split('_')[0])
                    for jjdx in range(counts_input-1):
                        function_str=function_str+'('
                    function_str=function_str+all_pins[0]

                    for jjdx in range(len(all_pins)-1):
                        function_str=function_str+' & '+all_pins[jjdx+1]+')'

                elif 'NOR' in temp3:
                    function_str='!'
                    counts_input=int(temp3.split('NOR')[1].split('_')[0])
                    for jjdx in range(counts_input-1):
                        function_str=function_str+'('
                    function_str=function_str+all_pins[0]

                    for jjdx in range(len(all_pins)-1):
                        function_str=function_str+' | '+all_pins[jjdx+1]+')'

                elif 'INV' in temp3:
                    function_str='!'
                    function_str=function_str+all_pins[0]
                
                elif 'DFF' in temp3:
                    function_str='iq'

                index_info=['max_capacitance','function']
                info_data.append(function_str)
                for jdx in range(len(conditionlist)):
                    info_data.append(conditionlist[jdx])
                    index_info.append('condition_list')




                if temp3 not in os.listdir(saving_dir):
                    os.mkdir(saving_dir+temp3)

                df_info=pd.DataFrame(info_data,columns=[whois_output],index=index_info) ############### 저장

                if '3_output_'+whois_output not in os.listdir(saving_dir+temp3+'/'):
                    os.mkdir(saving_dir+temp3+'/'+'3_output_'+whois_output)
                df_info.to_csv(saving_dir+temp3+'/'+'3_output_'+whois_output+'/0_info.tsv',sep='\t')

                conditionrist=list(df_info[whois_output])[2:]
                for jdx in range(len(conditionrist)):
                    for kvalue in temp7:
                        if temp7[kvalue]['condition_list']==conditionrist[jdx]:
                            temp7[kvalue]['delay_fall'].to_csv(saving_dir+temp3+'/'+'3_output_'+whois_output+'/'+'condition_'+str(jdx)+'_cell_fall.tsv',sep='\t')
                            temp7[kvalue]['delay_rise'].to_csv(saving_dir+temp3+'/'+'3_output_'+whois_output+'/'+'condition_'+str(jdx)+'_cell_rise.tsv',sep='\t')
                            temp7[kvalue]['transition_fall'].to_csv(saving_dir+temp3+'/'+'3_output_'+whois_output+'/'+'condition_'+str(jdx)+'_fall_transition.tsv',sep='\t')
                            temp7[kvalue]['transition_rise'].to_csv(saving_dir+temp3+'/'+'3_output_'+whois_output+'/'+'condition_'+str(jdx)+'_rise_transition.tsv',sep='\t')

                for kvalue in pindict:
                    if pindict[kvalue]['direction']=='INPUT':
                        df_input=pd.DataFrame([pindict[kvalue]['capacitance'],pindict[kvalue]['capacitance']],columns=[kvalue],index=['fall_capacitance','rise_capacitance'])
                        df_input.to_csv(saving_dir+temp3+'/'+'2_input_'+kvalue+'.tsv',sep='\t')
                
                ff=open(saving_dir+temp3+'/1_description.txt','w')
                if temp3 !='DFF_X80' and temp3 !='TIEH_X1':
                    ff.write('Combinational cell')
                elif temp3 =='DFF_X80':
                    ff.write('Pos.edge D-Flip-Flop')
                ff.close()



            else:
                outputindex=int()
                pins_list=list()
                for idx in range(len(macro_info[temp3])):
                    if 'pin (' in macro_info[temp3][idx]:
                        pins_list.append(idx)

                    if 'direction : output ;' in macro_info[temp3][idx]:
                        outputindex=idx

                pindict=dict()
                temp4=list()

                pindict.update({macro_info[temp3][pins_list[0]].split('(\"')[1].split('\")')[0]:{'direction':'OUTPUT','info':macro_info[temp3][pins_list[0]:]}})

                for kvalue in pindict:
                    if pindict[kvalue]['direction']=='OUTPUT':
                        for idx in range(len(pindict[kvalue]['info'])):
                            if 'max_capacitance' in pindict[kvalue]['info'][idx]:
                                    pindict[kvalue].update({'max_capacitance':pindict[kvalue]['info'][idx].split(': ')[1].split(' ;')[0]})

                whois_output='o'
                df_info=pd.DataFrame([[pindict['o']['max_capacitance']]],columns=['o'],index=['max_capacitance'])
                if temp3 not in os.listdir(saving_dir):
                    os.mkdir(saving_dir+temp3)

                if '3_output_'+whois_output not in os.listdir(saving_dir+temp3+'/'):
                    os.mkdir(saving_dir+temp3+'/'+'3_output_'+whois_output)
                df_info.to_csv(saving_dir+temp3+'/'+'3_output_'+whois_output+'/0_info.tsv',sep='\t')


                ff=open(saving_dir+temp3+'/1_description.txt','w')
                if temp3 =='TIEH_X1':
                    ff.write('Constant cell')
                ff.close()
        else:

            macro_info_cell=dict()
            temp3=ivalue.split('(\"')[1].split('\")')[0]
            macro_info_cell.update({temp3:{}})

            outpins_index=list()
            outputpins_name=list()
            for jdx in range(len(macro_info[ivalue])):
                if 'pin (' in macro_info[ivalue][jdx]:

                    outpins_index.append(jdx)
                    pin_name=macro_info[ivalue][jdx].split('(\"')[1].split('\")')[0]
                    macro_info_cell[temp3].update({pin_name:{}})
                    macro_info_cell[temp3][pin_name].update({'direction':macro_info[ivalue][jdx+1].split(': ')[1].split(' ;')[0]})
                    if macro_info_cell[temp3][pin_name]['direction']=='input':
                        outpins_index.remove(jdx)
                        outputpins_name.append(pin_name)
                        macro_info_cell[temp3][pin_name].update({'capacitance':float(macro_info[ivalue][jdx+2].split(': ')[1].split(' ;')[0])})

            ##print(macro_info_cell)
            for jdx in range(len(outpins_index)):
                pin_in_name=str()
                if jdx !=len(outpins_index)-1:
                    for jidx in range(len(macro_info[ivalue])):

                        if jidx==outpins_index[jdx]:
                            pin_in_name=macro_info[ivalue][jidx].split('(\"')[1].split('\")')[0]
                            macro_info_cell[temp3][pin_in_name].update({'info':[]})

                        if jidx>outpins_index[jdx] and jidx<outpins_index[jdx+1]:
                            macro_info_cell[temp3][pin_in_name]['info'].append(macro_info[ivalue][jidx])

                else:
                    for jidx in range(len(macro_info[ivalue])):

                        if jidx==len(macro_info[ivalue])-1:
                                break

                        if jidx==outpins_index[jdx]:
                            pin_in_name=macro_info[ivalue][jidx].split('(\"')[1].split('\")')[0]
                            macro_info_cell[temp3][pin_in_name].update({'info':[]})

                        elif jidx>outpins_index[jdx]:
                            macro_info_cell[temp3][pin_in_name]['info'].append(macro_info[ivalue][jidx])
            
            for jvalue in macro_info_cell[temp3]:
                if macro_info_cell[temp3][jvalue]['direction']=='output':
                    for kjdx in range(len(macro_info_cell[temp3][jvalue]['info'])):
                        if 'max_capacitance' in macro_info_cell[temp3][jvalue]['info'][kjdx]:
                            macro_info_cell[temp3][jvalue].update({'max_capacitance':float(macro_info_cell[temp3][jvalue]['info'][kjdx].split(': ')[1].split(' ;')[0])})
                        elif 'timing_sense' in macro_info_cell[temp3][jvalue]['info'][kjdx]:
                            macro_info_cell[temp3][jvalue].update({'unateness':macro_info_cell[temp3][jvalue]['info'][kjdx].split(': ')[1].split(' ;')[0]})
                        elif 'related_pin' in macro_info_cell[temp3][jvalue]['info'][kjdx]:
                            macro_info_cell[temp3][jvalue].update({'related_pin':macro_info_cell[temp3][jvalue]['info'][kjdx].split(': \"')[1].split('\" ;')[0]})
                        elif 'cell_rise' in macro_info_cell[temp3][jvalue]['info'][kjdx]:
                            macro_info_cell[temp3][jvalue].update({'cell_rise':float(macro_info_cell[temp3][jvalue]['info'][kjdx+1].split('(\"')[1].split('\")')[0])})
                        elif 'rise_transition' in macro_info_cell[temp3][jvalue]['info'][kjdx]:
                            macro_info_cell[temp3][jvalue].update({'rise_transition':float(macro_info_cell[temp3][jvalue]['info'][kjdx+1].split('(\"')[1].split('\")')[0])})
                        elif 'cell_fall' in macro_info_cell[temp3][jvalue]['info'][kjdx]:                           
                            macro_info_cell[temp3][jvalue].update({'cell_fall':float(macro_info_cell[temp3][jvalue]['info'][kjdx+1].split('(\"')[1].split('\")')[0])})
                        elif 'fall_transition' in macro_info_cell[temp3][jvalue]['info'][kjdx]:                    
                            macro_info_cell[temp3][jvalue].update({'fall_transition':float(macro_info_cell[temp3][jvalue]['info'][kjdx+1].split('(\"')[1].split('\")')[0])}) 
                    del macro_info_cell[temp3][jvalue]['info']

            if temp3 not in os.listdir(saving_dir):
                os.mkdir(saving_dir+temp3)

            for jvalue in macro_info_cell[temp3]:
                if macro_info_cell[temp3][jvalue]['direction']=='output':
                    if '3_output_'+jvalue not in os.listdir(saving_dir+temp3+'/'):
                        os.mkdir(saving_dir+temp3+'/3_output_'+jvalue)
                    datadata=[[macro_info_cell[temp3][jvalue]['max_capacitance']],[str()]]
                    if 'related_pin' in macro_info_cell[temp3][jvalue] and 'unateness' in macro_info_cell[temp3][jvalue]:
                        datadata.append(['condition : No condition, related_pin : '+macro_info_cell[temp3][jvalue]['related_pin']+', unateness : '+macro_info_cell[temp3][jvalue]['unateness']])
                        
                        fff=open(saving_dir+temp3+'/3_output_'+jvalue+'/condition_0_cell_fall.txt','w')
                        fff.write(str(macro_info_cell[temp3][jvalue]['cell_fall']))
                        fff.close()
                        fff=open(saving_dir+temp3+'/3_output_'+jvalue+'/condition_0_cell_rise.txt','w')
                        fff.write(str(macro_info_cell[temp3][jvalue]['cell_rise']))
                        fff.close()
                        fff=open(saving_dir+temp3+'/3_output_'+jvalue+'/condition_0_fall_transition.txt','w')
                        fff.write(str(macro_info_cell[temp3][jvalue]['fall_transition']))
                        fff.close()
                        fff=open(saving_dir+temp3+'/3_output_'+jvalue+'/condition_0_rise_transition.txt','w')
                        fff.write(str(macro_info_cell[temp3][jvalue]['rise_transition']))
                        fff.close()            

                    else:
                        datadata.append(['condition : No condition, related_pin : all, unateness : complex'])
                    df_output=pd.DataFrame(data=datadata,columns=[jvalue],index=['max_capacitance','function','condition_list'])
                    df_output.to_csv(saving_dir+temp3+'/3_output_'+jvalue+'/0_info.tsv',sep='\t')

            fff=open(saving_dir+temp3+'/1_description.txt','w')
            fff.write('MACRO')
            fff.close()

            for jvalue in macro_info_cell[temp3]:
                if macro_info_cell[temp3][jvalue]['direction']=='input':
                    datainput=[[macro_info_cell[temp3][jvalue]['capacitance']],[macro_info_cell[temp3][jvalue]['capacitance']]]
                    df_input=pd.DataFrame(data=datainput,columns=[jvalue],index=['fall_capacitance','rise_capacitance'])
                    df_input.to_csv(saving_dir+temp3+'/'+'2_input_'+jvalue+'.tsv',sep='\t')
    return 0











def transform_no_condition(to_file):
    macrolist_who_has_no_condition=os.listdir(to_file)

    for idx in range(len(macrolist_who_has_no_condition)):
        if '1. description.txt' in (os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/')):
                
            f=open(to_file+macrolist_who_has_no_condition[idx]+'/1. description.txt','r')

            line=f.readline()
            if line=='Combinational cell':


                for kdx in range(len(os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/'))):
                    if '3. output:' in os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/')[kdx]:
                        df1=pd.read_csv(to_file+macrolist_who_has_no_condition[idx]+'/'+os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/')[kdx]+'/0. info.tsv',sep='\t')
                        df2=copy.deepcopy(df1)
                        if len(list(df1.iloc[2:,1]))==1:
                            continue
              
                        for tdx in range(len(list(df1.iloc[2:,1]))):
                            if 'condition : No condition, related_pin :' in (list(df1.iloc[2:,1])[tdx]):

                                if 'HA' in macrolist_who_has_no_condition[idx]:                 

                                    if 'related_pin : A' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','B')
                                    elif 'related_pin : B' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A')
                                
                                elif 'OAI21' in macrolist_who_has_no_condition[idx] and 'OAI211' not in macrolist_who_has_no_condition[idx]:

                                    if 'related_pin : B1' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A & !B2')
                                    elif 'related_pin : B2' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A & !B1')
                           
                                elif 'OAI211' in macrolist_who_has_no_condition[idx]:

                                    if 'related_pin : C1' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A & B & !C2')
                                    elif 'related_pin : C2' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A & B & !C1')

                                elif 'AOI21' in macrolist_who_has_no_condition[idx] and 'AOI211' not in macrolist_who_has_no_condition[idx]:
                                    if 'related_pin : B1' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A & B2')
                                    elif 'related_pin : B2' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A & B1')      
                                                          
                                elif 'AOI211' in macrolist_who_has_no_condition[idx]:
                                    if 'related_pin : C1' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A & !B & C2')
                                    elif 'related_pin : C2' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A & !B & C1')

                                elif 'OR4' in macrolist_who_has_no_condition[idx]:
                                    if 'related_pin : A1' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A2 & !A3 & !A4')
                                    elif 'related_pin : A2' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A1 & !A3 & !A4')
                                    elif 'related_pin : A3' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A1 & !A2 & !A4')
                                    elif 'related_pin : A4' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A1 & !A2 & !A3')  

                                elif 'OR3' in macrolist_who_has_no_condition[idx]:
                                    if 'related_pin : A1' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A2 & !A3')
                                    elif 'related_pin : A2' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A1 & !A3')
                                    elif 'related_pin : A3' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A1 & !A2')

                                elif 'OR2' in macrolist_who_has_no_condition[idx]:
                                    if 'related_pin : A1' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A2')
                                    elif 'related_pin : A2' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','!A1')

                                elif 'AND4' in macrolist_who_has_no_condition[idx]:
                                    if 'related_pin : A1' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A2 & A3 & A4')
                                    elif 'related_pin : A2' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A1 & A3 & A4')
                                    elif 'related_pin : A3' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A1 & A2 & A4')
                                    elif 'related_pin : A4' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A1 & A2 & A3')

                                elif 'AND3' in macrolist_who_has_no_condition[idx]:
                                    if 'related_pin : A1' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A2 & A3')
                                    elif 'related_pin : A2' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A1 & A3')
                                    elif 'related_pin : A3' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A1 & A2')

                                elif 'AND2' in macrolist_who_has_no_condition[idx]:
                                    if 'related_pin : A1' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A2')
                                    elif 'related_pin : A2' in list(df1.iloc[2:,1])[tdx]:
                                        df2.iloc[2+tdx,1]=df2.iloc[2+tdx,1].replace('No condition','A1')

                                datadata=list()
                                for jdx in range(len(list(df2.iloc[0:,1]))):
                                    datadata.append([list(df2.iloc[0:,1])[jdx]])
                                df3=pd.DataFrame(data=datadata, index=list(df2['Unnamed: 0']),columns=[list(df2.columns)[1]])
                                df3.to_csv(to_file+macrolist_who_has_no_condition[idx]+'/'+os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/')[kdx]+'/0. info.tsv',sep='\t')


            f.close()




    macrolist_who_has_no_condition=os.listdir(to_file)
    kk=int()
    for idx in range(len(macrolist_who_has_no_condition)):
    
        if '1. description.txt' in (os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/')):
                
            f=open(to_file+macrolist_who_has_no_condition[idx]+'/1. description.txt','r')

            line=f.readline()
            if line=='Combinational cell':

                real_inputlist=list()
                for kdx in range(len(os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/'))):

                    if '2. input: ' in os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/')[kdx]:
                        real_inputlist.append(os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/')[kdx].replace("2. input: ",'').replace(".tsv",''))

                for kdx in range(len(os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/'))):
                    if '3. output:' in os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/')[kdx]:
                        df1=pd.read_csv(to_file+macrolist_who_has_no_condition[idx]+'/'+os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/')[kdx]+'/0. info.tsv',sep='\t')
                        df2=copy.deepcopy(df1)
                        if len(list(df1.iloc[2:,1]))==1:
                            continue

                        else:

                            input_in_conditions=list()
                            for tdx in range(len(list(df1.iloc[2:,1]))):
                                strstr=list(df1.iloc[2:,1])[tdx].split("condition : ")[1].split(", related_pin")[0]
                                if '!' in strstr:
                                    strstr=strstr.replace('!','')
                                if '&' in strstr:
                                    input_in_conditions=strstr.split(" & ")
                                else:
                                    input_in_conditions=[strstr]
                                for edx in range(len(real_inputlist)):
                                    if real_inputlist[edx] not in input_in_conditions:
                                        df2.iloc[tdx+2,1]=df2.iloc[tdx+2,1].split(", related_pin : ")[0]+', related_pin : '+real_inputlist[edx]+' , unateness : '+df2.iloc[tdx+2,1].split(", unateness : ")[1]
                        ##print(df2)
                        datadata=list()
                        for jdx in range(len(list(df2.iloc[0:,1]))):
                            datadata.append([list(df2.iloc[0:,1])[jdx]])
                        df3=pd.DataFrame(data=datadata, index=list(df2['Unnamed: 0']),columns=[list(df2.columns)[1]])
                        df3.to_csv(to_file+macrolist_who_has_no_condition[idx]+'/'+os.listdir(to_file+macrolist_who_has_no_condition[idx]+'/')[kdx]+'/0. info.tsv',sep='\t')


            f.close()
    ##for idx in range(len(macro_from_truth_table)):
    ##    print(macro_from_truth_table[idx])


    return 0







if __name__ == "__main__":
    type=sys.argv[2] #### Early, Late
    ##type='Late'
    numvver=sys.argv[1]
    to_file='../data/superblue'+numvver+'/superblue'+numvver+'_'+type+'/'
    fromfileAddress='../data/superblue'+numvver+'/superblue'+numvver+'_'+type+'.lib'
    lib_address='../data/deflef_to_graph_and_verilog/libs/'

    rrr=getMACROname(fromfileAddress,to_file)
    
    ##ttt=transform_no_condition(to_file)