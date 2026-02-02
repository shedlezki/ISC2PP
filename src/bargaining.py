import numpy as np
from scipy.optimize import minimize

# Given data
[(95, 61), (85, 85), (76, 98), (67, 101), (89, 67)]
x_vals = np.array([95,85,76,67,89])
y_vals = np.array([61,85,98,101,67])

x_vals=[95,85,76,101,89]
y_vals=[61,85,98,89,67]
# Disagreement point (non-cooperative outcome)
x0 = 122
y0 = 144

# Objective function to maximize: Nash product of gains
def objective(p):
    x_p = np.dot(p, x_vals)
    y_p = np.dot(p, y_vals)
    gain1 = x0 - x_p
    gain2 = y0 - y_p
    # Negative sign because we use a minimizer
    return -gain1 * gain2

# Constraints: p1 + p2 + p3 + p4 = 1
cons = {'type': 'eq', 'fun': lambda p: np.sum(p) - 1}

# Bounds: all p_i ≥ 0
bounds = [(0, 1)] * 5

# Initial guess
p0 = [0.2]*5

# Solve
res = minimize(objective, p0, bounds=bounds, constraints=cons)

# Output
optimal_p = res.x
optimal_point = (np.dot(optimal_p, x_vals), np.dot(optimal_p, y_vals))
nash_product = (x0 - optimal_point[0]) * (y0 - optimal_point[1])
np.set_printoptions(precision=10, suppress=True)
print("Optimal weights (p):", optimal_p)
print("Resulting point (x(p), y(p)):", optimal_point)
print("Resulting point utility: ",(122-optimal_point[0],144-optimal_point[1]))
print("Resulting point utility normalized: ",((122-optimal_point[0])/122,(144-optimal_point[1])/144))
print("Maximized Nash product:", nash_product)
