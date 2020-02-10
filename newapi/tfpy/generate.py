import tfpy.base
import tfpy.MatlabAdapter

def design_generator(d_range, n_range, t_range, field_range, design_type_range, matlab_adapter = None):
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
