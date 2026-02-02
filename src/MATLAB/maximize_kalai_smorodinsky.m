function [ksSol,ratio] = findKalaiSmorodinsky(gainPoints, d)
    % gainPoints: Nx2 matrix of gain outcomes (utility - disagreement point)

    n = size(gainPoints, 1);

    % Step 1: compute ideal point (max gain for each agent)
    ideal = max(gainPoints, [], 1);

    % Linear program variables: w_1,...,w_n (weights), t (common ratio)
    f = [zeros(n,1); -1];  % maximize t => minimize -t

    % Constraints: sum(w_i * gain_i_j) >= t * ideal_j for j = 1,2
    % -> -sum(...) + t * ideal_j <= 0
    A = zeros(2, n+1);
    A(1,1:n) = -gainPoints(:,1)';
    A(1,end) = ideal(1);
    A(2,1:n) = -gainPoints(:,2)';
    A(2,end) = ideal(2);
    b = [0; 0];

    % Convex combination: sum of weights = 1
    Aeq = [ones(1,n), 0];
    beq = 1;

    % Bounds: 0 <= w_i <= 1, t >= 0
    lb = [zeros(n,1); 0];
    ub = [ones(n,1); Inf];

    % Solve LP
    options = optimoptions('linprog','Display','none');
    [x, ~, exitflag] = linprog(f, A, b, Aeq, beq, lb, ub, options);

    if exitflag ~= 1
        error('No KS solution found.');
    end

    ratio = x(1:n);
    ratio=ratio';
    ksSol = ratio * gainPoints;
end
