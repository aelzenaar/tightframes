% These five are the parameters you might want to change.
d = 2;
n = 12;
t = 4;
k = 1e6; % Number of iterations
s = 1e6; % Number of initial seeds
b = 10;
ap = 10;
errorMultiplier = 1e-2;

% profile clear
% profile on
[result, errors, totalBadness] = tightframe(d, n, t, k, s, b, ap, errorMultiplier, 1);
% profile off
% profile viewer

disp(result);
fprintf(1, 'Norm of final error %f\n', norm(errors(k)));
fprintf(1, 'Total bad proportion %f\n', totalBadness./k);
save(sprintf('tf_run_%s.mat',datestr(datetime('now'),'yyyy-mm-dd-HH-MM-SS')),...
    'result','errors','totalBadness','d','n','t','k','s','b','ap','errorMultiplier');

x = 1:length(errors);
plot(x,errors);
hold on;
set(gca, 'YScale', 'log');
hold off;
