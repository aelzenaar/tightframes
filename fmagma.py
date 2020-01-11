import matlab.engine
from pathlib import Path
import argparse
import sys
import shutil
from datetime import datetime

import contextlib

@contextlib.contextmanager
def smart_open(filename=None):
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()

parser = argparse.ArgumentParser(description='Format a given spherical design in Magma matrix format')
parser.add_argument('filename', metavar='MATFILE', help='.mat file to read from')
parser.add_argument('-o','--output', default=None, help='output file (default is stdout)')
parser.add_argument('-e','--existing', action='count', default=0, help='connect to a running MATLAB session; specify twice to skip MATLAB verification prompt')
parser.add_argument('-u','--unit', default='i', help='name of complex unit (default is `i\')')
parser.add_argument('-f','--field', default='CC', help='name of complex field (default is `CC\')')
parser.add_argument('-v','--var', default='V', help='name of array variable to product (default is `V\')')

args = parser.parse_args()
filename = Path(args.filename)
output_filename = args.output

unit = args.unit
field = args.field
var = args.var

if not filename.exists():
    sys.exit('Input file does not exist.')

existing = args.existing

# -e but not -ee specified, so print usage and wait for user OK.
if existing == 1:
    print('In the running MATLAB session enter the command:\tmatlab.engine.shareEngine')
    input("Press Enter to continue...")


if existing > 0:
    if(matlab.engine.find_matlab() == ()):
        sys.exit('MATLAB is not running, or you didn\'t heed the prompt...')
    eng = matlab.engine.connect_matlab()
else:
    eng = matlab.engine.start_matlab()

matfile = eng.matfile(str(filename.resolve()))
result = eng.getfield(matfile,'result')
if result == None:
    sys.exit('No result array in input file.')


rows = int(eng.size(result, 1));
cols = int(eng.size(result, 2));
reals = eng.real(result);
imags = eng.imag(result);

with smart_open(output_filename) as f:
    f.write(f'{var}:=Matrix({field},{rows},{cols},[\n')
    for i in range(0,rows):
        for j in range(0,cols):
            f.write(f'    {reals[i][j]:.40} + {imags[i][j]:.40}*{unit}')
            if not ((i == rows - 1) and (j == cols - 1)):
                f.write(',\n')
    f.write('\n]);\n')
