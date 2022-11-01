
import json



def get_start_points(All,strstr):
    list_points=list()
    max_stage_number=int()



    for idx,ivalue in enumerate(All):
        if All[ivalue]['stage'][0]>max_stage_number:
            max_stage_number=All[ivalue]['stage'][0]
    
    if len(All[strstr]['to'])!=0:
        print('the pin is not Sequential input pin')
        return 0
   
    else:
        get_list(All,strstr,list_points)
        qlist=list(set(list_points))
        will_del=list()

        for idx in range(len(qlist)):
            if 'PIN' in qlist[idx]:
                will_del.append(idx)

        will_del.reverse()
        
        for qdd in range(len(will_del)):
            del qlist[will_del[qdd]]
        return qlist




def get_list(All,strstr,listlist):

    checking=All[strstr]['from'][0]
    if len(All[checking]['from'])==0:
        listlist.append(checking)
    else:
        for idx in range(len(All[checking]['from'])):
            get_list(All,All[checking]['from'][idx],listlist)
    return listlist


def get_clk_list(listlist):
    new_list=str()
    new_new=list()
    new_new=(listlist.replace("'",'').replace('Q','').replace(', ','').replace('l','').strip().split(' '))
    for idx in range(len(new_new)):
        new_new[idx]='clk'+str(int(new_new[idx]))+' '
    for idx in range(len(new_new)):
        new_list=new_list+new_new[idx]
    
    new_list='create_clock -name clk -period 10 {'+new_list.rstrip()+'}'
    return new_list


def get_have_a_lunch(qstrstr):
    tcl_file=['define_corners wc\n', 'read_liberty -corner wc example1_slow.lib\n', 'read_verilog not_yet_verilog.v\n', 'link_design top\n', \
        qstrstr+'\n', \
            'set_input_delay -clock clk 0 {temporary_net1 temporary_net2 temporary_net0 x1006 x1034 x1062 x1101 x1126 x1155 x1193 x1203 x1209 x1215 x1231 x1261 x1286 x130629 x130630 x130631 x130632 x130633 x130634 x130635 x130636 x130637 x130638 x130639 x130640 x130641 x130642 x130643 x130644 x130645 x130646 x130647 x130648 x130649 x130650 x130651 x130652 x130653 x130654 x130655 x130656 x130657 x1322 x1345 x1351 x1358 x1366 x1374 x1382 x1390 x1398 x1406 x1417 x1424 x1432 x1443 x1451 x1459 x1467 x1479 x1486 x1494 x1501 x1511 x1519 x1527 x1534 x1542 x1550 x1557 x1564 x1572 x1580 x1587 x1595 x1822 x806 x821 x837 x868 x889 x906 x940}\n', 
            'report_checks\n', 'exit\n']
    file_target='../data/deflef_to_graph_and_verilog/5. verilogs_with_tcl/ac97_ctrl_revised_by_june(temp)/whoareyou.tcl'
    ff= open(file_target,'w')
    ff.writelines(tcl_file)


    return 0



file_pathpath='temp.json'
list_of_last_nodes=dict()
with open (file_pathpath,'r') as ff:
    delay_without_clk_All=json.load(ff)


last_outnodes=list()
for idx,ivalue in enumerate(delay_without_clk_All):
    if delay_without_clk_All[ivalue]['stage'][1]=='INPUT' and len(delay_without_clk_All[ivalue]['from']) !=0 and len(delay_without_clk_All[ivalue]['to']) ==0 and delay_without_clk_All[ivalue]['type'] =="cell":
        last_outnodes.append(ivalue)



for idx in range(len(last_outnodes)):
    listlist=get_start_points(delay_without_clk_All,last_outnodes[idx])
    if len(listlist)==0:
        continue

    qstrstr=str()
    for idx in range(len(listlist)):
        listlist[idx]="\'"+listlist[idx]+"\'"
        if idx==0:
            qstrstr=listlist[0]
        else:
            qstrstr=qstrstr+', '+listlist[idx]
    qstrstr=qstrstr.lstrip()


    qstrstr=get_clk_list(qstrstr)
    get_have_a_lunch(qstrstr)