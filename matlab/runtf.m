% These five are the parameters you might want to change.
d = 5;
n = 12;
t = 2;
k = 1e6; % Number of iterations
s = 1e5; % Number of initial seeds

b = 2;
errorMultiplier = 1e-5; % Reduce if badness proportion > 0.9ish.
errorExp = 1;
comment = '**VARYING VECTORS DIRECTLY**';

% profile clear
% profile on
errorComputer = ComplexDesignPotential(d,n,t);
A = getRandomComplexSeed(d,n,s,errorComputer,1);
[result, errors, totalBadness] = iterateOnDesign(A, k, b, errorMultiplier, errorExp, errorComputer, 1);
% profile off
% profile viewer

fprintf(1,'\n')
disp(result);
fprintf(1, 'Norm of final error: %f\n', norm(errors(k)));
fprintf(1, 'Total bad proportion: %f\n', totalBadness./k);

outfile_stem = sprintf('tf_run_%s',datestr(datetime('now'),'yyyy-mm-dd-HH-MM-SS'));
outfile_mat = sprintf('%s.mat',outfile_stem);
outfile_graph = sprintf('%s_errors.png',outfile_stem);

save(outfile_mat, 'result','errors','totalBadness','d','n','t','k','s','b','errorMultiplier','errorExp','comment');
fprintf(1, 'Output file: %s\n', outfile_mat);

t = 1:length(errors);
plot(t,errors);
hold on;
set(gca, 'YScale', 'log');
hold off;
saveas(gcf,outfile_graph);

fprintf(1, 'Error graph: %s\n', outfile_graph);
