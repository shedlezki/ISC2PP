function [utilitarianSol,ratio] = findUtilitarianSolution(points)
    % Use LP to find convex combination that maximizes total utility

    n = size(points, 1);
    f = -sum(points, 2);  % we minimize negative utility for maximization
    Aeq = ones(1, n);
    beq = 1;
    lb = zeros(n, 1);

    % Linear programming to find the convex combination
    options = optimoptions('linprog','Display','off');
    [ratio, ~, exitflag] = linprog(f, [], [], Aeq, beq, lb, [], options);

    if exitflag ~= 1
        error('Linear program did not converge.');
    end
    ratio=ratio';
    utilitarianSol = ratio * points;
end
