import matlab.engine

import pathlib
matlab_dir = pathlib.Path(__file__).absolute().parent.parent / "matlab"

import tfpy.base
import numpy

class MatlabAdapter():
  def __init__(self, existing = False, np_real_type = 'float64', np_complex_type = 'complex128'):
    self.existing = existing
    self.np_real_type = np_real_type
    self.np_complex_type = np_complex_type

  def __enter__(self):
    if(self.existing):
      self.engine = matlab.engine.connect_matlab()
    else:
      self.engine = matlab.engine.start_matlab()

    self.engine.addpath(str(matlab_dir))
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    if not(self.existing):
      self.engine.quit()

  def numpy_to_matlab_array(self, array):
    return matlab.double(array.tolist())

  def matlab_to_numpy_array(self, array):
    if self.engine.isreal(array):
      return numpy.array(array, self.np_real_type)
    else:
      return numpy.array(array, self.np_complex_type)


  def produce_design(self, d, n, t, field, design_type):
    dp = self.engine.DesignParameters(matlab.double([d]), matlab.double([n]), matlab.double([t]), field.value, design_type.value)
    design, errors, _ = self.engine.produce_design(dp, matlab.double(),nargout=3)
    return tfpy.base.SphericalDesign(d, n, t, field, design_type, numpy.array(design), errors[-1])

  def compute_triple_products(self, sd):
    products = self.engine.compute_triple_products(self.numpy_to_matlab_array(sd.matrix))
    return self.matlab_to_numpy_array(products)

  def compute_gramian(self, sd):
    matrix = self.numpy_to_matlab_array(sd.matrix)
    gramian = self.engine.mtimes(self.engine.ctranspose(matrix), matrix)
    return self.matlab_to_numpy_array(gramian)
