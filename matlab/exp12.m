% These are the parameters you might want to change.
file_from = 'tf_run_2019-12-21-14-07-20.mat';
k = 1e7; % Number of iterations

b = 2;
ap = NaN; % Reduce if "got err: ..." value is becoming constant.
errorMultiplier = 1; % Reduce if badness proportion > 0.9ish.
errorExp = 1.1;

m = matfile(file_from);
result_old = m.result;
d = m.d;
n = m.n;
t = m.t;
s = 0; % Number of initial seeds
comment = ['Generated from ' file_from];

[result, errors, totalBadness] =...
    iterateOnDesign(result_old,k,b,errorMultiplier,errorExp,ComplexDesignPotential(d,n,t),1);

disp(result);
fprintf(1, 'Norm of final error %f\n', norm(errors(k)));
fprintf(1, 'Total bad proportion %f\n', totalBadness./k);
ootest = 1;
save(sprintf('tf_run_%s.mat',datestr(datetime('now'),'yyyy-mm-dd-HH-MM-SS')),...
    'result','errors','totalBadness','d','n','t','k','s','b','ap','errorMultiplier','ootest','comment');

t = 1:length(errors);
plot(t,errors);
hold on;
set(gca, 'YScale', 'log');
hold off;