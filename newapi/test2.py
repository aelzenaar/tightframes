import tfpy
import numpy

import sys
import os
rows, columns = os.popen('stty size', 'r').read().split()
numpy.set_printoptions(linewidth = int(columns),precision=4)

with tfpy.DatabaseAdapter() as da:
  for design in tfpy.design_generator([3], [48], [4], [tfpy.DesignField.REAL], [tfpy.DesignType.EQUAL_NORM]):
    print(f'[d = {int(design.d):3},\tn = {int(design.n):4},\tt = {int(design.t):3},\tfield = {design.field.value:7}, type = {design.design_type.value:10}] Minimal error: {design.error}', flush = True)
    da.insert(design)
    #print(design.gramian)
    #print(design.to_matlab_code())

#with tfpy.DatabaseAdapter() as da:
  #for design in da.search(d = [3], n = [27], t = [3], field=[tfpy.DesignField.COMPLEX], design_type=[tfpy.DesignType.EQUAL_NORM]):
    #if design.error < 1e-11:
      #print(design.to_magma_code())
      #print()
