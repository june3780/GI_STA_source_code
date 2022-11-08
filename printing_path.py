
import json
import sys
import copy
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt
from pylab import rcParams
import os
import shutil

def get_delay_path(wirewire,checking,number):

    address_of_path='../data/deflef_to_graph_and_verilog/results/'+checking+'/test_7800_'+wirewire+'/'

    file_name_of_path=str()
    file_name_of_path=get_file_name(checking,number)[0]
    file_name_of_path=file_name_of_path+'.json'

    if type(number)==type(' '):
        file_name_of_path='scratch_detailed.json'


    with open(address_of_path+file_name_of_path, 'r') as f:
        path_of_delay=json.load(f)
    f.close()

    return{file_name_of_path.replace('.json',''):path_of_delay[0]}





def get_path_of_group(wire_mode,checking):

    path_dictionary=dict()
    idx=str(' ')
    path_of_scrath=get_delay_path(wire_mode,checking,idx)
    ##get_net_info(checking,idx)
    path_dictionary.update(path_of_scrath)

    kidx=int()
    while True:

        something=get_file_name(checking,kidx)[1]
        if something=='continue':
            kidx=kidx+1
            continue

        elif something=='break':
            break

        path_of_scrath=get_delay_path(wire_mode,checking,kidx)
        path_dictionary.update(path_of_scrath)


        kidx=kidx+1
    return path_dictionary






def compare_with_scratch(dictionary,wire_mod,checking,color_number):
    scratch_delay=list()
    for ivalue in dictionary:
        if ivalue=='scratch_detailed':
            scratch_delay=dictionary['scratch_detailed']

    
    tt=int()
    kk=int()
    qq=int()

    percent100_different_path=list()
    diffenrent_path=list()
    same_path_different_unateness=list()
    same_path_same_unateness=list()


    total_number=int()
    total_delay=float()
    mean_total=float()
    std_total=float()

    total_number_with_same_path=int()
    total_delay_with_same_path=float()
    mean_with_same_path=float()
    std_with_same_path=float()

    total_delay_with_different_path=float()


    for ivalue in dictionary:
        if ivalue !='scratch_detailed':
            total_number=total_number+1
            total_delay=total_delay+dictionary[ivalue][-2][2]

            if len(dictionary[ivalue]) !=len(scratch_delay):
                percent100_different_path.append(ivalue)

            else:
                for idx in range(int(len(scratch_delay)/2)):
                    willindex=idx*2
                    if scratch_delay[willindex][0]!=dictionary[ivalue][willindex][0]:
                        diffenrent_path.append(ivalue)
                    elif scratch_delay[willindex][1]!=dictionary[ivalue][willindex][1]:
                        same_path_different_unateness.apend(ivalue)


    mean_total=total_delay/total_number


    setting_path_diff=set(diffenrent_path)
    diffenrent_path=list(setting_path_diff)

    if percent100_different_path!=[]:
        diffenrent_path.extend(percent100_different_path)

    setting_path_diff=set(same_path_different_unateness)
    same_path_different_unateness=list(setting_path_diff)
    will_del=list()
    for ivalue in same_path_different_unateness:
        if ivalue in diffenrent_path:
            will_del.append(ivalue)
    for ivalue in will_del:
        same_path_different_unateness.remove(ivalue)



    best_time=float(total_delay)
    best_path=str()
    worst_time=float()
    worst_path=str()

    best_time1=float(total_delay)
    best_path1=str()
    worst_time1=float()
    worst_path1=str()
    diff_path=list()
    all_path_delay=list()

    delay_list_of_all=list()
    delay_list_of_same_path=list()
    delay_list_of_different_path=list()



    all_path_delay.append('scratch_detailed'+' '+str(scratch_delay[-2][0:2])+' '+str(scratch_delay[-2][2]))
    for ivalue in dictionary:
        if ivalue !='scratch_detailed':
            delay_list_of_all.append(dictionary[ivalue][-2][2])

            square_total=abs(dictionary[ivalue][-2][2]-mean_total)
            std_total=std_total+square_total*square_total

            if best_time1>dictionary[ivalue][-2][2]:
                best_time1=dictionary[ivalue][-2][2]
                best_path1=ivalue
            if worst_time1<dictionary[ivalue][-2][2]:
                worst_time1=dictionary[ivalue][-2][2]
                worst_path1=ivalue

            if ivalue not in diffenrent_path and ivalue not in same_path_different_unateness:
                delay_list_of_same_path.append(dictionary[ivalue][-2][2])
                total_delay_with_same_path=total_delay_with_same_path+dictionary[ivalue][-2][2]
                if best_time>dictionary[ivalue][-2][2]:
                    best_time=dictionary[ivalue][-2][2]
                    best_path=ivalue
                if worst_time<dictionary[ivalue][-2][2]:
                    worst_time=dictionary[ivalue][-2][2]
                    worst_path=ivalue
                all_path_delay.append(ivalue+' '+str(dictionary[ivalue][-2][0:2])+' '+str(dictionary[ivalue][-2][2]))
                same_path_same_unateness.append(ivalue)

            else:
                delay_list_of_different_path.append(dictionary[ivalue][-2][2])
                diff_path.append(ivalue)
                total_delay_with_different_path=total_delay_with_different_path+dictionary[ivalue][-2][2]
                all_path_delay.append(ivalue+' '+str(dictionary[ivalue][-2][0:2])+' '+str(dictionary[ivalue][-2][2]))




    std_total=np.std(delay_list_of_all)
    mean_with_same_path=np.mean(delay_list_of_same_path)
    std_with_same_path=np.std(delay_list_of_same_path)


    address_of_path='../data/deflef_to_graph_and_verilog/results/'+checking+'/test_7800_'+wire_mod+'/path_compare.dat'

    for idx in range(len(all_path_delay)):
        if idx==0:
            fff=open(address_of_path,'w')
            fff.write(all_path_delay[idx]+'\n')
            fff.close()
            ##print(all_path_delay[idx])
        else:
            fff=open(address_of_path,'a')
            fff.write(all_path_delay[idx]+'\n')
            fff.close()

            ##print(all_path_delay[idx])

    print()
    print('changed_path: '+str(len(diffenrent_path)))
    print('same_path_but_different_unate: '+str(len(same_path_different_unateness)))
    print('not_changed_path: '+str(len(same_path_same_unateness)))
    print()
    print('scratch_path: '+'scratch_detailed, timing: '+str(scratch_delay[-2][2])+', last_cell: '+scratch_delay[-2][0])
    print('worst_path(same_path): '+worst_path+', timing: '+str(worst_time))
    print('best_path(same_path): '+best_path+', timing: '+str(best_time))


    ##print('same_path_mean: '+str(mean_with_same_path))
    ##print('same_path_std: '+str(std_with_same_path))

    delay_list_of_same_path.sort()

    cv1_pdf=np.array([])
    if wire_mod !='wire_load':
        cv1_pdf=stats.norm.pdf(delay_list_of_same_path,mean_with_same_path,std_with_same_path)

    ##print('scratch_path: '+'scratch_detailed, timing: '+str(scratch_delay[-2][2])+', last_cell: '+scratch_delay[-2][0])
    print('worst_path: '+worst_path1+', timing: '+str(worst_time1)+', last_cell: '+dictionary[worst_path1][-2][0])
    print('best_path: '+best_path1+', timing: '+str(best_time1)+', last_cell: '+dictionary[best_path1][-2][0])
    ##print('mean: '+str(mean_total))
    ##print('std: '+str(std_total))
    

    delay_list_of_all.sort()

    cv2_pdf=np.array([])
    if wire_mod !='wire_load':
        cv2_pdf=stats.norm.pdf(delay_list_of_all,mean_total,std_total)

    colorlist=get_colors(color_number)

    return [scratch_delay[-2][2],[delay_list_of_same_path, cv1_pdf],[delay_list_of_all, cv2_pdf],colorlist]







def get_other_path_of_delay(range_number_of_path,path_delays,checking,wirewire,number,Pass):
    print()
    list_of_other_ways=list(path_delays.keys())
    list_of_other_ways.remove('scratch_detailed')

    list_x = list()
    list_y = list()
    for rrdx in range(len(list_of_other_ways)):
        maximums_floats=list()
        file_name_of_path=list_of_other_ways[rrdx]+'.json'
        address_of_path='../data/deflef_to_graph_and_verilog/results/'+checking+'/test_7800_'+wirewire+'/'
        with open(address_of_path+file_name_of_path, 'r') as f:
            path_of_delay=json.load(f)
        f.close()

        worst_delay_value=path_of_delay[1][-2][2]
        parsing_the_table=path_of_delay[1:1+range_number_of_path]
        for qidx in range(len(parsing_the_table)):
            maximums_floats.append(parsing_the_table[qidx][-2][2])
        list_x.append(worst_delay_value)
        list_y.append(np.std(maximums_floats))


    colorlist=get_colors(number)
    if Pass!='Pass':
        plt.scatter(list_x, list_y,c=colorlist[1],label=checking+"_all_path")

        plt.xlabel('worst_delay: '+wirewire)
        plt.ylabel('std_of_delays: '+str(range_number_of_path))
    return 0




def get_colors(color_number):
    if color_number==0:
        same_color="salmon"
        all_color="maroon"

    
    elif color_number==1:
        same_color="lightgreen"
        all_color="g"

    elif color_number==2:
        same_color="plum"
        all_color="darkviolet"

    elif color_number==3:
        same_color="royalblue"
        all_color="navy"

    elif color_number==4:
        same_color="lightcyan"
        all_color="aqua"

    elif color_number==5:
        same_color="silver"
        all_color="black"

    elif color_number==6:
        same_color="bisque"
        all_color="darkorange"

    elif color_number==7:
        same_color="lightyellow"
        all_color="yellow"

    elif color_number==8:
        same_color="lightpink"
        all_color="hotpink"

    elif color_number==9:
        same_color="palevioletred"
        all_color="gold"

    elif color_number==10:
        same_color="lightsalmon"
        all_color="teal"

    else:
        same_color="darksalmon"
        all_color="chartreuse"
    

    return [same_color,all_color]









def get_net_info(checking,number):
    defdef=get_file_name(checking,number)[0]
    net_info_data='../data/deflef_to_graph_and_verilog/3. graphs/'+defdef+'_revised(temp)/temporary_net_info_'+defdef+'_revised(temp).json'
    with open(net_info_data, 'r') as f:
        lalala=json.load(f)
    f.close()
    print(len(lalala))
    return 0








def get_file_name(checking,number):


    file_name_of_path=str()
    if checking=='bank':
        file_name_of_path=str(number)+'bank_detailed'
    elif checking=='rbank':
        file_name_of_path=str(number)+'rbank_detailed'
    elif checking=='random':
        file_name_of_path='random'+str(number)+'_detailed'
    elif checking=='a1_bank':
        file_name_of_path='a1_'+str(number)+'bank.txt'
    elif checking=='a1_rbank':
        file_name_of_path='a1_'+str(number)+'rbank.txt'
    elif checking=='a2_bank':
        file_name_of_path='a2_'+str(number)+'bank.txt'
    elif checking=='a2_rbank':
        file_name_of_path='a2_'+str(number)+'rbank.txt'
    elif checking=='Rbank':
        file_name_of_path='rbank'+str(number)
    elif checking=='Rbank2':
        file_name_of_path='rbank'+str(number)+'_detailed'
    elif checking=='random3':
        file_name_of_path='3_random_'+str(number)
    elif checking=='Random':
        file_name_of_path='Random'+str(number)+'_detailed'
    elif checking=='Random2':
        file_name_of_path='Random1103_oneiter_'+str(number)+'_detailed'
    elif checking=='Random2_detailed':
        file_name_of_path='Random1103_oneiter_'+str(number)+'_detailed_detailed'


    strstr=str()
    if checking=='bank' and (number==25 or number==83):
        strstr='continue'

    if (checking=='Rbank' or checking=='Rbank2') and (number==0 or number==1 or number==2):
        strstr='continue'

    if (number==100 and (checking=='bank' or checking=='rbank' or checking=='random' or checking=='random3' or checking=='Random' or checking=="Random2",checking=='Random2_detailed')):
        strstr='break'

    if (number==50 and (checking=='a1_bank' or checking=='a1_rbank')):
        strstr='break'

    if (number==200 and (checking=='a2_bank' or checking=='a2_rbank')):
        strstr='break'

    if (number==103 and (checking=='Rbank' or checking=='Rbank2')):
        strstr='break'


    return [file_name_of_path,strstr]





if __name__ == "__main__":


    wire_mod=sys.argv[1]


    ttt=int()
    for idx in range(int(sys.argv[2])):
        searching=sys.argv[idx+3]
        file_saved_table='../data/deflef_to_graph_and_verilog/results/'+searching+'/test_7800_'+wire_mod
        if 'worst_path_group_of_a_def.json' not in os.listdir(file_saved_table):
            ttt=ttt+1
    if ttt==0:
        scratch_value=float()
        list_name=str()
        for idxx in range(int(sys.argv[2])):
            aaa=dict()

            searching=sys.argv[idxx+3]
            
            addressadd='../data/deflef_to_graph_and_verilog/results/'+searching+'/test_7800_'+wire_mod+'/path_compare.dat'
            shutil.copyfile(addressadd,'../data/7809cells_groups/results/paths/'+searching+'_'+wire_mod+'_path_compare.dat')

            file_saved_table='../data/deflef_to_graph_and_verilog/results/'+searching+'/test_7800_'+wire_mod
            table_npy=np.load(file_saved_table+'/worst_path_group_of_a_def.npy')

            with open(file_saved_table+'/worst_path_group_of_a_def.json', 'r') as file:
                aaa=json.load(file)

            if sys.argv[-1]!='Pass':
                plt.plot(aaa['data'], table_npy,color=get_colors(idxx)[1],label=aaa['label'])
            scratch_value=aaa['scratch_line']
            list_name=list_name+' '+sys.argv[idxx+3]
        list_name=list_name.strip()
        if sys.argv[-1]!='Pass':
            plt.axvline(x=scratch_value,color='k')
            plt.xlabel(wire_mod)
            plt.legend()
            plt.savefig('../data/7809cells_groups/results/'+list_name+'_'+wire_mod+'.png', dpi=400)
            plt.show()
            plt.close()



    scratch_delay=float()
    range_number=int()
    if len(sys.argv) !=int(sys.argv[2])+3:
        range_number=int(sys.argv[int(sys.argv[2])+3])
    else:
        range_number=1

    list_of_all_delay=list()

    if range_number!=0:
        for iiidx in range(int(sys.argv[2])):

            searching=sys.argv[iiidx+3]
            print(searching)
            path_delays=dict()
            path_delays=get_path_of_group(wire_mod,searching)
            list_a1_rbank=compare_with_scratch(path_delays,wire_mod,searching,iiidx)
            if wire_mod=='wire_load':
                continue
            list_of_all_delay.append([list_a1_rbank,searching])
            get_other_path_of_delay(range_number,path_delays,searching,wire_mod,iiidx,sys.argv[-1])

            scratch_delay=list_a1_rbank[0]
            
            print()
        if sys.argv[-1]!='Pass':
            plt.legend()
            plt.show()
            plt.close()


    

    if ttt!=0 and range_number!=0:
        for idxx in range(len(list_of_all_delay)):

            aaa=dict()
            list_a1_rbank=list_of_all_delay[idxx][0]
            searching=list_of_all_delay[idxx][1]
            #plt.plot(list_a1_rbank[1][0], list_a1_rbank[1][1], color=list_a1_rbank[3][0], label=searching+"_same_path")
            
            aaa={'data':list_a1_rbank[2][0],'label':searching+"_all_path",'scratch_line':scratch_delay}
            table_npy=list_a1_rbank[2][1]
            if sys.argv[-1]!='Pass':
                plt.plot(aaa['data'], table_npy,color=get_colors(idxx)[1],label=aaa['label'])
            file_saved_table='../data/deflef_to_graph_and_verilog/results/'+searching+'/test_7800_'+wire_mod
            with open(file_saved_table+'/worst_path_group_of_a_def.json', 'w') as file:
                json.dump(aaa, file)
            np.save(file_saved_table+'/worst_path_group_of_a_def',table_npy)

        if sys.argv[-1]!='Pass':
            plt.axvline(x=scratch_delay,color='k')
            plt.xlabel(wire_mod)
            plt.legend()
            plt.show()
            plt.close()