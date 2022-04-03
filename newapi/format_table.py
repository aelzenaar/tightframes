import tfpy

threshold = 1e-9

print('t,d,n,field,type,error')
minimals = {}
with tfpy.DatabaseAdapter() as db:
  designs = db.search()
  for design in designs:
    if design.error < threshold:
      if (design.t,design.d,design.field,design.design_type) in minimals:
        if minimals[(design.t,design.d,design.field,design.design_type)].n < design.n:
          continue
        elif minimals[(design.t,design.d,design.field,design.design_type)].n == design.n and minimals[(design.t,design.d,design.field,design.design_type)].error < design.error:
          continue
      minimals[(design.t,design.d,design.field,design.design_type)] = design

for _, design in minimals.items():
  print(f'{design.t},{design.d},{design.n},{design.field.value},{design.design_type.value},{design.error}')
