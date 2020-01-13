% The purpose of this script is to find putatively optimal spherical
% designs of _unknown_ n (with fixed d, t).

t = 3;
d = 2;
n_min = guessOrderLowerBound(d,t);
n_max = n_min*2;

comment = 'search_designs';

s = 1e5; % Number of seeds to try first
fast_k = 1000; % Number of times to iterate to find a good initial step size
slow_k = 1e7; % Number of iterations for the proper iteration.

dirname = sprintf('search_designs_%d_%d_%s',d,t,datestr(datetime('now'),'yyyy-mm-dd-HH-MM-SS'));
mkdir(dirname);
log_file = fopen(sprintf('%s/log.txt', dirname),'w');

for n = n_min:n_max
    errorComputer = ComplexDesignPotential(d,n,t);
    seed = getRandomComplexSeed(d,n,s,errorComputer,log_file);
    initialError = errorComputer.computeError(seed);
    fprintf(1, '[n = %d] Seed has error %E.\n',n,initialError);
    r = NaN;
    result = zeros(d,n);
    for r_try = -10:10
        fprintf(1, '[n = %d] Trying for step size 10^%d... ',n,-r_try);
        [result, errors, ~] = iterateOnDesign(seed, fast_k, 2, 10^(-r_try), 1, errorComputer, log_file);
        if(errors(end) < initialError)
            fprintf(1, 'Was good.\n');
            r = r_try;
            break;
        else
            fprintf(1, 'failed.\n');
        end
    end
    
    if isnan(r) || errors(end) > 100
        fprintf(1, '[n = %d] Failed to find good step size.\n',n);
        result = NaN(d,n);
        error = errors(end);
    else
        fprintf(1, '[n = %d] Found good step size. Iterating... ',n);
        [result, errors, totalBadness] = iterateOnDesign(result, slow_k, 2, 10^(-r), 1, errorComputer, log_file);
        error = errors(end);
        fprintf(1, 'done with final error %E (badness proportion %f)\n',error, totalBadness/slow_k);
    end
    
    errorMultiplier = 10^(-r);
    k = slow_k;
    save(sprintf('%s/run_%03d.mat',dirname,n), 'result','errors','totalBadness','d','n','t','k','errorMultiplier','comment');
    
    ghostFigure = figure('Visible',false);
    plot(1:length(errors),errors);
    set(gca, 'YScale', 'log');
    saveas(gcf, sprintf('%s/run_%03d_errors.png',dirname,n));
    close(gcf);
end

