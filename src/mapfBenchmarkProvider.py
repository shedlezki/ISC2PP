
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random
import visualization

PATH_TO_GRAPHS="../graphs/mapf-map/"
PATH_TO_EVEN_SCENES="../graphs/scen-even/"
PATH_TO_RANDOM_SCENES="../graphs/scen-random/"




def _map_file_to_grid(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    height = int([line for line in lines if line.startswith('height')][0].split()[1])
    width = int([line for line in lines if line.startswith('width')][0].split()[1])
    map_start_index = lines.index('map\n') + 1
    grid_lines = lines[map_start_index:map_start_index + height]
    grid = np.zeros((height, width))
    for i, line in enumerate(grid_lines):
        for j, char in enumerate(line.strip()):
            if char == '@' or char == 'T':
                grid[i, j] = 1  # 1 = obstacle, 0 = free
            elif char== 'X':
                grid[i, j] = -1
    return grid


def _get_grid_graph(grid):
    G = nx.DiGraph()
    rows, cols = len(grid), len(grid[0])
    for i in range(rows):
        for j in range(cols):
            if grid[i][j]<=0:
                G.add_node((i, j),coop=(grid[i][j]==-1))
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 4-neighborhood
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < rows and 0 <= nj < cols and grid[ni][nj]<=0:
                        G.add_edge((i, j), (ni, nj), weight=1, tau=1)
    pos = {node: (node[1], -node[0]) for node in G.nodes()}
    return G, pos


def _add_node_weights(G:nx.Graph, ratio=0.5, even=True, standard_time=10, cooperation_time=1, cooperation_setup=False):
    for node in G.nodes:
        if(node=='s_1' or node=='s_2' or node=='g_1' or node=='g_2'):
            t1=0
            t2=0      
        elif (random.random() <=ratio and not cooperation_setup) or (cooperation_setup and G.nodes[node]['coop']==True):
            if even:
                t1=standard_time
                t2=cooperation_time
            else:
                t1=standard_time
                t2=random.randrange(cooperation_time,standard_time)
        else:
            t1=standard_time
            if cooperation_setup:
                t1=cooperation_time
            t2=t1
            
        G.nodes[node]['tau_1']=max(t1,t2)
        G.nodes[node]['tau_2']=min(t1,t2)
    return G


def _random_cell_within_manhattan(grid, x, y, d):
    while True:
        # d = random.randint(0, max_distance)
        di = random.randint(-d, d)
        dj = d - abs(di)
        if random.choice([True, False]):
            dj = -dj
        new_i = y + di
        new_j = x + dj
        if 0 <= new_i < len(grid) and 0 <= new_j < len(grid[0]) and grid[new_j][new_i]==0:
            return (new_j, new_i)
        
def _random_cell_in_grid(grid):
    while True:
        i=random.randint(0,len(grid)-1)
        j=random.randint(0,len(grid[0])-1)
        
        if grid[j][i]==0:
            return (j, i)


def _generate_scenario_points(grid, length, s=None, g=None, distance=-1):
    if(s==None or g==None or distance==-1):
        start_x,start_y=_random_cell_in_grid(grid)
        goal_x,goal_y=_random_cell_within_manhattan(grid,start_x, start_y, length)
    else:
        (start_x,start_y)=s
        while (start_x,start_y)==g or (start_x,start_y)==s:
            start_x,start_y=_random_cell_within_manhattan(grid,s[0], s[1], distance)
        goal_x,goal_y=start_x,start_y
        while (start_x,start_y)==(goal_x,goal_y) or (goal_x,goal_y)==g or (goal_x,goal_y)==s:
            goal_x,goal_y=_random_cell_within_manhattan(grid,g[0],g[1], distance)
    
    return (start_x, start_y), (goal_x, goal_y) 



def _get_scenario_points(scene_file, line_number):
    with open(scene_file, 'r') as f:
        lines = f.readlines()

    if line_number > len(lines) - 1 or line_number<0:
        line_number=random.randint(0,len(lines) - 1)
   
    line = lines[line_number]  # +1 to skip the 'version' header
    parts = line.strip().split()
    if len(parts) < 8:
        raise ValueError("Invalid scenario line format.")

    start_x, start_y = int(parts[4]), int(parts[5])
    goal_x, goal_y = int(parts[6]), int(parts[7])
    dist=float(parts[8])
    return (start_x, start_y), (goal_x, goal_y)


def _add_or_set(G,pos,node,name):
    if G.has_node(node):
        G=nx.relabel_nodes(G, {node: name})
        pos[name]=(node[1], -node[0])
        pos.pop(node)
    else:
        print('else')
        pass
    


    return G, pos


def _add_start_and_target_nodes(G: nx.Graph, pos, scene_file, line1=-1, line2=-1):    
    s1,g1=_get_scenario_points(scene_file, line1)
    s2,g2=s1,g1
    while s2==s1 and g2==g1:
        s2,g2=_get_scenario_points(scene_file, line2)

    # s1,g1=(0,0),(5,5)
    # s2,g2=(1,1),(6,6)

    G, pos=_add_or_set(G, pos,s1,'s_1')
    G, pos=_add_or_set(G, pos,s2,'s_2')
    G, pos=_add_or_set(G, pos,g1,'g_1')
    G, pos=_add_or_set(G, pos,g2,'g_2')
   
    return G, pos

def _generate_and_add_start_and_target_nodes(G: nx.Graph, pos, grid, distance, length):    
    s1,g1=_generate_scenario_points(grid, length=length)
    s2, g2=_generate_scenario_points(grid, length=length, s=s1, g=g1, distance=distance)
    # print(s1,g1,s2,g2)
    # s1=(29,5)
    # g2=(9,5)
    # print(grid[9][5])
    # print(grid[29][5])
    # print(grid[29][7])
    # print(grid[8][4])
    # print(grid[0][0])
    # s2=(29,7)
    # g1=(8,4)
    G, pos=_add_or_set(G, pos,s1,'s_1')
    G, pos=_add_or_set(G, pos,s2,'s_2')
    G, pos=_add_or_set(G, pos,g1,'g_1')
    G, pos=_add_or_set(G, pos,g2,'g_2')
   
    return G, pos


def _draw_grid_and_graph(grid, G, pos):
    rows, cols = len(grid), len(grid[0])
    fig, ax = plt.subplots(figsize=(cols / 5, rows / 5))

    # Draw the grid: obstacles in black, free in white
    for i in range(rows):
        for j in range(cols):
            color = 'white' if grid[i][j]==0 else 'black'
            ax.add_patch(plt.Rectangle((j, rows - 1 - i), 1, 1, facecolor=color, edgecolor='gray', linewidth=0.2))

    # Graph node positions centered in each cell   
    pos = {node: (pos[node][0] + 0.5, rows - 1 + pos[node][1] + 0.5) for node in G.nodes()}
    node_colors = ['purple' if node == 's_1' or node=='g_1' else 'green' if node=='s_2' or node=='g_2' else 'blue' if G.nodes[node]['tau_1']>G.nodes[node]['tau_2'] else 'black' for node in G.nodes()]

    # Draw graph edges and nodes on top
    nx.draw_networkx_edges(G, pos, ax=ax, width=0.5, edge_color='red', alpha=0.7)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=8, node_color=node_colors)

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    plt.show()


def get_graph(map, scene, type='grid', ratio=0.5, coopertion_strength=10, distance=3, length=20, cooperation_setup=False):
    grid=_map_file_to_grid(PATH_TO_GRAPHS+map+'.map')
    if type=='grid':
        G,pos=_get_grid_graph(grid)
    else:
        G,pos=_get_grid_graph(grid)

    # G, pos=_add_start_and_target_nodes(G,pos,PATH_TO_EVEN_SCENES+map+'-'+scene+'.scen')
    if cooperation_setup:
        G, pos=_add_start_and_target_nodes(G,pos,PATH_TO_EVEN_SCENES+map+'-'+scene+'.scen')
        # print(G.nodes['s_1'],G.nodes['s_2'],G.nodes['g_1'],G.nodes['g_2'])
    else:
        G, pos=_generate_and_add_start_and_target_nodes(G,pos,grid, distance, length)
        # print(G.nodes['s_1'],G.nodes['s_2'],G.nodes['g_1'],G.nodes['g_2'])
    G=_add_node_weights(G,ratio,True,coopertion_strength,1, cooperation_setup)

    return G, pos, grid

if __name__ == "__main__":
    map='empty-8-8'
    scene='even-1'

    grid=_map_file_to_grid(PATH_TO_GRAPHS+map+'.map')
    G,pos=_get_grid_graph(grid)
    G,pos=_add_start_and_target_nodes(G,pos,PATH_TO_EVEN_SCENES+map+'-'+scene+'.scen')
    G=_add_node_weights(G,0.5,True,3,1)

    visualization.visualize(G,pos,None, grid)

    # print([G.nodes[n]['tau_1'] for n in G.nodes])
    # # print(pos['s_1'])
    # draw_grid_and_graph(grid, G, pos)

    # visualize_map(parse_map_file('./graphs/mapf-map/room-64-64-16.map'))

    # nx.draw(G, pos, node_size=10, with_labels=False, edge_color='red')
    # plt.gca().invert_yaxis()
    # plt.title("PRM-based Coarse Graph from .map")
    # plt.show()

    # plt.figure(figsize=(10, 10))
    # nx.draw(G, pos, node_size=10, node_color='blue', edge_color='gray')
    # plt.show()

