classdef (Abstract) DesignPotential
    methods (Abstract)
         error = computeError(S);
         grad = computeGradient(S);
    end
end