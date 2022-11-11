import readline
from tkinter.ttk import setup_master
from tracemalloc import start
import pandas as pd
import json
import os
import csv
import copy


def getMACROname(fileAddress,type,to_file):
    filelist=os.listdir(to_file)


    layerID_list = list()
    rrr=str()
    macrolist=os.listdir('../data/OPENSTA/OPENSTA_example_'+type+'/')
    cell_descriptidx=list()
    startidx=list()
    endidx=list()
    superend=int()
    file = open(fileAddress, 'r')
    for idx,iline in enumerate(file):
        iline=iline.strip().replace('\n','')
        if 'Module          	: ' in iline:
            cell_descriptidx.append(idx+1)
            startidx.append(idx+4)
        if '* End of file' in iline:
            superend=idx-4
    file.close()

    for idx in range(len(startidx)):
        if idx != (len(startidx)-1):
            endidx.append(startidx[idx+1]-8)
        else:
            endidx.append(superend)

    cell_descriptindex=int()
    startindex=int()
    endindex=int()

    for idx in range(len(startidx)):
        savingfile=str()
        valuesinmacro=dict()
        


        cell_descriptindex=cell_descriptidx[idx]
        startindex=startidx[idx]
        endindex=endidx[idx]
        startt_pin=list()
        description=str()
        file=open(fileAddress, 'r')
        for kdx, kline in enumerate(file):
            kline=kline.replace("\n",'').strip()
            if kdx>=startindex and kdx<=endindex:
                if kline == '':
                    continue
                if 'cell (' in kline:
                    valuesinmacro['cell_name']=kline.replace("cell (",'').replace(") {",'').strip()
                if 'drive_strength' in kline:
                    valuesinmacro['drive_strength']=int(kline.replace('drive_strength','').replace(":",'').replace(";",'').strip())
                if 'pin (' in kline:
                    startt_pin.append(kdx)
            if kdx==cell_descriptindex:
                description=kline.split(':')[1].strip()

        file.close()

        if 'Combinational cell' in description:
            description='Combinational cell'
        elif 'Pos.edge D-Flip-Flop' in description:
            description='Pos.edge D-Flip-Flop'
        elif 'Physical cell' in description:
            description='Physical cell'
        elif 'Combinational tri-state cell' in description:
            description='Combinational tri-state cell'
        elif 'High enable Latch' in description:
            description='High enable Latch'
        elif 'Low enable Latch' in description:
            description='Low enable Latch'
        else:
            description='Pos.edge clock gating cell'

        if description!='Combinational cell':
            continue

        valuesinmacro['description']=description
        valuesinmacro['input']=list()
        valuesinmacro['output']=list()
        startt_pin.append(endindex-1)



        for kdx in range(len(startt_pin)-1):
            inoroutlist=list()
            file=open(fileAddress, 'r')
            for tdx, tline in enumerate(file):
                tline=tline.replace("\n",'').strip()
                if tdx>=startt_pin[kdx] and tdx<startt_pin[kdx+1]:
                    if 'internal_power () {' in tline:
                        break
                    else:
                        inoroutlist.append(tline)
            if (len(inoroutlist)) ==10 or 'timing_type\t   : hold_rising;' in inoroutlist:
                valuesinmacro['input'].append(inoroutlist)
            elif 'timing_type\t   : min_pulse_width;' not in inoroutlist:
                valuesinmacro['output'].append(inoroutlist)
            file.close()

        '''hold_timing=list()
        setup_timing=list()
        for kdx in range(len(valuesinmacro['input'])):
            pins1=dict()
            pins1[str(valuesinmacro['input'][kdx][0].split('(')[1].split(')')[0].strip())]=None
            pins2=dict()
            pins2[str(valuesinmacro['input'][kdx][0].split('(')[1].split(')')[0].strip())]=None


            for tdx in range(len(valuesinmacro['input'][kdx])):
                if 'timing_type\t   : hold_rising;' == valuesinmacro['input'][kdx][tdx]:
                    pins1[str(valuesinmacro['input'][kdx][0].split('(')[1].split(')')[0].strip())]=valuesinmacro['input'][kdx][tdx:tdx+15]
                elif 'timing_type\t   : setup_rising;' == valuesinmacro['input'][kdx][tdx]:
                    pins2[str(valuesinmacro['input'][kdx][0].split('(')[1].split(')')[0].strip())]=valuesinmacro['input'][kdx][tdx:tdx+15]
            hold_timing.append(pins1)
            setup_timing.append(pins2)'''

        for kdx,kvalue in enumerate(valuesinmacro):
            if kvalue=='input':
                
                for tdx in range(len(valuesinmacro[kvalue])):
                    input_name=valuesinmacro[kvalue][tdx][0].split('(')[1].split(')')[0].strip()
                    fall_capa=float(valuesinmacro[kvalue][tdx][6].split(': ')[1].replace(';','').strip())
                    rise_capa=float(valuesinmacro[kvalue][tdx][7].split(': ')[1].replace(';','').strip())
                    valuesinmacro[kvalue][tdx]={'pin_name':input_name,'fall_capacitance':fall_capa,'rise_capacitance':rise_capa}
            
            if kvalue=='output':

                for tdx in range(len(valuesinmacro[kvalue])):
                    output_name=valuesinmacro[kvalue][tdx][0].split('(')[1].split(')')[0].strip()
                    max_capa=float(valuesinmacro[kvalue][tdx][5].split(": ")[1].split(';')[0].strip())
                    function_output=valuesinmacro[kvalue][tdx][6].split(": ")[1].split(';')[0].replace('"','').strip()
                
                    whereistable=list()
                    when_table=dict()

                    for jdx in range(len(valuesinmacro[kvalue][tdx])):
                        if 'timing ()'in valuesinmacro[kvalue][tdx][jdx]:
                            whereistable.append(jdx)
                    whereistable.append(jdx+1)

                    condition_table=list()
                    for jdx in range(len(whereistable)-1):
                        kk=int()
                        for qdx in range(whereistable[jdx],whereistable[jdx+1]):
                            if 'when' in valuesinmacro[kvalue][tdx][qdx]:
                                kk=kk+1
                                condition_table.append(valuesinmacro[kvalue][tdx][qdx].split(": ")[1].replace('";','').replace('"','').strip())
                        if kk ==0:
                            condition_table.append('No condition')
                        

                    if len(condition_table)==0:
                        for qdx in range(len(whereistable)):
                            condition_table.append('No condition')

                    for jdx in range(len(whereistable)-1):
                        for qdx in range(whereistable[jdx],whereistable[jdx+1]):
                            if 'related_pin	   :' in valuesinmacro[kvalue][tdx][qdx]:
                                related_pin=valuesinmacro[kvalue][tdx][qdx].split('"')[1].split('"')[0].strip()
                            if 'timing_sense	   : ' in valuesinmacro[kvalue][tdx][qdx]:
                                unateness=valuesinmacro[kvalue][tdx][qdx].split(": ")[1].split(';')[0]
                            if 'cell_fall' in valuesinmacro[kvalue][tdx][qdx]:
                                when_table.update({'condition : '+condition_table[jdx]+', related_pin : '+related_pin+' , unateness : '+unateness+', cell_fall':valuesinmacro[kvalue][tdx][qdx:qdx+11]})
                            elif 'cell_rise' in valuesinmacro[kvalue][tdx][qdx]:
                                when_table.update({'condition : '+condition_table[jdx]+', related_pin : '+related_pin+' , unateness : '+unateness+', cell_rise':valuesinmacro[kvalue][tdx][qdx:qdx+11]})
                            elif 'fall_transition' in valuesinmacro[kvalue][tdx][qdx]:
                                when_table.update({'condition : '+condition_table[jdx]+', related_pin : '+related_pin+' , unateness : '+unateness+', fall_transition':valuesinmacro[kvalue][tdx][qdx:qdx+11]})
                            elif 'rise_transition' in valuesinmacro[kvalue][tdx][qdx]:
                                when_table.update({'condition : '+condition_table[jdx]+', related_pin : '+related_pin+' , unateness : '+unateness+', rise_transition':valuesinmacro[kvalue][tdx][qdx:qdx+11]})

                    valuesinmacro[kvalue][tdx]={'pin_name':output_name,'max_capacitance':max_capa,'function':function_output, 'delay,transition by condition' : when_table}

        for kdx in range(len(valuesinmacro['output'])):
            total_input_transitionlist=list()
            load_capacitancelist=list()
            total_datalist=list()
            for tdx,tvalue in enumerate(valuesinmacro['output'][kdx]['delay,transition by condition']):
                input_transition_info={'input_transition':valuesinmacro['output'][kdx]['delay,transition by condition'][tvalue][1].split('("')[1].split('")')[0].split(',')}
                load_capacitance_info={'load_capacitance':valuesinmacro['output'][kdx]['delay,transition by condition'][tvalue][2].split('("')[1].split('")')[0].split(',')}
                total_input_transitionlist.append(input_transition_info)
                load_capacitancelist.append(load_capacitance_info)

                datalist=list()
                for jdx in range(7):
                    datalist.append(valuesinmacro['output'][kdx]['delay,transition by condition'][tvalue][jdx+3].split('"')[1].split('"')[0].split(','))
                total_datalist.append(datalist)

            for tdx in range(len(total_datalist)):
                for jdx in range(len(total_datalist[tdx])):
                    for udx in range(len(total_datalist[tdx][jdx])):
                        total_datalist[tdx][jdx][udx]=float(total_datalist[tdx][jdx][udx])
            
            for tdx in range (len(total_input_transitionlist)):
                for jdx in range(len(total_input_transitionlist[tdx]['input_transition'])):
                    total_input_transitionlist[tdx]['input_transition'][jdx]=float(total_input_transitionlist[tdx]['input_transition'][jdx])

            for tdx in range (len(load_capacitancelist)):
                for jdx in range(len(load_capacitancelist[tdx]['load_capacitance'])):
                    load_capacitancelist[tdx]['load_capacitance'][jdx]=float(load_capacitancelist[tdx]['load_capacitance'][jdx])

            for tdx,tvalue in enumerate(valuesinmacro['output'][kdx]['delay,transition by condition']):
                valuesinmacro['output'][kdx]['delay,transition by condition'][tvalue]=list([0 for i in range(3)])
            for tdx,tvalue in enumerate(valuesinmacro['output'][kdx]['delay,transition by condition']):
                valuesinmacro['output'][kdx]['delay,transition by condition'][tvalue][0]=total_input_transitionlist[tdx]
                valuesinmacro['output'][kdx]['delay,transition by condition'][tvalue][1]=load_capacitancelist[tdx]
                valuesinmacro['output'][kdx]['delay,transition by condition'][tvalue][2]=total_datalist[tdx]



        '''
        ##print(json.dumps(hold_timing,indent=4))
        ##print(json.dumps(setup_timing,indent=4))

        total_hold_table=dict()
        total_setup_table=dict()
        for kdx in range(len(hold_timing)):
            clock_ready=dict()
            data_ready=dict()
            value_ready=list()
            for tdx,tvalue in enumerate(hold_timing[kdx]):
                total_hold_table[tvalue]=dict()
                for jdx in range(len(hold_timing[kdx][tvalue])):
                    if 'index_2' in hold_timing[kdx][tvalue][jdx]:
                        clock_ready={'data_transition':hold_timing[kdx][tvalue][jdx].split('("')[1].split('")')[0].split(',')}
                    if 'index_1' in hold_timing[kdx][tvalue][jdx]:
                        data_ready={'clock_transition':hold_timing[kdx][tvalue][jdx].split('("')[1].split('")')[0].split(',')}
                    if 'values' in hold_timing[kdx][tvalue][jdx]:
                        value_ready.append(hold_timing[kdx][tvalue][jdx:jdx+3])
            total_hold_table[tvalue].update(data_ready)
            total_hold_table[tvalue].update(clock_ready)

            for tdx in range(len(value_ready)):
                for jdx in range(len(value_ready[tdx])):
                    value_ready[tdx][jdx]=value_ready[tdx][jdx].split('"')[1].split('"')[0].split(',')
            
            for tdx in range(len(value_ready)):
                for jdx in range(len(value_ready[tdx])):
                    for qdx in range(len(value_ready[tdx][jdx])):
                        value_ready[tdx][jdx][qdx]=float(value_ready[tdx][jdx][qdx])
            total_hold_table[tvalue].update({'fall_constraint':value_ready[0]})
            total_hold_table[tvalue].update({'rise_constraint':value_ready[1]})

        for kdx in range(len(setup_timing)):
            clock_ready=dict()
            data_ready=dict()
            value_ready=list()
            for tdx,tvalue in enumerate(setup_timing[kdx]):
                total_setup_table[tvalue]=dict()
                for jdx in range(len(setup_timing[kdx][tvalue])):
                    if 'index_2' in setup_timing[kdx][tvalue][jdx]:
                        clock_ready={'data_transition':setup_timing[kdx][tvalue][jdx].split('("')[1].split('")')[0].split(',')}
                    if 'index_1' in setup_timing[kdx][tvalue][jdx]:
                        data_ready={'clock_transition':setup_timing[kdx][tvalue][jdx].split('("')[1].split('")')[0].split(',')}
                    if 'values' in setup_timing[kdx][tvalue][jdx]:
                        value_ready.append(setup_timing[kdx][tvalue][jdx:jdx+3])
            total_setup_table[tvalue].update(data_ready)
            total_setup_table[tvalue].update(clock_ready)

            for tdx in range(len(value_ready)):
                for jdx in range(len(value_ready[tdx])):
                    value_ready[tdx][jdx]=value_ready[tdx][jdx].split('"')[1].split('"')[0].split(',')
            
            for tdx in range(len(value_ready)):
                for jdx in range(len(value_ready[tdx])):
                    for qdx in range(len(value_ready[tdx][jdx])):
                        value_ready[tdx][jdx][qdx]=float(value_ready[tdx][jdx][qdx])
            total_setup_table[tvalue].update({'fall_constraint':value_ready[0]})
            total_setup_table[tvalue].update({'rise_constraint':value_ready[1]})
        
        for kdx,kvalue in enumerate(total_hold_table):
            for tdx in range(len(total_hold_table[kvalue]['clock_transition'])):
                total_hold_table[kvalue]['clock_transition'][tdx]=float(total_hold_table[kvalue]['clock_transition'][tdx])
            for tdx in range(len(total_hold_table[kvalue]['data_transition'])):
                total_hold_table[kvalue]['data_transition'][tdx]=float(total_hold_table[kvalue]['data_transition'][tdx])           

        for kdx,kvalue in enumerate(total_setup_table):
            for tdx in range(len(total_setup_table[kvalue]['clock_transition'])):
                total_setup_table[kvalue]['clock_transition'][tdx]=float(total_setup_table[kvalue]['clock_transition'][tdx])
            for tdx in range(len(total_setup_table[kvalue]['data_transition'])):
                total_setup_table[kvalue]['data_transition'][tdx]=float(total_setup_table[kvalue]['data_transition'][tdx])'''        
        


        for kdx in range(len(filelist)):
            if filelist[kdx]==valuesinmacro['cell_name']:
                savingfile=to_file+filelist[kdx]
                
                f=open(savingfile+'/0. drive_strength.txt','w')
                f.write('drive_strength : '+str(valuesinmacro['drive_strength']))
                f.close()

                f=open(savingfile+'/1. description.txt','w')
                f.write(valuesinmacro['description'])
                f.close()

                '''for tdx,tvalue in enumerate(total_hold_table):
                    df4=pd.DataFrame(data=total_hold_table[tvalue]['fall_constraint'],index=total_hold_table[tvalue]['data_transition'],columns=total_hold_table[tvalue]['clock_transition'])
                    df5=pd.DataFrame(data=total_hold_table[tvalue]['rise_constraint'],index=total_hold_table[tvalue]['data_transition'],columns=total_hold_table[tvalue]['clock_transition'])
                    df4.to_csv(savingfile+'/4. hold_timing(fall_constraint): '+tvalue+'.tsv',sep='\t')
                    df5.to_csv(savingfile+'/4. hold_timing(rise_constraint): '+tvalue+'.tsv',sep='\t')

                for tdx,tvalue in enumerate(total_setup_table):
                    df4=pd.DataFrame(data=total_setup_table[tvalue]['fall_constraint'],index=total_setup_table[tvalue]['data_transition'],columns=total_setup_table[tvalue]['clock_transition'])
                    df5=pd.DataFrame(data=total_setup_table[tvalue]['rise_constraint'],index=total_setup_table[tvalue]['data_transition'],columns=total_setup_table[tvalue]['clock_transition'])
                    df4.to_csv(savingfile+'/5. setup_timing(fall_constraint): '+tvalue+'.tsv',sep='\t')
                    df5.to_csv(savingfile+'/5. setup_timing(rise_constraint): '+tvalue+'.tsv',sep='\t')'''

                for tdx in range(len(valuesinmacro['input'])):
                    df1=pd.DataFrame([[valuesinmacro['input'][tdx]['fall_capacitance']],[valuesinmacro['input'][tdx]['rise_capacitance']]],index=['fall_capacitance','rise_capacitance'],columns=[valuesinmacro['input'][tdx]['pin_name']])
                    df1.to_csv(savingfile+'/2. input: '+valuesinmacro['input'][tdx]['pin_name']+'.tsv',sep='\t')
   
                for tdx in range(len(valuesinmacro['output'])):
                    path=savingfile+'/3. output: '+valuesinmacro['output'][tdx]['pin_name']
                    ##os.mkdir(path)
                    data_of_output=list()

                    data_of_output.append([valuesinmacro['output'][tdx]['max_capacitance']])
                    data_of_output.append([valuesinmacro['output'][tdx]['function']])

                    inindexdex=list()
                    inindexdex.append('max_capacitance')
                    inindexdex.append('function')

                    for jdx,jvalue in enumerate(valuesinmacro['output'][tdx]['delay,transition by condition']):
                        if 'cell_fall' in jvalue:

                            data_of_output.append([jvalue.split(', cell_fall')[0].strip()])
                            inindexdex.append('condition_list')

                    df2=pd.DataFrame(data=data_of_output,index=inindexdex,columns=[valuesinmacro['output'][tdx]['pin_name']])
                    df2.to_csv(path+'/0. info.tsv',sep='\t')
                
                    for jdx,jvalue in enumerate(valuesinmacro['output'][tdx]['delay,transition by condition']):
                        data_of_table=valuesinmacro['output'][tdx]['delay,transition by condition'][jvalue][2]

                        df3=pd.DataFrame(data=data_of_table,index=valuesinmacro['output'][tdx]['delay,transition by condition'][jvalue][0]['input_transition'],columns=valuesinmacro['output'][tdx]['delay,transition by condition'][jvalue][1]['load_capacitance'])

                        table_name=str()
                        if int(jdx%4) ==0:
                            table_name=', cell_fall.tsv'
                        elif int(jdx%4) ==1:
                            table_name=', cell_rise.tsv'
                        elif int(jdx%4) ==2:
                            table_name=', fall_transtion.tsv'
                        else:
                            table_name=', rise_transtion.tsv'
                        df3.to_csv(path+'/'+'condition: '+str(jdx//4)+table_name,sep='\t')

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
                                print(macrolist_who_has_no_condition[idx])
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

                        print(macrolist_who_has_no_condition[idx])
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
    type='typ' #### fast, slow,typ
    to_file='../data/OPENSTA/OPENSTA_example_'+type+'/'
    fromfileAddress='../../../../OpenSTA/examples/example1_'+type+'.lib'
    truth_table='../data/macro_info_nangate_'+type

    ##rrr=getMACROname(fromfileAddress,type,to_file)

    ttt=transform_no_condition(to_file)