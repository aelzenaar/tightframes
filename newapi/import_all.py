from matlab.engine import MatlabExecutionError
from pathlib import Path
import argparse
import sys
import shutil
from datetime import datetime
import numpy.linalg

import tfpy

parser = argparse.ArgumentParser(description='Import many .mat files into one database.')
parser.add_argument('directory', metavar='DIR', help='directory to scan')
parser.add_argument('-R','--recursive', action='store_true', help='scan DIR recursively')
parser.add_argument('-e','--existing', action='count', default=0, help='connect to a running MATLAB session; specify twice to skip MATLAB verification prompt')

args = parser.parse_args()
search_dir = Path(args.directory)
if not search_dir.is_dir():
    sys.exit('Argument is not a directory.')

recurse = (args.recursive == True)
existing = args.existing

if recurse:
    mat_files = sorted(list(search_dir.glob('**/*.mat')))
else:
    mat_files = sorted(list(search_dir.glob('*.mat')))

# -e but not -ee specified, so print usage and wait for user OK.
if existing == 1:
    print('In the running MATLAB session enter the command:\tmatlab.engine.shareEngine')
    input("Press Enter to continue...")

count = 0
with tfpy.DatabaseAdapter(collection = 'designs') as db:
  with tfpy.MatlabAdapter(existing = (existing == 1)) as ma:
    for f in mat_files:
      matfile = ma.engine.matfile(str(f.resolve()))

      try:
        matrix = numpy.array(ma.engine.getfield(matfile,'result'))
        d = int(ma.engine.getfield(matfile, 'd'))
        n = int(ma.engine.getfield(matfile, 'n'))
        t = int(ma.engine.getfield(matfile, 't'))
        try:
          error = (ma.engine.getfield(matfile, 'errors'))[0][-1]
        except TypeError:
          # Maybe it's a singleton matrix.
          error = float(ma.engine.getfield(matfile, 'errors'))
        print(f'Saw {str(f)}\t\tand copying: ',end='',flush=True)
      except MatlabExecutionError as e:
        print(f'Saw {str(f)}\t\tNo result array.',flush=True)
        continue


      # Guess field.
      field = tfpy.DesignField.REAL
      for row in matrix:
        for cell in row:
          if complex(cell).imag > 1e-4:
            field = tfpy.DesignField.COMPLEX

      if field == tfpy.DesignField.REAL:
        matrix = numpy.array([[complex(cell).real for cell in row] for row in matrix])

      # Guess type.
      design_type = tfpy.DesignType.WEIGHTED if ((numpy.linalg.norm(matrix) - 1) <= 1e-4) else tfpy.DesignType.EQUAL_NORM


      try:
        db.insert(tfpy.SphericalDesign(d, n, t, field, design_type, matrix, error))
        print(f'd = {d}, n = {n}, t={t}, field={field.value}, type={design_type.value}, error={error}',flush=True)
        count = count + 1
      except tfpy.DimensionError as e:
        print(f'broken dimension: {str(e)}, not adding',flush=True)

print(f'Imported {count} files in total.')
