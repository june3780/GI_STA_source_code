from matplotlib import pyplot as plt
import numpy as np
import sys



def get_plt():
    gcd=[8.799919605255127,7.884354114532471,8.29155707359314,0.7883050441741943,0.220083690]
    scratch=[323.0312101840973,183.53912711143494,10.012068748474121,1.6116087436676025,0.459601564]
    superblue=[0.0,0.0,404.3744077682495,229.6896641254425,41.839603512]
    checking__gcd=[39.984424131,35.824345341,37.674564042,3.581842181,1]
    checking_scratch=[702.850545966,399.344000299,21.784235592,3.506534507,1]
    checking_super=[0.0,0.0,9.664871888,5.489766748,1]

    if sys.argv[2]==str(1):
        gcd=[0.0,0.0,8.29155707359314,0.7883050441741943,0.220083690]
        scratch=[0.0,0.0,10.012068748474121,1.6116087436676025,0.459601564]
        checking__gcd=[0.0,0.0,37.674564042,3.581842181,1]
        checking_scratch=[0.0,0.0,21.784235592,3.506534507,1]
        checking_super=[0.0,0.0,9.664871888,5.489766748,1]
    fig, ax = plt.subplots(figsize=(30,30))
    bar_width = 0.25
    index=np.arange(5)
    if sys.argv[1]=='gcd':
        plt.bar(index+bar_width,gcd,color='red',alpha=0.4,label='gcd')
    elif sys.argv[1]=='scratch_detailed':
        plt.bar(index+bar_width,scratch,color='blue',alpha=0.4,label='scratch_detailed')
    elif sys.argv[1]=='superblue16':
        plt.bar(index+bar_width,superblue,color='green',alpha=0.4,label='superblue16')

    elif sys.argv[1]=='gcd_multiple':
        plt.bar(index+bar_width,checking__gcd,color='red',alpha=0.4,label='gcd')
    elif sys.argv[1]=='scratch_detailed_multiple':
        plt.bar(index+bar_width,checking_scratch,color='blue',alpha=0.4,label='scratch_detailed')
    elif sys.argv[1]=='superblue16_multiple':
        plt.bar(index+bar_width,checking_super,color='green',alpha=0.4,label='superblue16')

    xinfo=['python_version_1_X','python_version_1_O','python_version_2_X','python_version_2_O','openSTA']
    plt.xticks(np.arange(bar_width, 5 + bar_width, 1), xinfo)
    plt.xlabel('def', size = 13)
    plt.ylabel('second', size = 13)
    plt.legend()
    plt.show()

    print('gcd: 182 components')
    print('scratch_detailed: 7809 components')
    print('superblue: 981559 components')
    return 0



if __name__ == "__main__":
    get_plt()