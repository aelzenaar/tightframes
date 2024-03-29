% The purpose of this script is to generate all minimal (t,t)-designs, for
% all d and all t.

t_min = 2;
d_min = 3;
type = 'weighted';
field = 'real';

list_from = 1;

k = Inf; % Number of iterates
n_max = Inf; % Number of vectors to check up to
max_iter_each_time = 1e5; % Number of iterations for each (d,n,t) triplet
threshold = 1e-9; % Guess we have a design if error < threshold.
comment = sprintf('tabulate, threshold = %E',threshold);

dirname = sprintf('tabulate_%s_%s_%s',field,type,datestr(datetime('now'),'yyyy-mm-dd-HH-MM-SS'));
mkdir(dirname);
fd = fopen(sprintf('%s/results.csv',dirname), 'w');

% We want to run until the heat death of the universe.
warning('off','MATLAB:warn_truncate_for_loop_index');

fprintf(1, 'Output directory is: %s\n', dirname);
fprintf(fd, 't,d,n,filename,error image,final error\n');

for h = list_from:k
    % Apply inverse Cantor pairing to h
    % (https://en.wikipedia.org/wiki/Pairing_function#Inverting_the_Cantor_pairing_function)
    w = floor((sqrt(8*h+1)-1)/2);
    v = (w^2 + w)/2;
    d = h - v;
    t = w - d;
    
    d = d + d_min;
    t = t + t_min;
    
    n_min = guessOrderLowerBound(d,t);
    %n_min = 2;
    
    fprintf(1, '[t = %d, d = %d] Searching in n = %d:%d\n', t, d, n_min, n_max);
    for n = n_min:n_max
        fprintf(1, '[t = %d, d = %d, n = %d] Iterating... ',t, d, n);
        if(strcmp(field,'real'))
            errorComputer = RealDesignPotential(d,n,t,type);
        elseif strcmp(field, 'complex')
            errorComputer = ComplexDesignPotential(d,n,t,type);
        else
            error('unknown field');
        end
        
        [result, errors, ~] = iterateOnDesignMO(NaN(d,n), max_iter_each_time, errorComputer);
        
        fprintf(1, 'done with final error %E',errors(end));
        filename = sprintf('run_%03d_%03d_%03d.mat',t,d,n);
        filename_graph = sprintf('run_%03d_%03d_%03d_errors.png',t,d,n);
        
        % Save design & error graph
        save(sprintf('%s/%s',dirname,filename), 'result','errors','t','d','n','k','comment');
        %ghostFigure = figure('Visible',false);
        %plot(1:length(errors),errors);
        %set(gca, 'YScale', 'log');
        %saveas(gcf, sprintf('%s/%s', dirname, filename_graph));
        %close(gcf);
        
        if(errors(end) < threshold)
            fprintf(1, ' (met threshold!)\n');
            
            % Log to results database file
            fprintf(fd, '%d,%d,%d,%s,%s,%E\n', t, d, n, filename, filename_graph, errors(end));
                        
            break;
        end
        fprintf(1,'\n');
    end
end
