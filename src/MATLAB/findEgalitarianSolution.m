function [egalSol, ratio] = findEgalitarianGain(points)
    % points: Nx2 matrix of gains (u - d)
    n = size(points, 1);
    % Objective: maximize g => minimize -g
    f = [zeros(n,1); -1];

    % Constraints: sum(w_i * points(i,j)) >= g  => -sum(...) + g <= 0
    A = zeros(2, n+1);
    
    A(1,1:n) = -points(:,1)';
    A(1,end) = 1;
    A(2,1:n) = -points(:,2)';
    A(2,end) = 1;
    b = [0; 0];
    % Equality constraint: sum(w_i) = 1
    Aeq = [ones(1,n), 0];
    beq = 1;

    % Bounds
    lb = [zeros(n,1); -Inf];
    ub = [ones(n,1); Inf];

    % Solve LP
    options = optimoptions('linprog','Display','none');
    [x,~,exitflag] = linprog(f, A, b, Aeq, beq, lb, ub, options);

    if exitflag ~= 1
        error('No egalitarian solution found.');
    end

    ratio = x(1:n);
    ratio=ratio';
    egalSol = ratio * points;  % egalitarian gain vector
end
