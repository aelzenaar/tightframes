% Attempt to generate a good candidate Gram matrix for starting iteration.
%
% Parameters: d - dimension of space.
%             n - number of vectors in design.
%             t - parameter of (t,t)-design.
%             k - number of iterations to run for.
%             s - number of initial seed matrices to check.
%             errorComputer - instance of DesignPotential to use to compute
%                             the error of possible Gram matrices.
%             fd - file descriptor for output messages.
%
% Output:     result - A d x n matrix consisting of n column vectors in C^d
%                      which approximately minimises the error.
%             errors - A k x 1 matrix consisting of the best error found at
%                      each iteration.
%             totalBadness - the total number of times that the algorithm
%                            failed to improve the estimate by walking
%                            down the gradient.
function A = getRandomComplexSeed(d,n,t,s,errorComputer,fd)
    A = zeros(n,n); % The "best" Gram matrix found so far.
    error = inf; % The error associated with A
    
    % Check lots of random matrices to find a good starting point.
    for h = 1:s
        % Produce a random n^2 Hermitian matrix B.
        B = (randn(d,n) + 1i*randn(d,n)); % get a random set of n d-vectors
        B = B./vecnorm(B); % normalise all the vectors, column by column
        B = B'*B; % make the matrix Hermitian by replacing it with its Gramian
        
        error_try = errorComputer.computeError(B);
        if(error_try < error)
            error = error_try;
            A = B;
            fprintf(fd, 'Seeding, %d/%d (best found err: %f, new best)\n', h, s, error);
        else
        end
        drawnow('update');
    end
    fprintf(fd, 'Found best seed with error %f.\n\n', error);
end
