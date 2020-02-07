from enum import Enum
import json

class DesignField(Enum):
  """The field of definition of a spherical design."""
  REAL = 'real'
  COMPLEX = 'complex'

class DesignType(Enum):
  """The type of a spherical design."""
  WEIGHTED = 'weighted'
  EQUAL_NORM = "equal_norm"

class TFError(Exception):
  """Base exception class for tfpy."""
  pass

class DimensionError(TFError):
  """Exception raised when a matrix is of unexpected dimension."""
  def __init__(self, expected_shape, actual_shape):
    self.expected_shape = expected_shape
    self.actual_shape = actual_shape

  def __str__(self):
    return f'DimensionError: Incorrect matrix dimension; expected {self.expected_shape}, got {self.actual_shape}.'

class SphericalDesign():
  """A class representing a spherical t-design in Python.

  Attributes:
      d (int): dimension of space the design is embedded in.
      n (int): number of vectors in the design.
      t (int): parameter of the design.
      field (base.DesignField): the field the design is over.
      design_type (base.DesignType): the type of design.
      matrix (numpy.array): the actual data of the design.
  """

  def __init__(self, d, n, t, field, design_type, matrix = None, error = None):
    self.d = d
    self.n = n
    self.t = t
    self.field = field
    self.design_type = design_type
    self.error = error

    if matrix is not None and matrix.shape != (d,n):
      raise DimensionError((d,n), matrix.shape)
    self.matrix = matrix
