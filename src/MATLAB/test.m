% Define the points

% 
  % points = [70,70;41,75;91,57];
  % SP=[112,122]
% points=[1,2;2,1;5,5]
% SP=[7,7]
hold off
hold on


% Plot the line x = y
x = linspace(0, 100, 100); % Generate x values
y = x; % Since y = x, we can directly assign y
% plot(x, y, 'g--', 'LineWidth', 1.5); % Plot the line in green dashed style


% points = [95,61; 85,85;76,98;67,101;89,67];
% SP=[122,144];
% plotSolutions(points, SP);
% 
% points = [70,70;41,75;91,57];
% SP=[112,122];
% plotSolutions(points, SP);
% 
% points = [66, 100;116, 82; 87,87];
% SP=[166,166];
% plotSolutions(points, SP);
% 
% points = [93, 71;75, 97; 101,67];
% SP=[166,144];
% plotSolutions(points, SP);


points = [34, 29;25, 30];
SP=[37,42];
% reducedPoints = SP - points;
% x=reducedPoints(:,1);
% y=reducedPoints(:,2);
% plot(x,y, 'bo', 'MarkerSize', 8, 'LineWidth', 1.5); % blue circles
% normalizedPoints = reducedPoints ./ SP;
% plotConvexHull(reducedPoints)

 % points=[24, 29];
 % SP=[37,47];
 reducedPoints = SP - points; % Calculate the reduced points based on SP
 plotConvexHull(reducedPoints);
% points = [70, 92;82, 82; 100,78; 108,74];
% SP=[156,156];


 [nash_point,nash_ratio,egal_point,egal_ratio, util_point,util_ratio, ks_point,ks_ratio]=findSolutions(points, 37,42,[37 42]);
 % [nash_point,nash_ratio,egal_point,egal_ratio, util_point,util_ratio, ks_point,ks_ratio]=findSolutions(points, SP);
% display(nash_ratio);
% display(egal_ratio);
% display(util_ratio);
% display(ks_ratio);
disp(nash_point);
disp(egal_point);
disp(util_point);
disp(ks_point);

points = [29, 34;30, 25];
SP=[42,37];
 reducedPoints = SP - points; % Calculate the reduced points based on SP
 plotConvexHull(reducedPoints);
  [nash_point,nash_ratio,egal_point,egal_ratio, util_point,util_ratio, ks_point,ks_ratio]=findSolutions(points, 42, 37, [42 37]);
 % [nash_point,nash_ratio,egal_point,egal_ratio, util_point,util_ratio, ks_point,ks_ratio]=findSolutions(points, SP);
% display(nash_ratio);
% display(egal_ratio);
% display(util_ratio);
% display(ks_ratio);
disp(nash_point);
disp(egal_point);
disp(util_point);
disp(ks_point);