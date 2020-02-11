import tfpy.base
import tfpy.MatlabAdapter
from scipy.special import comb as nchoosek
import numpy

def design_generator(d_range, n_range, t_range, field_range, design_type_range, matlab_adapter = None):
  """Generate best approximations to spherical designs for given sets of parameters.

    Parameters:
      d_range, n_range, t_range -- lists of numerical parameters for the t-design.
      field_range -- a list of tfpy.DesignField values giving the field(s) to search in.
      design_type_range -- a list of tfpy.DesignType values specifying the type of design to find.
      matlab_adapter -- use an existing MatlabAdapter object (optional)
  """

  # Peform the actual loop in a dummy function, so that we can wrap it in a context manager if
  # needed without duplicate code.
  def dummy(ma):
    for d in d_range:
      for n in n_range:
        for t in t_range:
          for field in field_range:
            for design_type in design_type_range:
              yield ma.produce_design(d,n,t,field,design_type)

  if matlab_adapter is None:
    with tfpy.MatlabAdapter(existing = True) as ma:
      return dummy(ma)
  else:
      return dummy(matlab_adapter)


def lower_bound_n(d,t):
  if t % 2 == 0:
    e = t/2
    return nchoosek(d + e - 1, d - 1) + nchoosek(d + e - 2, d - 1)
  else:
    e = (t-1)/2
    return 2*nchoosek(d + e - 1, d - 1)


def to_infinity_and_beyond(counter):
  index = counter - 1
  while True:
    index = index + 1
    yield index


def design_table_generator(d_min, t_min, field_range, design_type_range, list_from = 0, threshold = 1e-10, matlab_adapter = None):
  def dummy(ma):
    for h in to_infinity_and_beyond(list_from):
        # Apply inverse Cantor pairing to h (https://en.wikipedia.org/wiki/Pairing_function#Inverting_the_Cantor_pairing_function)
        w = numpy.floor((numpy.sqrt(8*h+1)-1)/2)
        v = (w**2 + w)/2
        d = h - v
        t = w - d

        d = d + d_min
        t = t + t_min
        n_min = lower_bound_n(d, t)

        for field in field_range:
          for design_type in design_type_range:
            break_loop_on_reentry = False
            for n in to_infinity_and_beyond(n_min):
              if break_loop_on_reentry:
                break
              design = ma.produce_design(d,n,t,field,design_type)
              if design.error < threshold:
                break_loop_on_reentry = True
                yield design

  if matlab_adapter is None:
    with tfpy.MatlabAdapter(existing = True) as ma:
      return dummy(ma)
  else:
      return dummy(matlab_adapter)
