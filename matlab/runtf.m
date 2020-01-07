% These five are the parameters you might want to change.
d = 2;
n = 12;
t = 4;
k = 4e7; % Number of iterations
s = 1e7; % Number of initial seeds

b = 10;
errorMultiplier = 1e-2; % Reduce if badness proportion > 0.9ish.
errorExp = 1.2;
comment = '**VARYING VECTORS DIRECTLY**';

% profile clear
% profile on
errorComputer = ComplexDesignPotential(d,n,t);
A = getRandomComplexSeed(d,n,s,errorComputer,1);
[result, errors, totalBadness] = iterateOnDesign(A, k, b, errorMultiplier, errorExp, errorComputer, 1);
% profile off
% profile viewer

disp(result);
fprintf(1, 'Norm of final error %f\n', norm(errors(k)));
fprintf(1, 'Total bad proportion %f\n', totalBadness./k);
save(sprintf('tf_run_%s.mat',datestr(datetime('now'),'yyyy-mm-dd-HH-MM-SS')),...
    'result','errors','totalBadness','d','n','t','k','s','b','errorMultiplier','errorExp','comment');

t = 1:length(errors);
plot(t,errors);
hold on;
set(gca, 'YScale', 'log');
hold off;
