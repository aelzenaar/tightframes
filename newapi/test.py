import tfpy
import numpy

with tfpy.MatlabAdapter() as ma:
  identity = tfpy.SphericalDesign(3,3,1,tfpy.DesignField.REAL, tfpy.DesignType.EQUAL_NORM, numpy.array([[1,0,0],[0,1,0],[0,0,1]]))
  identity_prods = ma.compute_triple_products(identity)
  print(identity_prods)
  design = ma.produce_design(3,6,2, tfpy.DesignField.REAL, tfpy.DesignType.EQUAL_NORM)
  print(design.matrix)
  print(ma.compute_gramian(design))
