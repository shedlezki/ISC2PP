import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Step 1: Create a NetworkX graph
G = nx.Graph()
G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])  # Example of a simple cycle

# Step 2: Define the positions of nodes using a spring layout
pos = nx.spring_layout(G)

# Step 3: Define the path (list of nodes) for the circle to follow
path = [0, 1, 2, 3, 4, 0]  # A path along the graph edges

# Step 4: Set up the plot
fig, ax = plt.subplots()
nx.draw(G, pos, ax=ax, with_labels=True, node_color='lightblue', node_size=500, font_size=16)

# Draw the graph once
nodes = list(G.nodes)
path_edges = list(zip(path[:-1], path[1:]))

# Step 5: Draw the moving circle
circle, = ax.plot([], [], 'o', color='red', markersize=15)  # The circle to animate

# Step 6: Helper function to interpolate between two points
def interpolate(p1, p2, alpha):
    """Interpolate between points p1 and p2 by alpha (0 <= alpha <= 1)."""
    return (1 - alpha) * p1 + alpha * p2

# Step 7: Create a list of all interpolated points along the edges in the path
def get_interpolated_positions(path, pos, num_steps_per_edge=50):
    interpolated_positions = []
    for i in range(len(path) - 1):
        start_node = path[i]
        end_node = path[i + 1]
        start_pos = np.array(pos[start_node])
        end_pos = np.array(pos[end_node])
        for step in np.linspace(0, 1, num_steps_per_edge):
            interpolated_positions.append(interpolate(start_pos, end_pos, step))
    return interpolated_positions

# Get interpolated positions along the edges
interpolated_positions = get_interpolated_positions(path, pos)

# Step 8: Update function for the animation
def update(num):
    x, y = interpolated_positions[num]  # Get the interpolated position
    circle.set_data(x, y)  # Move the circle to the new position
    return circle,

# Step 9: Create the animation
ani = animation.FuncAnimation(fig, update, frames=len(interpolated_positions), interval=50, blit=True, repeat=True)
plt.autoscale()
# Show the animation
plt.show()
