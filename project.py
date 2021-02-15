import matlab.engine
from pathlib import Path
import argparse
import sys
import shutil
from random import random
import colorsys


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

parser = argparse.ArgumentParser(description='Format a given spherical design in TiKZ format.', epilog='Smart colours are no longer available.')
parser.add_argument('filename', metavar='MATFILE', help='.mat file to read from')
parser.add_argument('-o','--output', default=None, help='output file (default is stdout)')
parser.add_argument('-e','--existing', action='count', default=0, help='connect to a running MATLAB session; specify twice to skip MATLAB verification prompt')
parser.add_argument('-a','--multi-axis', action='store_true', default=False, help='draw a separate axis per dimension')
parser.add_argument('-d','--domestic-lines', action = 'store_true', default=False, help='draw a cycle around the coordinates of a single direction')
parser.add_argument('-i','--international-lines', action = 'store_true', default=False, help='draw coloured lines between the coordinates of a single point')
parser.add_argument('-r','--rays', action = 'store_true', default=False, help='draw rays for each coordinate')
parser.add_argument('-s','--scale', type=int, default=4, help='scaling factor for graph')
parser.add_argument('-f','--fast-colours', action = 'store_true', default=False, help='use fast colours, not smart colours')


args = parser.parse_args()
filename = Path(args.filename)
output_filename = args.output

if not filename.exists():
    sys.exit('Input file does not exist.')

existing = args.existing
multi_axis = args.multi_axis
domestic_lines = args.domestic_lines
international_lines = args.international_lines
rays = args.rays

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


d = int(eng.size(result, 1))
n = int(eng.size(result, 2))
reals = eng.real(result)
imags = eng.imag(result)

# Pick n colours.
colours = []
for i in range(0,n):
    colours.append(colorsys.hls_to_rgb(i/n, 0.5 + random()/100, 0.9 + random()/100) )

#
# Below this point are the functions called in the below loop to actually generate LaTeX code.
#

width = args.scale

def offset(j):
    return j*2.5*width

def preamble():
    return '''\\documentclass{standalone}
\\usepackage{tikz}
\\begin{document}
    \\begin{tikzpicture}
'''

def peroration():
    return '   \\end{tikzpicture}\n\\end{document}\n'

# Helper function to produce code for a new axis at the right offset in TiKZ.
def new_axis(j):
    return f'''
        \\draw[->,ultra thick, lightgray] ({-width+offset(j)},0)--({width+offset(j)},0) node[right]{{$x_{j+1}$}};
        \\draw[->,ultra thick, lightgray] ({offset(j)},{-width})--({offset(j)},{width}) node[above]{{$y_{j+1}$}};
'''
    return axis_string

# Draw a point (x,y) on axis j.
def draw_point_on_axis(j,x,y,colour):
    return f'''
        \\node at ({x*width + offset(j):.3},{y*width:.3})[circle,fill={colour},inner sep=1.2pt]{{}};
'''

# Draw an arrow from (x_from,y_from) to (x_to,y_to) on axis j.
def draw_arrow_on_axis(j_from, x_from, y_from, j_to, x_to, y_to, colour, thickness):
    return f'''
        \\draw[->, {thickness}, color={colour}] ({x_from*width + offset(j_from):.3},{y_from*width:.3}) -- ({x_to*width + offset(j_to):.3}, {y_to*width:.3});
'''

def rgb_to_colour_string(colour):
    return f'{{rgb:red,{colour[0]/3.0:.3};green,{colour[1]/3.0:.3};blue,{colour[2]/3.0:.3}}}'

#
# Now the loop that actually produces the output.
#

with smart_open(output_filename) as f:
    f.write(preamble())

    # i counts the rows of the result matrix - i.e. increasing i moves down a vector through different dimensions.
    for i in range(0,d):
        if multi_axis:
            axis = i
            prev_axis = i-1
            f.write(new_axis(i))
        else:
            if i == 0:
                f.write(new_axis(i))
            axis = 0
            prev_axis = 0

        # j counts the columns of the matrix - i.e. increasing j moves to a different vector.
        for j in range(0,n):
            f.write(draw_point_on_axis(axis, reals[i][j], imags[i][j], rgb_to_colour_string(colours[j])))

            # draw rays if needed
            if rays:
                f.write(draw_arrow_on_axis(axis, 0.0, 0.0, axis, reals[i][j], imags[i][j], 'lightgray', 'thin'))

            # If we are on the second row or higher, draw a COLOURED line from THIS vector from the previous dimension.
            if international_lines and i > 0:
                f.write(draw_arrow_on_axis(prev_axis, reals[i-1][j], imags[i-1][j], axis, reals[i][j], imags[i][j], rgb_to_colour_string(colours[j]), 'very thick'))

            # If we are on the second column or higher, draw a BLACK line from the previous vector in THIS dimension.
            if domestic_lines:
                if j > 0:
                    f.write(draw_arrow_on_axis(axis, reals[i][j-1], imags[i][j-1], axis, reals[i][j], imags[i][j], 'black', 'thin'))
                else:
                    # We complete the cycle by drawing an arrow from the n-1th point to the 0th point
                    f.write(draw_arrow_on_axis(axis, reals[i][n-1], imags[i][n-1], axis, reals[i][0], imags[i][0], 'black', 'thin'))

    f.write(peroration())



