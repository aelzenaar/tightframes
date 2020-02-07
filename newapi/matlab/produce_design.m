% Produce an optimal (d,n,t)-design, using Manopt.
%
% Parameters: dp - an instance of DesignParameters.
%             A - initial guess, or [] for automatic
%
% Output:     result - A d x n matrix consisting of n column vectors in C^d
%                      which approximately minimises the error.
%             errors - A k' x 1 matrix consisting of the best error found at
%                      each iteration
%             kprime - k', the actual number of iterations performed
function [result,errors, kprime] = produce_design(dp, A)
    options.maxiter = 1000;
    options.verbosity = 0;
    warning('off', 'manopt:getHessian:approx')

    problem.M = dp.getManoptManifold();
    problem.cost = @(x) dp.computeError(x);
    problem.egrad = @(x) dp.computeGradient(x);
    
    [A, ~, info, ~] = trustregions(problem,A,options);
    
    result = A;
    errors = [info.cost];
    kprime = length(errors);
end
