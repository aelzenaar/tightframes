% The purpose of this script is to find putatively optimal spherical
% designs of _unknown_ n (with fixed d, t).

t = 3;
d = 2;
n_min = 1;
n_max = 10;

comment = 'search_designs';

s = 1000; % Number of seeds to try first
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
    for r_try = 0:10
        fprintf(1, '[n = %d] Trying for step size 10^-%d... ',n,r_try);
        [result, errors, ~] = iterateOnDesign(seed, fast_k, 2, 10^(-r_try), 1, errorComputer, log_file);
        if(errors(end) < initialError)
            fprintf(1, 'Was good.\n');
            r = r_try;
            break;
        else
            fprintf(1, 'failed.\n');
        end
    end
    
    if isnan(r)
        fprintf(1, '[n = %d] Failed to find good step size.\n',n);
        result = NaN(d,n);
        error = inf;
    else
        fprintf(1, '[n = %d] Found good step size. Iterating... ',n);
        [result, errors, ~] = iterateOnDesign(result, slow_k, 2, 10^(-r), 1, errorComputer, log_file);
        error = errors(end);
        fprintf(1, 'done with final error %E\n',error);
    end
    
    errorMultiplier = 10^(-r);
    save(sprintf('%s/run_%d.mat',dirname,n), 'result','errors','d','n','t','errorMultiplier','comment');
    plot(1:length(errors),errors);
    set(gca, 'YScale', 'log');
    saveas(gcf, sprintf('%s/run_%d_errors.png',dirname,n));
    close(gcf);
end

