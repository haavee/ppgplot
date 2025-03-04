#/usr/bin/env python
#
#  pgex1: freely taken after PGDEMO1.F
#
import ppgplot
import numpy as np
import sys

# create an array 
xs=[1.,2.,3.,4.,5.]
ys=np.array([1.,4.,9.,16.,25.])

# creat another array
yr = 0.1*np.array(range(0,60))
xr = yr*yr


# pgplotting
if len(sys.argv) > 1: # if we got an argument use the argument as devicename
	ppgplot.pgopen(sys.argv[1])
else:
	ppgplot.pgopen('?')
ppgplot.pgenv(0.,10.,0.,20.,0,1)
ppgplot.pglab('(x)', '(y)', r'PGPLOT Example 1:  y = x\u2')
ppgplot.pgpt(xs,ys,9)
ppgplot.pgline(xr,yr)
ppgplot.pgclos()
