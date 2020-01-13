design-finder
=============

A collection of utilities to generate spherical (_t_,_t_)-designs (henceforth, _t_-designs) in **C**^d with given parameters.

This software was written by me under the supervision of [Shayne Waldron](https://www.math.auckland.ac.nz/~waldron/).

Requirements
------------

  * MATLAB (at least R2018b) with the Statistics toolbox

For the Python utilities, you also need:
  * Python 3._x_, where _x_ is a version [supported](https://au.mathworks.com/help/matlab/matlab_external/system-requirements-for-matlab-engine-for-python.html) by
    the [MATLAB API for Python](https://au.mathworks.com/help/matlab/matlab-engine-for-python.html)  (for Python utility only).
  * The MATLAB API for Python itself ([installation instructions](https://au.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html)). This comes with MATLAB,
    it just needs to be manually enabled.

Scripts included
----------------

### MATLAB scripts and functions
The following MATLAB scripts may be used by modifying the parameters at the top of each file.

  * `runtf.m`, which tries to generate a _t_-design with given fixed parameters.
  * `search_designs.m`, which tries to find a _t_-design for *lots* of _n_, given
    a fixed _d_ and _t_.
  * `exp12.m`, which takes an existing design generated by `runtf` and makes it better.

For the more technical user, here are the functions and objects that you can call and use from your own scripts. The three scripts
listed above should be decent examples of the usage of these utilities.

  * `DesignPotential` is an object representing an error function and the gradient of that function, for use in computations.
    One example is `ComplexDesignPotential` (which deals with the complex case).
  * `getRandomComplexSeed` generates a good starting matrix for iteration.
  * `iterateOnDesign` takes a starting matrix and a `DesignPotential` instance and tries to iterate it to compute
    a better design.
  * `compute3Products` takes a design and returns the list of its 3-products in ascending order.


Remarks.

  * Designs are always stored as _d_ by _n_ matrices.
  * `runtf.m` and `exp12.m` will both produce a file in the current directory, named like `tf_run_YYYY_MM_DD_hh_mm_ss.mat`, containing all the data used
    to generate the design, as well as the design itself, and a list of the error of the design produced at each iteration. `search_designs.m` will produce
    a whole *directory* (in the current directory), named like `search_designs_D_T_YYYY_MM_DD_hh_mm_ss/`, which contains `.mat` files like those generated
    by `runtf.m` (named according to _n_) and plots of the associated errors.
  * `runtf.m` takes an `errorMultiplier` parameter (the step size at each iteration is then `errorMultiplier * (error)^errorExp`); this needs to be chosen
    by the user for a given _d_,_n_,_t_ triple and can be fiddly to do. An example of an automated method, which seems to work reasonably well, may be found
    in `search_designs.m` (in particular, the for loop on `r_try`).

### Python scripts
The Python scripts accept a `--help` argument. Here is a list of the scripts.

  * `generate_runtf.py`, which takes a directory of output files from the MATLAB scripts and produces a standalone directory containing an HTML index file to all of them.
  * `generate_from_search.py`, which takes a *single* output directory from `search_designs.m` and produces a nice HTML rendering (for certain values of 'nice').
  * `fmagma.py`, which takes a single `.mat` file and produces a `.magma` file containing the same design.

References
----------
The canonical reference for the mathematics is the following book:

**Waldron, Shayne F. D.** An introduction to finite tight frames. Applied and Numerical Harmonic Analysis. _Birkhäuser/Springer, New York_, 2018. xx+587 pp. ISBN: 978-0-8176-4814-5; 978-0-8176-4815-2 [MR3752185](http://www.ams.org/mathscinet-getitem?mr=3752185)

See in particular chapter 6.
