function [nash_point,nash_ratio,egal_point,egal_ratio, util_point,util_ratio, ks_point,ks_ratio]=plotSolutions(points,SP)
reducedPoints = SP - points;
normalizedPoints = reducedPoints ./ SP;
hull=plotConvexHull(reducedPoints);
plotParetoAvgPoints(reducedPoints,hull);

try
    [nash_point, nash_ratio] = maximize_nash_product(points, [0,0]);
    plot(nash_point(1), nash_point(2), 'bo', 'MarkerSize', 3, 'MarkerFaceColor', 'b'); % Plot the point in blue
    text(nash_point(1), nash_point(2), 'Nash', 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right', 'Color', 'r', 'FontSize', 10);
    
catch
    disp('No Nash solution found.');
end

try
    [egal_point, egal_ratio] = findEgalitarianSolution(reducedPoints);
    plot(egal_point(1), egal_point(2), 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'r'); % Plot the point in blue
    text(egal_point(1), egal_point(2), 'Egalitarian', 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right', 'Color', 'r', 'FontSize', 10);
catch
    disp('No Egalitarian solution found.');
end

try
    [util_point,util_ratio] = findUtilitarianSolution(reducedPoints);
    plot(util_point(1), util_point(2), 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'r'); % Plot the point in blue
    text(util_point(1), util_point(2), 'Utilitarian', 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right', 'Color', 'r', 'FontSize', 10);
catch
    disp('No Egalitarian solution found.');
end


try
    [ks_point, ks_ratio] = maximize_kalai_smorodinsky(reducedPoints);
    plot(ks_point(1), ks_point(2), 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'r'); % Plot the point in blue
    text(ks_point(1), ks_point(2), 'KS', 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right', 'Color', 'r', 'FontSize', 10);
catch
    disp('No KS solution found.');
end