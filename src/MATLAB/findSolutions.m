function [nash_point,nash_ratio,egal_point,egal_ratio, util_point,util_ratio, ks_point,ks_ratio]=findSolutions(points,SP1, SP2, SPSP)
% Filter points based on the conditions provided
filteredPoints = points(points(:,1) < SPSP(1) & points(:,2) < SPSP(2), :);
% points = filteredPoints;
SP=[SP1 SP2];
d=[SP1-SPSP(1),SP2-SPSP(2)];
reducedPoints = SP - points;
% normalizedPoints = reducedPoints ./ SP;
% hull=plotConvexHull(reducedPoints);
% plotParetoAvgPoints(reducedPoints,hull);

try
    [nash_point, nash_ratio] = maximize_nash_product(reducedPoints, d);
    nash_point = SP - nash_point;
catch
    disp('No Nash solution found.');
end

try
    [egal_point, egal_ratio] = findEgalitarianSolution(reducedPoints);
    egal_point = SP - egal_point;
catch
    disp('No Egalitarian solution found.');
end

try
    [util_point,util_ratio] = findUtilitarianSolution(reducedPoints);
    util_point = SP - util_point;
catch
    disp('No Egalitarian solution found.');
end


try
    [ks_point, ks_ratio] = maximize_kalai_smorodinsky(reducedPoints, d);
    ks_point = SP - ks_point;
catch
    disp('No KS solution found.');
end