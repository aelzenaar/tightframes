from enum import Enum
import json
import numpy

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
    self.d = d
    self.n = n
    self.t = t
    self.field = field
    self.design_type = design_type
    self.error = error
    self._gramian = None
    self._triple_products = None

    if matrix is not None and matrix.shape != (d,n):
      raise DimensionError((d,n), matrix.shape)
    self.matrix = matrix

  @property
  def gramian(self):
    if self._gramian is None:
      self._gramian = numpy.matmul(self.matrix.conj().T, self.matrix)
    return self._gramian

  @property
  def triple_products(self):
    if self._triple_products is None:
      self._triple_products = []
      for u,v,w in triples(self.matrix):
        self._triple_products.append(numpy.dot(u,v)*numpy.dot(v,w)*numpy.dot(w,u))
      self._triple_products = numpy.sort(numpy.array(self._triple_products)[::-1])
      print(self._triple_products)

    return self._triple_products

  @classmethod
  def from_dict(cls, dct):
    if 'matrix' in dct:
      matrix = dct['matrix']
    else:
      matrix = None

    new_design = cls(dct['d'], dct['n'], dct['t'], DesignType(dct['field']), DesignType(dct['design_type']), matrix)

    if 'error' in dct:
      new_design.error = dct['error']
    if 'triple_products' in dct:
      new_design._triple_products = dct['triple_products']
    if 'gramian' in dct:
      new_design._gramian = dct['gramian']

  def to_dict(self):
    dct = dict(self)

    if '_gramian' in dct:
      dct['gramian'] = dct.pop('_gramian')

    if '_triple_products' in dct:
      dct['triple_products'] = dct.pop('_triple_products')

    dct['field'] = dct['field'].value
    dct['design_type'] = dct['design_type'].value

    return dct
