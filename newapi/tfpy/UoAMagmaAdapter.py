import matlab.engine

import pathlib
matlab_dir = pathlib.Path(__file__).absolute().parent.parent / "matlab"

import tfpy.base
import numpy

class UoAMagmaAdapter(object):
  """Encapsulate a Magma instance at the University of Auckland.

  """
  def __init__(self, username, password, server='gauld'):
    self.username = username
    self.password = password
    self.server = server

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
    return False # Don't catch exceptions; in particular, we need GeneratorExit to fall through.

  def numpy_to_matlab_array(self, array):
    "Convert a NumPy array to one that can be passed into the MATLAB API."

    is_complex = (array.dtype == self.np_complex_type)
    return matlab.double(array.tolist(), is_complex = is_complex)


  def matlab_to_numpy_array(self, array):
    "Convert a MATLAB matrix to a NumPy one of the correct type."

    if self.engine.isreal(array):
      return numpy.array(array, self.np_real_type)
    else:
      return numpy.array(array, self.np_complex_type)


  def produce_design(self, d, n, t, field, design_type):
    dp = self.engine.DesignParameters(matlab.double([d]), matlab.double([n]), matlab.double([t]), field.value, design_type.value)
    design, errors, _ = self.engine.produce_design(dp, matlab.double(),nargout=3)

    # Sometimes the MATLAB code produces a singleton array for the errors, which is interpreted
    # by the Python-MATLAB library as a double rather than as a 1x1 matrix.
    if isinstance(errors, float):
      errors = [[errors]]

    # Same as above - if the design is of one vector in 1D, we need to manually make it back into a matrix.
    if isinstance(design, float) or isinstance(design, complex):
      design = [[design]]

    return tfpy.base.SphericalDesign(d, n, t, field, design_type, numpy.array(design), errors[0][-1])

  def compute_triple_products(self, sd):
    products = self.engine.compute_triple_products(self.numpy_to_matlab_array(sd.matrix))
    return numpy.array([p[0] for p in self.matlab_to_numpy_array(products)])

  def compute_gramian(self, sd):
    matrix = self.numpy_to_matlab_array(sd.matrix)
    gramian = self.engine.mtimes(self.engine.ctranspose(matrix), matrix)
    return self.matlab_to_numpy_array(gramian)
