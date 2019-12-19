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
            epsilon = abs(this.coefficient_*sum(abs(S).^(2*this.t_),'all') - (sum(diag(S).^this.t_))^2);
        end
        
        function grad = computeGradient(this,S)
            grad = zeros(this.n_);
            for row = 1:this.n_
                for col = 1:this.n_
                    grad(row,col) = this.t_.*this.coefficient_.*abs(S(row,col)).^(2*(this.t_-1)).*conj(S(row,col));
                end
            end
        end
    end
end