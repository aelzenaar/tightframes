import matlab.engine
from pathlib import Path
import argparse
import sys
import shutil
from datetime import datetime

parser = argparse.ArgumentParser(description='Generate a database of designs from a given directory, output by search_designs.m.')
parser.add_argument('directory', metavar='DIR', help='directory to scan')
parser.add_argument('-e','--existing', action='count', default=0, help='connect to a running MATLAB session; specify twice to skip MATLAB verification prompt')
parser.add_argument('-o','--output', default='html', help='output directory')

args = parser.parse_args()
search_dir = Path(args.directory)
if not search_dir.is_dir():
    sys.exit('Argument is not a directory.')

parsed_search_dir = str(search_dir).split('_')

if not (parsed_search_dir[0] == 'search' and parsed_search_dir[1] == 'designs'):
    sys.exit('Given directory does not seem to be output from search_designs.\nFormat of dir name should be search_designs_D_T_DATESTR, where D, T are design\nparameters and DATESTR is a timestamp.')

d = parsed_search_dir[2]
t = parsed_search_dir[3]
timestamp = parsed_search_dir[4]


output_dir = Path(args.output)
existing = args.existing
mat_files = sorted(list(search_dir.glob('*.mat')))

n = []
k = []
totalBadness = []
errorMultiplier = []
error = []
error_short = []
error_img = []
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

    fill(n,'n',int)
    fill(k,'k',int)
    fill(errorMultiplier,'errorMultiplier',lambda val: '%E'%(val) )
    fill(totalBadness,'totalBadness',int)
    fill(error,'errors',lambda val: val[-1][0])
    fill(error_short,'errors',lambda val: '%E'%(val[-1][0]) )


    relative_filename = output_dir/f.relative_to(search_dir)
    filenames.append(str(relative_filename.relative_to(output_dir)))

    relative_filename.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy(f,relative_filename)

    this_image = f.parent / Path(str(f.stem) + '_errors.png');
    if this_image.exists():
        relative_image = output_dir/this_image.relative_to(search_dir)
        error_img.append(str(relative_image.relative_to(output_dir)))

        relative_image.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy(this_image,relative_image)
    else:
        error_image.append(None)

with (output_dir/'index.html').open(mode='w') as f:
    f.write(f'''<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>
        <title>Index of generated designs -- (d,t) = ({d},{t}) </title>
    </head>
    <body>
        <h1>Index of generated designs -- (d,t) = ({d},{t}) </h1>
        <p><i>Generation time for the designs: {timestamp}
        <table border="1px" cellspacing="0" cellpadding="3">
            <tr><th><i>n</i></th><th>errorMultiplier</th><th>error (short)</th><th>error (long)</th><th>badness proportion</th><th>error plot</th><th>Link</th></tr>\n''')
    for i in range(0,len(filenames)):
        if error_img[i] == None:
            img_tag = '(no image)'
        else:
            img_tag = f'<img src="{error_img[i]}" width="500px" alt="Error plot for this run."/>'
        if totalBadness[i] == None or k[i] == None:
            bad_tag = '(no badness)'
        else:
            bad_tag = f'{totalBadness[i]}/{k[i]} = {totalBadness[i]/k[i]}'
        f.write(f'''            <tr>
                                    <td>{n[i]}</td>
                                    <td>{errorMultiplier[i]}</td>
                                    <td>{error_short[i]}</td>
                                    <td>{error[i]}</td>
                                    <td>{bad_tag}</td>\
                                    <td>{img_tag}</td>
                                    <td><a href="{filenames[i]}">{filenames[i]}</a></td>
                                </tr>\n'''
        )
    f.write(f'''
        </table>
        <footer>Page generated: {datetime.today().ctime()}</footer>
    </body>
</html>''')
