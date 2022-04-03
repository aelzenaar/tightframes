classdef DesignParameters
    properties (Access = private)
        coefficient
        d
        n
        t
        M
    end
    methods
        function this = DesignParameters(d, n, t, field, type)
            this.d = d;
            this.n = n;
            this.t = t;
            
            if ~strcmp(type,'weighted') && ~strcmp(type,'equal_norm')
                error('Unknown design type: %s',type)
            end
    
            if strcmp(field, 'real')
                this.coefficient = prod(d:2:(d+2*(t-1)))/prod(1:2:(2*t-1));
                if strcmp(type, 'weighted')
                    this.M = spherefactory(d,n);
                elseif strcmp(type, 'equal_norm')
                    this.M = obliquefactory(d,n);
                end
            elseif strcmp(field, 'complex')
                this.coefficient = nchoosek(d+t-1,t);
                if strcmp(type, 'weighted')
                    this.M = spherecomplexfactory(d,n);
                elseif strcmp(type, 'equal_norm')
                    this.M = obliquecomplexfactory(d,n);
                end
            else
                error('Unknown field: %s', field)
            end
        end
        
        function M = getManoptManifold(this)
            M = this.M;
        end
        
        function [d,n,t] = getParameters(this)
            d = this.d;
            n = this.n;
            t = this.t;
        end
        
        function epsilon = computeError(this,S)
            gram = S'*S;
            epsilon = abs(this.coefficient*sum(abs(gram).^(2*this.t),'all') - (sum(diag(gram).^this.t))^2);
        end
        
        
        function grad = computeGradient(this,S)
            gram = S'*S;
            grad = zeros(this.d,this.n);
            for row = 1:this.d
                for col = 1:this.n
                    sum1 = abs(gram(col,:)).^(2*this.t - 2) .* transpose(gram(:,col)) .* S(row, :);
                    grad(row,col) = 4*this.coefficient*this.t*sum(sum1)...
                        - 4*this.t*sum(diag(gram).^(this.t)).*gram(col,col).^(this.t-1).*S(row,col);
                end
            end
        end
    end
end