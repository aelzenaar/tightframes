classdef RealDesignPotential < DesignPotential
    properties (Access = private)
        coefficient_
        d_
        n_
        t_
        solver_
    end
    methods
        function this = RealDesignPotential(d,n,t,type)
            this = this@DesignPotential();
            this.d_ = d;
            this.n_ = n;
            this.t_ = t;
            this.coefficient_ = prod(d:2:(d+2*(t-1)))/prod(1:2:(2*t-1));
            if strcmp(type, 'weighted')
                this.solver_ = @euclideanfactory;
            elseif strcmp(type, 'equal_norm')
                this.solver_ = @obliquefactory;
            else
                error('unknown design type');
            end
        end
        
        function solver = getSolver(this)
            solver = this.solver_;
        end
        
        function epsilon = computeError(this,S)
            t = this.t_;
            coefficient = this.coefficient_;
            gram = S'*S;
            epsilon = abs(coefficient*sum(abs(gram).^(2*t),'all') - (sum(abs(diag(gram)).^t))^2) + (gram(1,1) - 1)^2;
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
                    grad(row,col) = 4*coefficient*t*sum(sum1) - 4*t*sum(abs(diag(gram)).^t).*gram(col,col)^(t-1).*S(row,col);
                end
            end
            grad(:,1) = grad(:,1) + 4*(gram(1,1) - 1)^2.*S(:,1);
        end
        
        function [d,n,t] = getParameters(this)
            d = this.d_; n = this.n_; t = this.t_;
        end
    end
end
