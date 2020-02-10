import tfpy
import numpy
import numpy.linalg

import os
rows, columns = os.popen('stty size', 'r').read().split()
numpy.set_printoptions(linewidth = int(columns))

with tfpy.MatlabAdapter(existing = True) as ma:
  identity = tfpy.SphericalDesign(3,3,1,tfpy.DesignField.REAL, tfpy.DesignType.EQUAL_NORM, numpy.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]))
  print(f'[3x3 identity] Triple products: {identity.triple_products}')
  print(f'[3x3 identity] As Magma code: {identity.to_magma_code()}')

  design = ma.produce_design(3,6,2, tfpy.DesignField.REAL, tfpy.DesignType.EQUAL_NORM)
  print(f'[Equiangular R^3, equal norm] Best error: {design.error} ')
  norms = []
  for vector in numpy.transpose(design.matrix):
    norms.append(numpy.linalg.norm(vector))
  print(f'[Equiangular R^3, equal norm] Norms of vectors: {numpy.array(norms)} ')
  print(f'[Equiangular R^3, equal norm] Gramian:\n{design.gramian} ')
  print(f'[Equiangular R^3, equal norm] Gramian sanity check (should be zero):\n{design.gramian - ma.compute_gramian(design)} ')

  design = ma.produce_design(5,16,2, tfpy.DesignField.REAL, tfpy.DesignType.WEIGHTED)
  print(f'[2-design in R^5, weighted] Best error: {design.error} ')
  norms = []
  for vector in numpy.transpose(design.matrix):
    norms.append(numpy.linalg.norm(vector))
  print(f'[2-design in R^5, weighted] Norms of vectors: {numpy.array(norms)} ')
  print(f'[2-design in R^5, weighted] Frobenius norm of design matrix: {numpy.linalg.norm(design.matrix)} ')
  print(f'[2-design in R^5, weighted] Gramian:\n{design.gramian} ')

  design = ma.produce_design(4,40,3, tfpy.DesignField.COMPLEX, tfpy.DesignType.EQUAL_NORM)
  print(f'[highly symmetric 3-design in C^4, equal norm] Best error: {design.error} ')
  norms = []
  for vector in numpy.transpose(design.matrix):
    norms.append(numpy.linalg.norm(vector))
  print(f'[highly symmetric 3-design in C^4, equal norm] Norms of vectors: {numpy.array(norms)} ')
  print(f'[highly symmetric 3-design in C^4, equal norm] Gramian:\n{design.gramian} ')

  design = ma.produce_design(5,5,1, tfpy.DesignField.COMPLEX, tfpy.DesignType.EQUAL_NORM)
  print(f'[orthonormal basis in C^5] Best error: {design.error} ')
  print(f'[orthonormal basis in C^5] As Magma code: {design.to_magma_code()}')
  norms = []
  for vector in numpy.transpose(design.matrix):
    norms.append(numpy.linalg.norm(vector))
  print(f'[orthonormal basis in C^5] Norms of vectors: {numpy.array(norms)} ')
  print(f'[orthonormal basis in C^5] Gramian:\n{design.gramian} ')
  print(f'[orthonormal basis in C^5] Triple products: {design.triple_products}')
  print(f'[orthonormal basis in C^5] Triple product sanity check (should be zero): {design.triple_products - ma.compute_triple_products(design)}')

  print('\nNow test design_generator...')
  for design in tfpy.design_generator(range(1,6), range(1,6), range(1,3), [tfpy.DesignField.REAL, tfpy.DesignField.COMPLEX], [tfpy.DesignType.WEIGHTED, tfpy.DesignType.EQUAL_NORM], matlab_adapter = ma):
    print(f'[d = {design.d},\tn = {design.n},\tt = {design.t},\tfield = {design.field.value:7}, type = {design.design_type.value:10}] Error: {design.error}')
