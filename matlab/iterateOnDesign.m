% Iterate on the given Gram matrix A to produce a better design.
%
% Parameters: d - dimension of space.
%             n - number of vectors in design.
%             t - parameter of (t,t)-design.
%             A - initial matrix for iteration.
%             k - number of iterations to run for.
%             b - the algorithm attempts to walk down the line of the gradient
%                 this many times before falling back to looking at a ball.
%             ap - number of times to run alternating projection on each
%                  iteration. Tropp says (p.138) that ap > 500 produces
%                  negligible return.
%             errorMultiplier - scale the walk length by this amount.
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
function [result,errors,totalBadness] = iterateOnDesign(d, A, k, b, ap, errorMultiplier, errorComputer, fd)
    error = errorComputer.computeError(A);
    errors = zeros(k,1);
    badCount = 0; % Iterations since we last improved things by walking down the gradient.
    totalBadness = 0; % Total number of times walking down the gradient didn't work - if this is large, we decrease our step size accordingly.

    for h = 1:k
        errors(h) = error; % Log the best error we have right now.
        if(badCount < b)
            delta = random('Lognormal',log(error.*errorMultiplier./(totalBadness + 1)),1);
            A_new = A - delta.*errorComputer.computeGradient(A); % Pick a random matrix in the right direction.
        else
            fprintf(fd, 'Badness reached %d (total bad proportion %f), so randomly trying around.\n', badCount, totalBadness./h);
            A_new = A + randn(size(A)).*error.*errorMultiplier;
        end
        
        A_new = (A_new + A_new')./2; % Project the new matrix onto the space of Hermitian matrices.
        A_new = alternatingProjection(A_new,d,ap); % Try to fix the rank and so forth.
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

    % We may reproduce the frame from the Gramian matrix A; the columns of A
    % give a "copy" of the frame in C^n, and we therefore diagonalise to get
    % these vectors to be embedded in a more natural d-dimensional subspace
    % of C^n so we can look at them.
    [U,D] = eig(A);
    result = (U*sqrt(D))';
    result(abs(result)<1e-6)=0;
    result = result(any(result,2),:); % Remove zero lines.
end
