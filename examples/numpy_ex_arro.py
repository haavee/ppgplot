#/usr/bin/env python

import numpy as np
from ppgplot import *

# initialize ploting.
pgbeg("?",1,1)       # open ploting device
pgask(1)                 # wait for user to press a key before erasing.
pgswin(-10,10,-10,10)    # set axis ranges.
                         # label the plot.
pgiden()                 # put user-name and date on plot.

# calculate a suitable function.
f = np.arange(0,2*np.pi,0.25)
fx = np.cos(f);
fy = np.sin(f);

for i in range(f.shape[0]):
    pgslw(i%10+1)           # set line-width
    pgsls(i%5+1)            # set line-style
    pgsci(i%15+1)           # set color-index
    pgarro(fx[i],fy[i],10*fx[i],10*fy[i])

#close the plot.
pgend()

