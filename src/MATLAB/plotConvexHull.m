function hullPoints=plotConvexHull(points)


try
    if size(points, 1) == 1
        hullPoints = points; % Return the single point if only one point is provided
        plot(hullPoints(:, 1), hullPoints(:, 2), 'black', 'LineWidth', 2); % Plot the convex hull of the divided pointsre
        return
    elseif size(points, 1) == 2
        % Add a third point that is guaranteed to not be part of the convex hull
        thirdPoint = [min(points(:, 1)), min(points(:, 2))]; % Point with minimal x and y values
        points = [points; thirdPoint]; % Append the third point to the existing points
    elseif rank(points - points(1,:)) == 1
        % Points are colinear: add a third "dummy" point
        thirdPoint = [min(points(:, 1)), min(points(:, 2))]; 
        points = [points; thirdPoint];
    end
    % Calculate convex hull
    hullIndices = convhull(points(:, 1), points(:, 2));
    hullPoints = points(hullIndices, :);

    % Plot convex hull
    plot(hullPoints(:, 1), hullPoints(:, 2), 'black', 'LineWidth', 2);

catch ME
    % Print error message
    fprintf('Error in convhull: %s\n', ME.message);

    % Print the input points
    disp('Input points were:');
    disp(points);
end

% 
% % Plot the normalized utility point
%     plot(normalized_utility(1), normalized_utility(2), 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'b'); % Plot the point in blue
%     plot(utility(1), utility(2), 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'b'); % Plot the point in blue
%     plot(optimal_point(1), optimal_point(2), 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'b'); % Plot the point in blue
% 
%     plot(normalized_utility2(1), normalized_utility2(2), 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'g'); % Plot the point in blue
%     plot(utility2(1), utility2(2), 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'g'); % Plot the point in blue
%     plot(optimal_point2(1), optimal_point2(2), 'bo', 'MarkerSize', 8, 'MarkerFaceColor', 'g'); % Plot the point in blue
% 
% 

end