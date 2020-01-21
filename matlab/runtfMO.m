% These five are the parameters you might want to change.
d = 5;
n = 12;
t = 2;
k = 1e6; % Number of iterations

comment = '*MO (k is actual # of iterations done)';

errorComputer = ComplexDesignPotential(d,n,t);
[result, errors, k] = iterateOnDesignMO(NaN(d,n), k, errorComputer);

fprintf(1,'\n')
disp(result);
fprintf(1, 'Norm of final error %f\n', norm(errors(k)));
save(sprintf('tf_runMO_%s.mat',datestr(datetime('now'),'yyyy-mm-dd-HH-MM-SS')),...
    'result','errors','d','n','t','k','comment');

t = 1:length(errors);
plot(t,errors);
hold on;
set(gca, 'YScale', 'log');
hold off;
