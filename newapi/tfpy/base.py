from enum import Enum
import json
import numpy
import tfpy.matrix_translations as matrix_translations
from copy import deepcopy

class DesignField(Enum):
  """The field of definition of a spherical design."""
  REAL = 'real'
  COMPLEX = 'complex'

ALL_FIELDS = [DesignField.REAL, DesignField.COMPLEX]

class DesignType(Enum):
  """The type of a spherical design."""
  WEIGHTED = 'weighted'
  EQUAL_NORM = "equal_norm"

ALL_DESIGN_TYPES = [DesignType.WEIGHTED, DesignType.EQUAL_NORM]

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

def triples(lst):
  n = len(lst)
  for i in range(n):
    for j in range(n):
      for k in range(n):
        yield lst[i],lst[j],lst[k]

class SphericalDesign(object):
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
    self.d = int(d)
    self.n = int(n)
    self.t = int(t)
    self.field = field
    self.design_type = design_type
    self.error = error
    self._gramian = None
    self._triple_products = None

    if matrix is not None and matrix.shape != (self.d,self.n):
      raise DimensionError((self.d,self.n), matrix.shape)
    self.matrix = matrix

  @property
  def gramian(self):
    "Compute the Gram matrix of the design."
    if self._gramian is None:
      self._gramian = numpy.matmul(self.matrix.conj().T, self.matrix)
    return self._gramian

  @property
  def triple_products(self):
    "Compute the sorted list of 3-products of the design."
    if self._triple_products is None:
      self._triple_products = []
      for u,v,w in triples(self.matrix):
        self._triple_products.append(numpy.dot(u,v)*numpy.dot(v,w)*numpy.dot(w,u))
      self._triple_products = numpy.sort(numpy.array(self._triple_products)[::-1])

    return self._triple_products

  @classmethod
  def from_dict(cls, dct):
    "Construct a SphericalDesign from a return value of to_dict()."
    if 'matrix' in dct:
      if dct['field'] == 'complex':
        matrix = numpy.array([[complex(cell[0],cell[1]) for cell in row] for row in dct['matrix']])
      elif dct['field'] == 'real':
        # Some code somewhere is sometimes putting real values into the form [real, imag] where imag = 0. Catch this here.
        if isinstance(dct['matrix'][0][0], list):
          matrix = numpy.array([[float(cell[0]) for cell in row] for row in dct['matrix']])
        else:
          matrix = numpy.array(dct['matrix'])
      else:
        assert False # should not get here
    else:
      matrix = None

    new_design = cls(dct['d'], dct['n'], dct['t'], DesignField(dct['field']), DesignType(dct['design_type']), matrix)

    if 'error' in dct:
      new_design.error = dct['error']
    if 'triple_products' in dct:
      new_design._triple_products = dct['triple_products']
    if 'gramian' in dct:
      new_design._gramian = dct['gramian']
    return new_design

  def to_dict(self):
    "Return a serialisable dictionary that can be used to recreate this design using from_dict()."
    dct = deepcopy(vars(self))

    if '_gramian' in dct:
      dct['gramian'] = dct.pop('_gramian')

    if '_triple_products' in dct:
      dct['triple_products'] = dct.pop('_triple_products')

    dct['field'] = dct['field'].value
    dct['design_type'] = dct['design_type'].value
    if self.field == DesignField.COMPLEX:
      dct['matrix'] = [[(cell.real, cell.imag) for cell in row] for row in dct['matrix'].tolist()]
    elif self.field == DesignField.REAL:
      dct['matrix'] = dct['matrix'].tolist()
    else:
      assert False # Should never get here.


    return dct

  # Helper constants for to_magma_code.
  _FIELD_MAP = {DesignField.REAL:'RealField', DesignField.COMPLEX:'ComplexField'}
  _MAGMA_FORMAT = """load "ComputeSymmetry.magma";
Attach("FrameSymmetry.m");
SetVerbose("FrameSymmetry",2);

CC<i> := {field_name}({accuracy});

V:=Matrix(CC,{d},{n},
{matrix_rows}
);

G := FrameSymmetry(CanonicalGramian(V));

"""

  def to_magma_code(self, accuracy = 32, format_string = _MAGMA_FORMAT):
    """Return formatted Magma code that can be used directly with the ComputeSymmetry.magma script.

      Parameters
        accuracy -- number of decimal places to output to.
        format_string -- a Python format string that is used for the generation. The available
                        format fields are:
                          * field_name -- either ComplexField or RealField
                          * matrix_rows -- a set of comma separated values, going row-by-row down the matrix
                          * accuracy -- the argument to this method
                          * d, n, t -- design parameters
    """
    return format_string.format(d = self.d, n = self.n, t = self.t, accuracy = accuracy, field_name = self._FIELD_MAP[self.field], matrix_rows = matrix_translations.array_to_magma(self.matrix, accuracy))

  def to_matlab_code(self, accuracy = 32):
    """Return formatted MATLAB code to reproduce the stored design.

      Parameters
        accuracy -- number of decimal places to output to.
    """
    return matrix_translations.array_to_matlab(self.matrix, accuracy)
