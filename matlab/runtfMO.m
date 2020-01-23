% These five are the parameters you might want to change.
d = 5;
n = 157;
t = 3;
k = 1e6; % Number of iterations

comment = '*MO (k is actual # of iterations done)';

errorComputer = ComplexDesignPotential(d,n,t);
[result, errors, k] = iterateOnDesignMO(NaN(d,n), k, errorComputer);

fprintf(1,'\n')
disp(result);
fprintf(1, 'Norm of final error %f\n', norm(errors(k)));

outfile_stem = sprintf('tf_runMO_%s',datestr(datetime('now'),'yyyy-mm-dd-HH-MM-SS'));
outfile_mat = sprintf('%s.mat',outfile_stem);
outfile_graph = sprintf('%s_errors.png',outfile_stem);

save(outfile_mat, 'result','errors','d','n','t','k','comment');
fprintf(1, 'Output file: %s\n', outfile_mat);

t = 1:length(errors);
plot(t,errors);
hold on;
set(gca, 'YScale', 'log');
hold off;
saveas(gcf,outfile_graph);

fprintf(1, 'Error graph: %s\n', outfile_graph);
