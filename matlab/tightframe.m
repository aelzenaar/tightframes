% Attempt to generate a spherical (t,t)-design.
%
% Parameters: d - dimension of space.
%             n - number of vectors in design.
%             t - parameter of (t,t)-design.
%             k - number of iterations to run for.
%             s - number of initial seed matrices to check. (This is cheap.)
%             b - the algorithm attempts to walk down the line of the gradient
%                 this many times before falling back to looking at a ball.
%             ap - number of times to run alternating projection on each
%                  iteration. Tropp says (p.138) that ap > 500 produces
%                  negligible return.
%             errorMultiplier - scale the walk length by this amount.
%             fd - file descriptor for output messages.
%
% Output:     result - A d x n matrix consisting of n column vectors in C^d
%                      which approximately minimises the error.
%             errors - A k x 1 matrix consisting of the best error found at
%                      each iteration.
%             totalBadness - the total number of times that the algorithm
%                            failed to improve the estimate by walking
%                            down the gradient.
function [result, errors, totalBadness] = ...
  tightframe(d, n, t, k, s, b, ap, errorMultiplier, fd)
    errorComputer = ComplexDesignPotential(d,n,t);

    A = getRandomComplexSeed(d,n,t,s,errorComputer,fd);
    [result, errors, totalBadness] = iterateOnDesign(d,n,t,A,k,b,ap,errorMultiplier,errorComputer,fd);
end
