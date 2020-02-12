import tfpy

with tfpy.DatabaseAdapter() as da:
  for design in tfpy.design_table_generator(4, 5, tfpy.ALL_FIELDS, tfpy.ALL_DESIGN_TYPES):
    print(f'[d = {int(design.d):3},\tn = {int(design.n):4},\tt = {int(design.t):3},\tfield = {design.field.value:7}, type = {design.design_type.value:10}] Minimal error: {design.error}', flush = True)
    da.insert(design)
