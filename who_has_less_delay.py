



def get_info(defdef):
    f=open(defdef,'r')
    who_has_less=str()
    best_delay=float(10000000000)
    while True:
        line=f.readline()
        if not line:
            break
        if best_delay>float(line.split('HPWL: ')[1].strip()):
            best_delay=float(line.split('HPWL: ')[1].strip())
            who_has_less=line
        
    f.close()
    print(who_has_less)


    return 0








if __name__ == "__main__":
    what_is_that='a2'
    bank_or_rbank='rbank'
    defdef='../data/hpwl_result_'+what_is_that+'_'+bank_or_rbank+'.txt'
    get_info(defdef)