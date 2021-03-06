classdef RealDesignPotential < DesignPotential
    properties (Access = private)
        coefficient_
        d_
        n_
        t_
    end
    methods
        function this = RealDesignPotential(d,n,t)
            this = this@DesignPotential();
            this.d_ = d;
            this.n_ = n;
            this.t_ = t;
            this.coefficient_ = prod(d:2:(d+2*(t-1)))/prod(1:2:(2*t-1));
        end
        
        function epsilon = computeError(this,S)
            n = this.n_;
            t = this.t_;
            coefficient = this.coefficient_;
            gram = S'*S;
            epsilon = abs(coefficient*sum(abs(gram).^(2*t),'all') - n^2);
        end
        
        function grad = computeGradient(this,S)
            d = this.d_;
            t = this.t_;
            n = this.n_;
            coefficient = this.coefficient_;
            gram = S'*S;
            grad = zeros(d,n);
            for row = 1:d
                for col = 1:n
                    sum1 = abs(gram(col,:)).^(2*t - 2) .* transpose(gram(:,col)) .* S(row, :);
                    grad(row,col) = 4*coefficient*t*sum(sum1) - 4*t*n.*S(row,col);
                end
            end
        end
        
        function [d,n,t] = getParameters(this)
            d = this.d_; n = this.n_; t = this.t_;
        end
    end
end