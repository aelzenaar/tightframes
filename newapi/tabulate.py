import tfpy

with tfpy.DatabaseAdapter() as da:
  for design in tfpy.design_table_generator(1, 1, tfpy.ALL_FIELDS, tfpy.ALL_DESIGN_TYPES):
    print(f'[d = {int(design.d)},\tn = {int(design.n)},\tt = {int(design.t)},\tfield = {design.field.value:7}, type = {design.design_type.value:10}] Minimal error: {design.error}', flush = True)
    da.insert(design)
