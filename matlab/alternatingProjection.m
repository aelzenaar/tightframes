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
