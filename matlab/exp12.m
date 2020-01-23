% These are the parameters you might want to change.
file_from = 'tf_run_2020-01-16-18-12-10';
k = 1e5; % Number of iterations

b = 2;
errorMultiplier = 10; % Reduce if badness proportion > 0.9ish.
errorExp = 1;

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

outfile_stem = sprintf('tf_run_%s',datestr(datetime('now'),'yyyy-mm-dd-HH-MM-SS'));
outfile_mat = sprintf('%s.mat',outfile_stem);
outfile_graph = sprintf('%s_errors.png',outfile_stem);

save(outfile_mat, 'result','errors','totalBadness','d','n','t','k','s','b','errorMultiplier','comment','errorExp');
fprintf(1, 'Output file: %s\n', outfile_mat);

t = 1:length(errors);
plot(t,errors);
hold on;
set(gca, 'YScale', 'log');
hold off;
saveas(gcf,outfile_graph);

fprintf(1, 'Error graph: %s\n', outfile_graph);
