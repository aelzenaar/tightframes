import tfpy

threshold = 1e-9

print('n,error')
minimals = {}
with tfpy.DatabaseAdapter() as db:
  for design in db.search(d = [5], t = [3], field = [tfpy.DesignField.REAL], design_type = [tfpy.DesignType.EQUAL_NORM]):
    if design.n in minimals:
      if minimals[design.n] < design.error:
        continue
    minimals[design.n] = design.error

for n, err in minimals.items():
  print(f'{n},{err}')
