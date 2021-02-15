import matlab.engine
from pathlib import Path
import argparse
import sys
import shutil
from datetime import datetime

parser = argparse.ArgumentParser(description='Generate a database of designs from a given set of runtf.m output files.')
parser.add_argument('directory', metavar='DIR', help='directory to scan')
parser.add_argument('-R','--recursive', action='store_true', help='scan DIR recursively')
parser.add_argument('-e','--existing', action='count', default=0, help='connect to a running MATLAB session; specify twice to skip MATLAB verification prompt')
parser.add_argument('-t','--threshold', action='store', default=0, help='threshold to include, error must be < 10^-t')
parser.add_argument('-o','--output', default='html', help='output directory')
parser.add_argument('-u','--unique', action='count', default = 0, help='keep only the best value for each t,d,n; specify twice to only keep the best n meeting the threshold')

args = parser.parse_args()
search_dir = Path(args.directory)
if not search_dir.is_dir():
    sys.exit('Argument is not a directory.')

output_dir = Path(args.output)
output_dir.mkdir(parents=True,exist_ok=True)
recurse = (args.recursive == True)
existing = args.existing
threshold = int(args.threshold)
unique = args.unique

if recurse:
    mat_files = sorted(list(search_dir.glob('**/*.mat')))
else:
    mat_files = sorted(list(search_dir.glob('*.mat')))

designs = []

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

for f in mat_files:
    matfile = eng.matfile(str(f.resolve()))
    if eng.getfield(matfile,'result') == None:
        print(f'Saw {str(f)}\t\tNo result array.')
        continue
#    print(f'Saw {str(f)}\t\tand copying.')

    def fill(array, name, form):
        try:
            this_one = eng.getfield(matfile,name)
        except:
            this_one = None
        finally:
            designs.append(form(this_one) if this_one != None else None)

    new_design = {}
    new_design['t'] = int(eng.getfield(matfile,'t'))
    new_design['d'] = int(eng.getfield(matfile,'d'))
    new_design['n'] = int(eng.getfield(matfile,'n'))
    print(eng.getfield(matfile,'errors')[0][-1])
    new_design['error'] = float(eng.getfield(matfile,'errors')[0][-1])
    new_design['comment'] = str(eng.getfield(matfile,'comment'))
    relative_filename = output_dir/f.relative_to(search_dir)
    new_design['original_file'] = f
    new_design['filename'] = relative_filename.relative_to(output_dir)

    if new_design['error'] > (10**(-threshold)):
      continue

    is_admissible = True
    if unique == 1:
      for design in list(designs):
        if design['t'] == new_design['t'] and design['d'] == new_design['d'] and design['n'] == new_design['n']:
          is_admissible = False
          if design['error'] > new_design['error']:
            designs.remove(design)
            is_admissible = True

    if unique == 2:
      for design in list(designs):
        if design['t'] == new_design['t'] and design['d'] == new_design['d']:
          is_admissible = False
          if design['n'] == new_design['n'] and design['error'] > new_design['error']:
            designs.remove(design)
            is_admissible = True
          if design['n'] > new_design['n']:
            designs.remove(design)
            is_admissible = True

    if is_admissible:
      designs.append(new_design)

with (output_dir/'index.html').open(mode='w') as f:
    f.write(f'''<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>
        <title>Index of generated designs</title>
    </head>
    <body>
        <h1>Index of generated designs from directory {search_dir.resolve()}</h1>
        <h2>Key of colours</h2>
        <table border="1px" cellspacing="0" cellpadding="3">
            <tr>
                <td style="background-color: #ff8080">error &lt; 10^-12</td>
                <td style="background-color: #ffdd80">error &lt; 10^-9</td>
                <td style="background-color: #87c9ff">error &lt; 10^-4</td>
                <td style="background-color: #80ffc2">error &lt; 1</td>
                <td style="background-color: #ffffff">error ≥ 1</td>
            </tr>
        </table>
        <h2>List of designs</h2>
        <table border="1px" cellspacing="0" cellpadding="3">
            <tr>
                <th><i>d</i></th>
                <th><i>n</i></th>
                <th><i>t</i></th>
                <th>error (short)</th>
                <th>error (long)</th>
                <th>comment</th>
                <th>link to .mat file</th>
            </tr>\n''')
    for design in designs:
        (output_dir/design['filename']).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy(design['original_file'],output_dir/design['filename'])
        f.write(f'''            <tr style="background-color: {'#ff8080' if design['error'] < 1e-12 else '#ffdd80' if design['error'] < 1e-9 else '#87c9ff;' if design['error'] < 1e-4 else '#80ffc2' if design['error'] < 1 else '#fff'}">
                <td>{design['t']}</td>
                <td>{design['d']}</td>
                <td>{design['n']}</td>
                <td>{'%E'%design['error']}</td>
                <td>{design['error']}</td>
                <td>{design['comment']}</td>
                <td><a href="{design['filename']}">{design['filename']}</a></td>
            </tr>'''
        )
    f.write(f'''
        </table>
        <footer>This page was generated by {sys.argv[0]} at: {datetime.today().ctime()}</footer>
    </body>
</html>''')
