classdef ComplexDesignPotential < DesignPotential
    properties (Access = private)
        coefficient_
        d_
        n_
        t_
    end
    methods
        function this = ComplexDesignPotential(d,n,t)
            this = this@DesignPotential();
            this.d_ = d;
            this.n_ = n;
            this.t_ = t;
            this.coefficient_ = nchoosek(d+t-1,t);
        end
        
        function epsilon = computeError(this,S)
            t = this.t_;
            coefficient = this.coefficient_;
            gram = S'*S;
            epsilon = abs(coefficient*sum(abs(gram).^(2*t),'all') - (sum(diag(gram).^t))^2);
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
                    grad(row,col) = 4*coefficient*t*sum(sum1) - 4*t*sum(diag(gram).^(t)).*gram(col,col).^(t-1).*S(row,col);
                end
            end
        end
    end
end