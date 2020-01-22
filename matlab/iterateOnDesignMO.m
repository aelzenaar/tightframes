% Iterate on the given d x n matrix A to produce a better design, using
% the Manopt software package.
%
% Parameters: A - initial matrix for iteration, or NaN(d,n) for automatic.
%             k - maximum number of iterations to run for.
%             errorComputer - instance of DesignPotential to compute error
%                             and error gradient.
%
% Output:     result - A d x n matrix consisting of n column vectors in C^d
%                      which approximately minimises the error.
%             errors - A k' x 1 matrix consisting of the best error found at
%                      each iteration
%             kprime - k', the actual number of iterations performed
function [result,errors, kprime] = iterateOnDesignMO(A, k, errorComputer)
    d = size(A,1);
    n = size(A,2);
    if any(isnan(A))
        A = [];
    end
    
    options.maxiter = k;
    options.verbosity = 0;
    warning('off', 'manopt:getHessian:approx')

    problem.M = obliquecomplexfactory(d,n);
    problem.cost = @(x) errorComputer.computeError(x);
    problem.egrad = @(x) errorComputer.computeGradient(x);
    
    [A, ~, info, ~] = trustregions(problem,A,options);
    
    result = A;
    errors = [info.cost];
    kprime = length(errors);
end
