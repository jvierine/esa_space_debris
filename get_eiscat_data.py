#!/usr/bin/env python

import numpy as n
import glob
import h5py
import re
import os

h5fl = glob.glob("data/*.h5")
h5fl.sort()

fl=glob.glob("/home/j/culebra/leo_pwait_2.3u_3P@uhf/2*/*.mat")
fl.sort()

times=[]
for f in fl:
    times.append(float(re.search(".*/(2.*).mat",f).group(1)))
times=n.array(times)-12.8/2.0
print(times)

for hf in h5fl:
    h=h5py.File(hf,"r")
    print(h["name"].value)
    for s in h["eiscat_secs"].value:
        idx=n.argmin(n.abs(s-times))
        if (n.abs(s-times[idx]) < 20.0):
            print("found %s %1.2f"%(fl[idx],s))
            os.system("rsync -av %s data/"%(fl[idx]))
            os.system("rsync -av %s data/"%(fl[idx-1]))
            os.system("rsync -av %s data/"%(fl[idx+1]))

    h.close()
    


