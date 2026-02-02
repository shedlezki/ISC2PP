import random
import networkx as nx
from math import sqrt
from scipy.spatial import KDTree
import matplotlib.pyplot as plt
import numpy as np

def get_free_cells(grid):
    free = []
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] == 0:
                free.append((x, y))
    return free


def bresenham(x0, y0, x1, y1):
    """Generate all cells a line from (x0, y0) to (x1, y1) passes through."""
    cells = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            cells.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            cells.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    cells.append((x1, y1))
    return cells


def is_collision_free(p1, p2, grid):
    line=bresenham(p1[0], p1[1], p2[0], p2[1])
    for x, y in line:
        if grid[y][x] != 0:
            return False
    return True


def build_prm(grid, num_samples=800, k=5):
    free_cells = get_free_cells(grid)
    if len(free_cells) == 0:
        raise ValueError("No free cells available in the map.")
    
    samples = random.sample(free_cells, min(num_samples, len(free_cells)))
    G = nx.Graph()
    G.add_nodes_from(samples)

    sample_array = np.array(samples)
    tree = KDTree(sample_array)

    for i, s in enumerate(samples):
        dists, idxs = tree.query(s, k=k + 1)  # includes self
        for j in idxs[1:]:  # skip self
            s2 = samples[j]
            if is_collision_free(s, s2, grid):
                dist = sqrt((s[0] - s2[0]) ** 2 + (s[1] - s2[1]) ** 2)
                G.add_edge(s, s2, weight=dist)
    return G

def build_visibility_roadmap(grid, num_samples=1600, k=5):
    free_cells = get_free_cells(grid)
    if len(free_cells) == 0:
        raise ValueError("No free cells available in the map.")
    
    guards=[]
    connectors=[]
    
    G = nx.Graph()
    for i in range(num_samples):
        sample=random.choice(free_cells)
        while sample in guards or sample in connectors:
            sample=random.choice(free_cells)

        visible_nodes=[]
        for node in guards:
            if is_collision_free(sample,node,grid):
                visible_nodes.append(node)
        
        if len(visible_nodes)==0:
            guards.append(sample)
            G.add_node(sample)

        else:
            connected_components=set(min(nx.node_connected_component(G,v)) for v in visible_nodes)
            if(len(connected_components)>1):   
                connectors.append(sample)
                G.add_node(sample)
                for g in visible_nodes:
                    dist = sqrt((sample[0] - g[0]) ** 2 + (sample[1] - g[1]) ** 2)
                    G.add_edge(sample,g, weight=dist)
        

    # samples = random.sample(free_cells, min(num_samples, len(free_cells)))
   
    # G.add_nodes_from(samples)

    # sample_array = np.array(samples)
    # tree = KDTree(sample_array)

    # for i, s in enumerate(samples):
    #     dists, idxs = tree.query(s, k=k + 1)  # includes self
    #     for j in idxs[1:]:  # skip self
    #         s2 = samples[j]
    #         if is_collision_free(s, s2, grid):
    #             dist = sqrt((s[0] - s2[0]) ** 2 + (s[1] - s2[1]) ** 2)
    #             G.add_edge(s, s2, weight=dist)
    return G



def parse_map_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    height = int([line for line in lines if line.startswith('height')][0].split()[1])
    width = int([line for line in lines if line.startswith('width')][0].split()[1])
    map_start_index = lines.index('map\n') + 1
    grid_lines = lines[map_start_index:map_start_index + height]
    grid = np.zeros((height, width))
    for i, line in enumerate(grid_lines):
        for j, char in enumerate(line.strip()):
            if char == '@':
                grid[i, j] = 1  # 1 = obstacle, 0 = free
    return grid


def visualize_map(grid):
    plt.imshow(grid, cmap='gray_r')
    plt.title("MAPF Environment")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.gca().invert_yaxis()  # Make top row correspond to top of image



def read_map_file(fname):
    grid=parse_map_file(fname)
    G = build_visibility_roadmap(grid, num_samples=300, k=10)
    pos = {node: node for node in G.nodes}
    return G, pos, grid

if __name__ == "__main__":
    grid=parse_map_file("./graphs/Berlin_1_256.map")
    visualize_map(grid)
    G = build_visibility_roadmap(grid, num_samples=300, k=10)
    pos = {node: node for node in G.nodes}
    nx.draw(G, pos, node_size=10, with_labels=False, edge_color='red')
    plt.gca().invert_yaxis()
    plt.title("PRM-based Coarse Graph from .map")
    plt.show()