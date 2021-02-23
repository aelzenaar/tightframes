classdef QuaternionicDesignPotential < DesignPotential
    properties (Access = private)
        coefficient_
        d_
        n_
        t_
        solver_
    end
    methods
        function this = QuaternionicDesignPotential(d,n,t,type)
            this = this@DesignPotential();
            this.d_ = d;
            this.n_ = n;
            this.t_ = t;
            real_dim = 4;
            ind = 0:(t-1);
            numerator = real_dim + 2.*ind;
            denominator = real_dim*d + 2.*ind;
            this.coefficient_ = (prod(numerator./denominator))^(-1);
            if strcmp(type, 'weighted')
                this.solver_ = @euclideancomplexfactory;
            elseif strcmp(type, 'equal_norm')
                this.solver_ = @obliquecomplexfactory;
            else
                error('unknown design type');
            end
        end
        
        function solver = getSolver(this)
            solver = this.solver_;
        end
        
        function epsilon = computeError(this,S)
            t = this.t_;
            d = this.d_;
            X = S(1:d,:);
            Y = S(d+1:2*d,:);
            coefficient = this.coefficient_;
            gramXX = X'*X;
            gramXY = X'*Y;
            gramYY = Y'*Y;
            epsilon = coefficient*abs(sum((abs(gramXX+conj(gramYY)).^2 + abs(gramXY-gramXY').^2).^t,'all')) - (sum((diag(gramXX) + diag(gramYY)).^t))^2;
            epsilon = abs(epsilon);
        end
        
        function grad = computeGradient(this,S)
            d = this.d_;
            n = this.n_;
            howBad = 1e-10;
            grad = zeros(size(S));
            currentError = this.computeError(S);
            for alpha = 1:2*d
                for beta = 1:n
                    pertubation = zeros(size(S));
                    pertubation(alpha,beta) = howBad;
                    grad(alpha,beta) = (1/howBad)*(this.computeError(S+pertubation) - currentError);
                end
            end
        end
        
%         function grad = computeGradient(this,S)
%             d = this.d_;
%             t = this.t_;
%             n = this.n_;
%             X = S(1:d,:);
%             Y = S(d+1:2*d,:);
%             coefficient = this.coefficient_;
%             gramXX = X'*X; gramXY = X'*Y; gramYY = Y'*Y;
%             gradX = zeros(d,n);
%             gradY = zeros(d,n);
%             for alpha = 1:d
%                 for beta = 1:n
%                     termsX = ones(1,n);
%                     termsY = ones(1,n);
%                     for ell = 1:n
%                         leading = abs((abs(gramXX(ell,beta) + conj(gramYY(ell,beta)))^2 + abs(gramXY(ell,beta) - conj(gramXY(ell,beta)))^2 )^(t-1));
%                         termsX(ell) = leading * (X(alpha,ell)*(conj(gramXX(ell,beta))+gramYY(ell,beta)) + Y(alpha,ell)*(conj(gramXY(ell,beta) - gramXY(ell,beta))));
%                         termsY(ell) = leading * (Y(alpha,ell)*(conj(gramXX(ell,beta))+gramYY(ell,beta)) - X(alpha,ell)*(conj(gramXY(ell,beta) - gramXY(ell,beta))));
%                     end
%                     constant = 4*t*sum((diag(gramXX) + diag(gramYY)).^t)*(gramXX(beta,beta)+gramYY(beta,beta))^(t-1);
%                     gradX(alpha,beta) = 4*t*coefficient*sum(termsX) - constant*X(alpha,beta);
%                     gradY(alpha,beta) = 4*t*coefficient*sum(termsY) - constant*Y(alpha,beta);
%                 end
%             end
%             grad = [gradX;gradY];
%             assert(isequal(size(grad),size(S)));
%         end
        
        function [d,n,t] = getParameters(this)
            d = 2*this.d_; n = this.n_; t = this.t_;
        end
    end
end