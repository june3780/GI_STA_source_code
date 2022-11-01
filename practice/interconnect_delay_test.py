from selectors import EpollSelector
import numpy as np







dri_resist=7326
dri_cap=24.57

wire_resist=123.1
wire_cap=1.23

load_cap=35.1

n=10000000

############################ 파이형태로 딜레이
willsum=float()
sum=float()
for idx in range(n+1):
    if idx ==0:
        willsum=dri_resist*(dri_cap+(wire_cap/(2*n)))
    elif idx ==n:
        willsum=(dri_resist+wire_resist)*(wire_cap/(2*n))
    else:
        willsum=(dri_resist+(idx*(wire_resist/n)))*(wire_cap/(n))
    sum=sum+willsum



print(sum/1000000)