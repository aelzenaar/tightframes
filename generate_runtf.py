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
parser.add_argument('-o','--output', default='html', help='output directory')

args = parser.parse_args()
search_dir = Path(args.directory)
if not search_dir.is_dir():
    sys.exit('Argument is not a directory.')

output_dir = Path(args.output)
recurse = (args.recursive == True)
existing = args.existing

if recurse:
    mat_files = sorted(list(search_dir.glob('**/*.mat')))
else:
    mat_files = sorted(list(search_dir.glob('*.mat')))

d = []
n = []
t = []
k = []
totalBadness = []
errorMultiplier = []
errorExp = []
error = []
error_short = []
comment = []
filenames = []

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
    print(f'Saw {str(f)}\t\tand copying.')

    def fill(array, name, form):
        try:
            this_one = eng.getfield(matfile,name)
        except:
            this_one = None
        finally:
            array.append(form(this_one) if this_one != None else None)

    fill(d,'d',int)
    fill(n,'n',int)
    fill(t,'t',int)
    fill(k,'k',int)
    fill(errorMultiplier,'errorMultiplier',lambda val: '%E'%(val) )
    fill(errorExp,'errorExp',float)
    fill(totalBadness,'totalBadness',int)
    fill(error,'errors',lambda val: val[-1][0])
    fill(error_short,'errors',lambda val: '%E'%(val[-1][0]) )
    fill(comment,'comment',str)

    relative_filename = output_dir/f.relative_to(search_dir)
    filenames.append(str(relative_filename.relative_to(output_dir)))

    relative_filename.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy(f,relative_filename)

with (output_dir/'index.html').open(mode='w') as f:
    f.write('''<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>
        <title>Index of generated designs</title>
    </head>
    <body>
        <h1>Index of generated designs</h1>
        <table border="1px" cellspacing="0" cellpadding="3">
            <tr><th><i>d</i></th><th><i>n</i></th><th><i>t</i></th><th>iterations (<i>k</i>)</th><th>errorMultiplier</th><th>errorExp</th><th>error (short)</th><th>error (long)</th><th>badness proportion</th><th>Comment</th><th>Link</th></tr>\n''')
    for i in range(0,len(filenames)):
        f.write(f'            <tr><td>{d[i]}</td>\
                              <td>{n[i]}</td>\
                              <td>{t[i]}</td>\
                              <td>{k[i]}</td>\
                              <td>{errorMultiplier[i]}</td>\
                              <td>{errorExp[i]}</td>\
                              <td>{error_short[i]}</td>\
                              <td>{error[i]}</td>\
                              <td>{totalBadness[i]}/{k[i]} = {totalBadness[i]/k[i]} </td>\
                              <td>{comment[i]}</td>\
                              <td><a href="{filenames[i]}">{filenames[i]}</a></td></tr>\n'
        )
    f.write(f'''
        </table>
        <footer>Generated: {datetime.today().ctime()}</footer>
    </body>
</html>''')
