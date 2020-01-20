import matlab.engine
from pathlib import Path
import argparse
import sys
import shutil
from random import random
import colorsys
from collections import namedtuple

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

parser = argparse.ArgumentParser(description='Format a given spherical design in TiKZ format.')
parser.add_argument('filename', metavar='MATFILE', help='.mat file to read from')
parser.add_argument('-o','--output', default=None, help='output file (default is stdout)')
parser.add_argument('-e','--existing', action='count', default=0, help='connect to a running MATLAB session; specify twice to skip MATLAB verification prompt')
parser.add_argument('-s','--scale', type=int, default=4, help='scaling factor for graph')


args = parser.parse_args()
filename = Path(args.filename)
output_filename = args.output

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


d = int(eng.size(result, 1))
n = int(eng.size(result, 2))
print(d,n)
reals = eng.real(result)
imags = eng.imag(result)
scale = args.scale

# Pick n colours.
colours = []
for i in range(0,n):
    colours.append(colorsys.hls_to_rgb(i/n, 0.5 + random()/100, 0.9 + random()/100) )



#
# Below this point are the functions called in the below loop to actually generate LaTeX code.
#

Point3D = namedtuple('Point3D', ['x','y','z'])
def vecsum(P,Q):
  return Point3D(P.x + Q.x, P.y + Q.y, P.z + Q.z)

def scamul(mu, P):
  return Point3D(mu*P.x, mu*P.y, mu*P.z)

projectionPoint = Point3D(-2,-6,d+2)
projectionPlaneY = 2


def preamble():
    return '''\\documentclass{standalone}
\\usepackage{tikz}
\\begin{document}
    \\begin{tikzpicture}
'''

def peroration():
    return '   \\end{tikzpicture}\n\\end{document}\n'

# Take a Point3D and return the projection from projectionPoint onto Y = projectionPlaneY.
def project_point(P):
  l = (projectionPlaneY - projectionPoint.y)/(P.y - projectionPoint.y)
  return scamul(scale, vecsum( scamul(l, vecsum( P, scamul(-1, projectionPoint) ) ), projectionPoint)) # scale*[l*(P-projectionPoint) + projectionPoint]

# Helper function to produce code for a new axis at the right offset in TiKZ.
def axes_arrows(num, coordList):
    return f'''
        \\draw[->,thin, lightgray] ({coordList[0].x:.4},{coordList[0].z:.4})--({coordList[1].x:.4},{coordList[1].z:.4}) node[above]{{$y_{num}$}};
        \\draw[->,thin, lightgray] ({coordList[2].x:.4},{coordList[2].z:.4})--({coordList[3].x:.4},{coordList[3].z:.4}) node[right]{{$x_{num}$}};
'''

def axes_solid(coordList):
    # Compute the centre of the axes
    x1,x2,x3,x4 = coordList[0].x,coordList[1].x,coordList[2].x,coordList[3].x
    z1,z2,z3,z4 = coordList[0].z,coordList[1].z,coordList[2].z,coordList[3].z
    l = ((z1 - z3)*(x4 - x3) + (x3 - x1)*(z4 - z3))/( (x2 - x1)*(z2 - z3) - (z2 - z1)*(x4 - x3) )
    centre = vecsum(scamul(l, vecsum(coordList[1], scamul(-1, coordList[0]))), coordList[0])

    # Now compute corners, clockwise from top left
    corners = [vecsum(coordList[1], coordList[2]),
               vecsum(coordList[1], coordList[3]),
               vecsum(coordList[0], coordList[3]),
               vecsum(coordList[0], coordList[2])]
    corners = [ vecsum(corner, scamul(-1, centre)) for corner in corners]

    return f'''
        \\draw[fill=lightgray, opacity=0.8] ({corners[0].x:.4},{corners[0].z:.4})--({corners[1].x:.4},{corners[1].z:.4})--({corners[2].x:.4},{corners[2].z:.4})--({corners[3].x:.4},{corners[3].z:.4})--cycle;
'''

# Draw a point P in a 2D plane with coordinates (x, z).
def coloured_point(P, colour):
    return f'''
        \\node at ({P.x:.4},{P.z:.4})[circle,fill={colour},inner sep=1.2pt]{{}};
'''

# Draw an arrow from P to Q in a 2D plane with coordinates (x, z).
def coloured_arrow(P, Q, colour, thickness):
    return f'''
        \\draw[->, {thickness}, color={colour}] ({P.x:.4},{P.z:.4}) -- ({Q.x:.4}, {Q.z:.4});
'''

def rgb_to_colour_string(colour):
    return f'{{rgb:red,{colour[0]/3.0:.4};green,{colour[1]/3.0:.4};blue,{colour[2]/3.0:.4}}}'

#
# Now the loop that actually produces the output.
#

with smart_open(output_filename) as f:
    f.write(preamble())

    # We need to remember to subtract 1 from i when we do array indexing.
    for i in range(0, d):
        # Coordinate axes extremities. i+1 is used rather than i because we want to label
        # everything from 1, not 0.
        axes = [Point3D(0, -1, i+1),
                Point3D(0, 1, i+1),
                Point3D(-1, 0, i+1),
                Point3D(1, 0, i+1)]
        projectedAxes = [project_point(axis) for axis in axes]

        f.write(axes_solid(projectedAxes))

        arrow_strings = ''
        for j in range(0, n):
            P = Point3D(reals[i][j], imags[i][j], i + 1)
            projectedP = project_point(P)
            f.write(coloured_point(projectedP, rgb_to_colour_string(colours[j])))

            if i < d - 1:
                Q = Point3D(reals[i+1][j], imags[i+1][j], i + 2)
                projectedQ = project_point(Q)
                arrow_strings = arrow_strings + coloured_arrow(projectedP, projectedQ, rgb_to_colour_string(colours[j]), 'very thick')

        f.write(axes_arrows(i+1, projectedAxes))
        f.write(arrow_strings) # Paint coloured arrows on top of axes


    f.write(peroration())



