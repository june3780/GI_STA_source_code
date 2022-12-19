import json
import sys


def comparing(aa,bb):

    bblist=list()
    bbb=list()
    for ivalue in bb:
        bblist.append(ivalue.replace('\n','').split(' ')[0])
        bbb.append(ivalue.replace('\n','').split(' ')[-2].split('/')[0])
    del bbb[0]
    del bblist[0]
    del aa[0]
    del bb[0]
    tdtd=int()
    kk=float()
    print('checking')
    for idx in range(len(aa)):
        if '\\' in aa[idx][3]:
            aa[idx][3]=aa[idx][3].replace('\\','__')
        if '[' in aa[idx][3]:
            aa[idx][3]=aa[idx][3].replace('[','__')
        if ']' in aa[idx][3]:
            aa[idx][3]=aa[idx][3].replace(']','__')
        if aa[idx][3]!=bbb[idx]:
            tdtd=tdtd+1
            print(idx,aa[idx],bbb[idx])
    print('fin')
    print(tdtd)
    print('tpgmlwns1!')

    ttt=int()
    for idx in range(len(aa)):
        if get_approximate(aa[idx][0])!=float(bb[idx].split(' ')[0]) or get_approximate(aa[idx][1])!=float(bb[idx].split(' ')[1]):
            ttt=ttt+1
            kk=kk+abs(aa[idx][0]-float(bb[idx].split(' ')[0]))+abs(aa[idx][1]-float(bb[idx].split(' ')[1]))
            print(aa[idx],bb[idx])
            print()


    print('tpgmlwns1!!')
    print(ttt)
    print(len(bb))
    print(len(aa))
    print(kk)
    return 0






def get_approximate(one_float):
    flow=float()
    if len(str(one_float).split('.')[1])==1 or len(str(one_float).split('.')[1])==2:
        flow=one_float
    else:
        flow=float(str(one_float).split('.')[0]+'.'+str(one_float).split('.')[1][0]+str(one_float).split('.')[1][1])
        if len(str(one_float).split('.')[1])>2:
            if int(str(one_float).split('.')[1][2])>=5:
                if int(str(one_float).split('.')[1][1])==9:
                    if int(str(one_float).split('.')[1][0])==9:
                        flow=float(str((int(str(one_float).split('.')[0])+1))+'.'+str(00))
                    else:
                        flow=float(str(one_float).split('.')[0]+'.'+str(int(str(one_float).split('.')[1][0])+1)+str(0))
                else:
                    flow=float(str(one_float).split('.')[0]+'.'+str(one_float).split('.')[1][0]+str(int(str(one_float).split('.')[1][1])+1))

    return flow


if __name__ == "__main__":
    with open(sys.argv[1]+'temp_sta.json','r') as fw:
        aaa=json.load(fw)
    fw.close()
    opensta='opensta_temp_'+sys.argv[1]+'.txt'
    file = open(opensta, "r")
    strings = file.readlines()
    file.close()
    comparing(aaa,strings)#FE_OFC173028_n176837/o