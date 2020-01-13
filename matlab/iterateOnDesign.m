% Iterate on the given Gram matrix A to produce a better design.
%
% Parameters: A - initial matrix for iteration.
%             k - number of iterations to run for.
%             b - the algorithm attempts to walk down the line of the gradient
%                 this many times before falling back to looking at a ball.
%             errorMultiplier, errorExp - walk distance is given by
%                 errorMultiplier*(error)^errorExp.
%             errorComputer - instance of DesignPotential to compute error
%                             and error gradient.
%             fd - file descriptor for output messages.
%
% Output:     result - A d x n matrix consisting of n column vectors in C^d
%                      which approximately minimises the error.
%             errors - A k x 1 matrix consisting of the best error found at
%                      each iteration.
%             totalBadness - the total number of times that the algorithm
%                            failed to improve the estimate by walking
%                            down the gradient.
function [result,errors,totalBadness] = iterateOnDesign(A, k, b, errorMultiplier,errorExp, errorComputer, fd)
    error = errorComputer.computeError(A);
    errors = zeros(k,1);
    badCount = 0; % Iterations since we last improved things by walking down the gradient.
    totalBadness = 0; % Total number of times walking down the gradient didn't work - if this is large, we decrease our step size accordingly.

    for h = 1:k
        errors(h) = error; % Log the best error we have right now.
        meanWalk = errorMultiplier .* error.^errorExp;
        if(badCount < b)
            delta = exp(randn() + log(meanWalk));
            A_new = A - delta.*errorComputer.computeGradient(A); % Pick a random matrix in the right direction.
        else
            fprintf(fd, 'Badness reached %d (total bad proportion %f), so randomly trying around.\n', badCount, totalBadness./h);
            A_new = A + randn(size(A)) .* meanWalk;
        end
        
        
        A_new = A_new./vecnorm(A_new); % normalise all the vectors, column by column
        error_new = errorComputer.computeError(A_new);

        if(error_new < error)
            fprintf(fd, '****  Better found, %d/%d (had err: %e, got err: %e)\n', h, k, error, error_new);
            error = error_new;
            A = A_new;
            badCount = 0;
        else
            badCount = badCount + 1;
            totalBadness = totalBadness + 1;
            fprintf(fd, 'Nothing better, %d/%d (had err: %e, got err: %e)\n', h, k, error, error_new);
        end
    end
    
    result = A;
    result(abs(result)<1e-6)=0;
end
