% The purpose of this script is to find putatively optimal spherical
% designs of _unknown_ n (with fixed d, t).

t = 3;
d = 5;
n_min = guessOrderLowerBound(d,t);
n_max = n_min*2;

k_try = 1e3;

comment = 'search_designsMO';

fprintf(1, "Searching (d,t) = (%d,%d) in n = %d:%d\n", d, t, n_min, n_max);

dirname = sprintf('search_designsMO_%d_%d_%s',d,t,datestr(datetime('now'),'yyyy-mm-dd-HH-MM-SS'));
mkdir(dirname);
fprintf(1, 'Output directory: %s\n\n', dirname);

for n = n_min:n_max
    fprintf(1, '[n = %d] Iterating... ',n);
    errorComputer = ComplexDesignPotential(d,n,t);
    [result, errors, k] = iterateOnDesignMO(NaN(d,n), k_try, errorComputer);
    fprintf(1, 'done with final error %E\n',errors(end));
        
    save(sprintf('%s/run_%03d.mat',dirname,n), 'result','errors','d','n','t','k','comment');
    
    ghostFigure = figure('Visible',false);
    plot(1:length(errors),errors);
    set(gca, 'YScale', 'log');
    saveas(gcf, sprintf('%s/run_%03d_errors.png',dirname,n));
    close(gcf);
end

fprintf(1, 'Output directory was: %s\n', dirname);

