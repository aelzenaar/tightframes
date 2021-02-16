% The purpose of this script is to find putatively optimal spherical
% designs of _unknown_ n (with fixed d, t).

t = 3;
d = 3;
n_min = 2;
n_max = 50;
type = 'weighted';
field = 'complex';

k_try = 1e3;

comment = append('search_designsMO ', field, ' ', type);

fprintf(1, "Searching (d,t) = (%d,%d) in n = %d:%d\n", d, t, n_min, n_max);

dirname = sprintf('search_designsMO_%s_%s_%d_%d_%s',field,type,d,t,datestr(datetime('now'),'yyyy-mm-dd-HH-MM-SS'));
mkdir(dirname);
fprintf(1, 'Output directory: %s\n\n', dirname);

for n = n_min:n_max
    fprintf(1, '[n = %d] Iterating... ',n);
    if(strcmp(field,'real'))
        errorComputer = RealDesignPotential(d,n,t,type);
    elseif strcmp(field, 'complex')
        errorComputer = ComplexDesignPotential(d,n,t,type);
    else
        error('unknown field');
    end
    [result, errors, k] = iterateOnDesignMO(NaN(d,n), k_try, errorComputer);
    fprintf(1, 'done with final error %E\n',errors(end));
        
    save(sprintf('%s/run_real_%03d.mat',dirname,n), 'result','errors','d','n','t','k','comment');
    
    ghostFigure = figure('Visible',false);
    plot(1:length(errors),errors);
    set(gca, 'YScale', 'log');
    saveas(gcf, sprintf('%s/run_%03d_errors.png',dirname,n));
    close(gcf);
end

fprintf(1, 'Output directory was: %s\n', dirname);

