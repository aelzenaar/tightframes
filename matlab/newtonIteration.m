% Iterate on the given Gram matrix A using Newton's method to produce a better design.
%
% Parameters: d - dimension of space.
%             n - number of vectors in design.
%             t - parameter of (t,t)-design.
%             A - initial matrix for iteration.
%             k - number of iterations to run for.
%             ap - number of times to run alternating projection on each
%                  iteration.
%             errorComputer - instance of DesignPotential to compute error
%                             and error gradient.
%             fd - file descriptor for output messages.
%
% Output:     result - A d x n matrix consisting of n column vectors in C^d
%                      which approximately minimises the error.
%             errors - A k x 1 matrix consisting of the best error found at
%                      each iteration.
function [result,errors] = newtonIteration(d, A, k, ap, errorComputer, fd)
    errors = zeros(k,1);
    
    error = errorComputer.computeError(A);
    gfA = errorComputer.computeGradient(A);
    Q1 = error^2 * trace(gfA*gfA');
    Q2 = (real(trace(gfA*A')))/(error*trace(gfA*gfA'));
    Q3 = (real(trace(gfA*A')))^2/trace(gfA*gfA') - trace(A*A') + length(A)^2/d;

    for h = 1:k
        errors(h) = error; % Log the best error we have right now.
        theta = rand()*2*pi;
        lambda = ((Q1/Q3)*cos(theta) - Q2) + 1i*((Q1/Q3)*sin(theta));
        A_new = A - gfA.*lambda.*error;
        
        A_new = (A_new + A_new')./2; % Project the new matrix onto the space of Hermitian matrices.
        A_new = alternatingProjection(A_new,d,ap); % Try to fix the rank and so forth.
        error_new = errorComputer.computeError(A_new);

        if(error_new < error)
            fprintf(fd, '****  Better found, %d/%d (had err: %e, got err: %e)\n', h, k, error, error_new);
            error = error_new;
            A = A_new;
            gfA = errorComputer.computeGradient(A);
            Q1 = error^2 * trace(gfA*gfA');
            Q2 = (real(trace(gfA*A')))/(error*trace(gfA*gfA'));
            Q3 = (real(trace(gfA*A')))^2/trace(gfA*gfA') - trace(A*A') + length(A)^2/d;
        else
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
