% Iterate on the given d x n matrix A to produce a better design, using
% the Manopt software package.
%
% Parameters: A - Unused
%             k - maximum number of iterations to run for.
%             errorComputer - instance of DesignPotential to compute error
%                             and error gradient.
%
% Output:     result - A d x n matrix consisting of n column vectors in C^d
%                      which approximately minimises the error.
%             errors - A k' x 1 matrix consisting of the best error found at
%                      each iteration
%             kprime - k', the actual number of iterations performed
function [result,errors, kprime] = iterateOnDesignMO(~, k, errorComputer)
%    d = size(A,1);
%    n = size(A,2);
%    if any(isnan(A))
%        A = [];
%    end
    [d,n,~] = errorComputer.getParameters();
    A = [];
    
%    options.maxiter = k;
    options.miniter = k;
    options.verbosity = 0;
    warning('off', 'manopt:getHessian:approx')

    solver = errorComputer.getSolver();
    problem.M = solver(d,n);
    problem.cost = @(x) errorComputer.computeError(x);
    problem.egrad = @(x) errorComputer.computeGradient(x);
    problem.delta_bar = problem.M.typicaldist()/10;

    [A, ~, info, ~] = trustregions(problem,A,options);
    
    result = sqrt(n)*A./norm(A,'fro');
    errors = [info.cost];
    kprime = length(errors);
end
