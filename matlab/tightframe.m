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
%                  iteration.
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
    coefficient = nchoosek(d+t-1,t); % Pre-calculate c_t since it is constant throughout.

    A = zeros(n,n); % The "best" Gram matrix found so far.
    error = inf; % The error associated with A
    
    % Check lots of random matrices to find a good starting point.
    for h = 1:s
        A_try = randomUnitHermitian(d,n);
        error_try = computeError(t,A_try,coefficient);
        if(error_try < error)
            error = error_try;
            A = A_try;
            fprintf(fd, 'Seeding, %d/%d (best found err: %f, new best)\n', h, s, error);
        else
            fprintf(fd, 'Seeding, %d/%d (best found err: %f so far)\n', h, s, error);
        end
        drawnow('update');
    end
    fprintf(fd, 'Found best seed with error %f.\n\n', error);
    
    
    errors = zeros(k,1);
    badCount = 0; % Iterations since we last improved things by walking down the gradient.
    totalBadness = 0; % Total number of times walking down the gradient didn't work - if this is large, we decrease our step size accordingly.

    for h = 1:k
        errors(h) = error; % Log the best error we have right now.
        if(badCount < b)
            delta = random('Lognormal',log(error.*errorMultiplier./(totalBadness + 1)),1);
            A_new = A - delta.*potentialGradient(t,A,coefficient); % Pick a random matrix in the right direction.
        else
            fprintf(fd, 'Badness reached %d (total bad proportion %f), so randomly trying around.\n', badCount, totalBadness./h);
            A_new = A + randn(size(A)).*error.*errorMultiplier;
        end
        A_new = (A_new + A_new')./2; % Project the new matrix onto the space of Hermitian matrices.
        A_new = alternatingProjection(A_new,d,ap); % Try to fix the rank and so forth.
        error_new = computeError(t,A_new,coefficient);

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




function A = randomUnitHermitian(d,n)
	% Produce a random n^2 Hermitian matrix A.
	A = (randn(d,n) + 1i*randn(d,n)); % get a random set of n d-vectors
	A = A./vecnorm(A); % normalise all the vectors, column by column
	A = A'*A; % make the matrix Hermitian by replacing it with its Gramian
	assert(isequal(A,A'))
end

% This method implements a modified version of the "alternating projections"
% algorithm of Tropp (2004).
% 
% Parameters:  G - an Hermitian matrix (of size n x n).
%              d - the rank of the desired output matrix.
%              T - the maximum number of iterations to run for.
%
% Output:      An n x n matrix H with the following properties:
%                (1) H has a unit diagonal
%                (2) H is positive semi-definite
%                (3) rank H <= d
%                (4) tr H = n
function H = alternatingProjection(G, d, T)
	n = length(G);
	for t = 1:T
		% Project G onto the subspace of matrices with unit diagonal
		% which come from dot products of unit vectors.
		H = G .* (ones(n) - eye(n)) + eye(n); % Make unit diagonal
 		H = (H./abs(H)).*min(ones(n),abs(H)); % Truncate entries to length <= 1
 		H(isnan(H)) = 0;
 		H(isinf(H)) = 0;
                
		% Project H onto the space of matrices with properties (2) to (4) above.
  
		[U,L] = eig(H);
		%   Sort the eigenvalues and vectors in descending order.
		D = diag(L);
		[~, perm] = sort(D,'descend');
		D = D(perm);
		U = U(:,perm);
		%   Zero out all the eigenvalues after the d-th one.
		zeroer = zeros(n,1);
		zeroer(1:d,1) = ones(d,1);
		D = D.*zeroer;
		D(abs(D)<1e-6)=0;
		%   Fix rank if needed.
		eigCount = nnz(D);
		if d - eigCount > 0
			for iter = (eigCount+1):(d)
				D(iter) = D(eigCount)*iter/(d - eigCount + 1);
			end
		end
		%   Pick the right value of gamma (see cited algorithm for notation). The
		%   first (commented out) line will use a slow golden-ratio search; the
		%   method actually implemented is more difficult to read but essentially
		%   uses the fact that the function fn is piecewise linear with
		%   the corners (the non-linear points) at x \in {lambda_i | 1<=i<=d} U {0}
		%   to find the linear part containing the x-intercept of fn, and then
		%   solves the resulting linear equation to compute gamma. It is faster
		%   but not as well-tested as the golden-ratio search.
% 		gamma = fibsearch(@(x) abs(sum(max(D - x, 0)) - n), -D(1), D(1), 50);
		optSamples = [D(1)+1;D(1:d,1);0;-1];
		optValues = zeros(size(optSamples));
		for iter = 1:(d+3)
			optValues(iter) = sum(max(D - optSamples(iter), 0)) - n;
		end
		gamma = inf;
		len = length(optValues);
		for iter = 0:(len-2)
			if optValues(len - iter) == 0
				gamma = optSamples(len - iter);
				break;
			elseif optValues(len - iter) < 0
				R = [optSamples(len - iter + 1), optValues(len - iter + 1), -1;
				     optSamples(len - iter),     optValues(len - iter),     -1  ];
				N = null(R);
				gamma = N(3)/N(1);
				break;
			end
		end
		%   Recompose to form the new matrix G.
		G = zeros(n);
		for iter = 1:d
			G = G + max(D(iter) - gamma, 0).*U(:,iter)*U(:,iter)';
		end
	end

	H = G;
end 

% Compute the gradient of the (square) matrix S with respect to the frame potential;
% the formula is given on page 140 of Waldron (2018).
function grad = potentialGradient(t,S,coefficient)
    dim = length(S);
    grad = zeros(dim);
    for row = 1:dim
        for col = 1:dim
            grad(row,col) = t.*coefficient.*abs(S(row,col)).^(2*(t-1)).*conj(S(row,col));
        end
    end
end

function epsilon = computeError(t,S,coefficient)
    assert(size(S,1) == size(S,2));
	epsilon = abs(coefficient*sum(abs(S).^(2*t),'all') - (sum(diag(S).^t))^2);
	assert(epsilon >= 0)
end
