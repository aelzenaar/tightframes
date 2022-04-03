keep_going = 1;
family = 0.6827; % Family 1
%family = 0.4376; % Family 2
% while keep_going
    dp = DesignParameters(3,24,4,'real','equal_norm');
    options.maxiter = 10000;
%     options.verbosity = 0;
    warning('off', 'manopt:getHessian:approx')

    problem.M = obliquefactory(3,8);
    problem.cost = @(x) err(dp,x);
    problem.egrad = @(x) gradient(dp,x);
    
    [A, cost, info, ~] = trustregions(problem,[],options);
    
%     if cost < 1e-3 & sum(abs(A(1,:) - family) < 0.0001) > 0
%         disp(toframe(A));
%         keep_going = 0;
%     end
    
% end

function frame = toframe(x)
    % Take the eight columns of x and rotate by 120 and 240 degrees.
    rot120 = [cos(2*pi/3), -sin(2*pi/3); sin(2*pi/3), cos(2*pi/3)];
    rot240 = rot120^2;
    
    frame = [x(1,:), x(1,:), x(1,:); x(2:3,:), rot120*x(2:3,:), rot240*x(2:3,:)];
    frame = frame./vecnorm(frame);
end

function g = gradient(dp,x)
    f = toframe(x);
    
    mod = zeros(3,8);
    mod(1,1) = 20000*(f(1,1) - 0);
    mod(1,2) = 20000*(f(1,2) - 0.20131);
    g=dp.computeGradient(f);
    g = g(:,1:8) + mod;
end

function e = err(dp,x)
    f = toframe(x);
    
    e = dp.computeError(f) + 10000*(x(1,1) - 0)^2 + 10000*(x(1,2) - 0.20131)^2;
end

