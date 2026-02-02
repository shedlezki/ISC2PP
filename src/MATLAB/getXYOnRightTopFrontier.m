function [yVal, xVal] = getXYOnRightTopFrontier(dividedHullPoints, x1, y1)
    % Get the top-right frontier from the convex hull
    % Inputs:
    %   dividedHullPoints - Nx2 matrix of [x, y] in counterclockwise order
    %   x1 - x to query for corresponding y on the frontier
    %   y1 - y to query for corresponding x on the frontier
    % Outputs:
    %   yVal - interpolated y at x1
    %   xVal - interpolated x at y1

    points = dividedHullPoints;

    % Find indices of rightmost and topmost points
    [~, idxRight] = max(points(:,1));
    [~, idxTop] = max(points(:,2));

    % Traverse counterclockwise from rightmost to topmost
    n = size(points, 1);
    if idxTop >= idxRight
        frontier = points(idxRight:idxTop, :);
    else
        frontier = [points(idxRight:end, :); points(1:idxTop, :)];
    end

    % Remove possible duplicates
    frontier = unique(frontier, 'rows', 'stable');

    % Interpolate y at x1
    yVal = NaN;
    frontierX = sortrows(frontier, 1);  % sort by x
    xVals = frontierX(:,1);
    if x1 >= min(xVals) && x1 <= max(xVals)
        for j = 1:size(frontierX,1)-1
            A = frontierX(j,:);
            B = frontierX(j+1,:);
            if (A(1) <= x1 && B(1) >= x1) || (A(1) >= x1 && B(1) <= x1)
                t = (x1 - A(1)) / (B(1) - A(1));
                yVal = A(2) + t * (B(2) - A(2));
                break;
            end
        end
        % Exact match
        idx = find(frontierX(:,1) == x1, 1);
        if ~isempty(idx)
            yVal = frontierX(idx,2);
        end
    end

    % Interpolate x at y1
    xVal = NaN;
    frontierY = sortrows(frontier, 2);  % sort by y
    yVals = frontierY(:,2);
    if y1 >= min(yVals) && y1 <= max(yVals)
        for j = 1:size(frontierY,1)-1
            A = frontierY(j,:);
            B = frontierY(j+1,:);
            if (A(2) <= y1 && B(2) >= y1) || (A(2) >= y1 && B(2) <= y1)
                t = (y1 - A(2)) / (B(2) - A(2));
                xVal = A(1) + t * (B(1) - A(1));
                break;
            end
        end
        % Exact match
        idx = find(frontierY(:,2) == y1, 1);
        if ~isempty(idx)
            xVal = frontierY(idx,1);
        end
    end
end
