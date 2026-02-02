function [optimal_point,ratio] = maximize_nash_product(points, d)
    x0=d(1);
    y0=d(2);
    x_vals = points(:, 1);
    y_vals = points(:, 2);
    % Objective function to maximize: Nash product of gains
    objective = @(p) -(x0 - dot(p, x_vals)) * (y0 - dot(p, y_vals));
    
    % Constraints: p1 + p2 + p3 + p4 + p5 = 1 (equality)
    % and p_i >= 0 (inequality)
    cons = @(p) deal([], sum(p) - 1); % No inequality constraints, equality constraint is p1 + p2 + p3 + p4 + p5 = 1
    
    
    count = size(points, 1);    
    % Bounds: all p_i ≥ 0
    lb = zeros(1, count);
    ub = ones(1, count);
    
    % Initial guess
    p0 = 1/count* ones(1, count);
    
    % Options for optimization
    options = optimoptions('fmincon', 'Display', 'off');
    
    % Solve
    optimal_p = fmincon(objective, p0, [], [], [], [], lb, ub, cons, options);

    % Output calculations
    ratio=optimal_p;
    optimal_point = [dot(optimal_p, x_vals), dot(optimal_p, y_vals)];
    % utility = [x0 - optimal_point(1), y0 - optimal_point(2)];
    % normalized_utility = [(x0 - optimal_point(1)) / x0, (y0 - optimal_point(2)) / y0];
    % nash_product = utility(1) * utility(2);
end