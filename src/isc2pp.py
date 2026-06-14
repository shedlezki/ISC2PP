import networkx as nx
import bisect 


# merge the paths and lengths into a single dictionary with the source node as the key and a dictionary of destination nodes and their corresponding paths and times as the value
def merge_paths_and_lengths(paths, lengths):
    merged = {}
    for src in paths:
        merged[src] = {}
        for dest in paths[src]:
            merged[src][dest] = {
                'path': paths[src][dest],
                'length': lengths[src][dest]
            }
    return merged


# adding the node travel time to the edge travel time to get the total travel time for each edge (for use with nx's shortest path algorithms)
def get_waits_included_graph(G, tau):
    G_mod = G.copy()
    for node in G.nodes:
        for neighbor in G.neighbors(node):
            if('visited' not in G_mod[node][neighbor]):
                G_mod[node][neighbor]['visited']=True
                G_mod[node][neighbor]['tau'] += G_mod.nodes[node][tau]
    return G_mod


# find the shortest paths from all nodes to all other nodes in the graph and return them in a dictionary with the source node as the key and a dictionary of destination nodes and their corresponding paths and times as the value
def all_pairs_shortest_paths(G, tau):
    G_mod=get_waits_included_graph(G, tau)
    shortest_paths = dict(nx.all_pairs_dijkstra_path(G_mod,weight='tau'))
    shortest_path_lengths = dict(nx.all_pairs_dijkstra_path_length(G_mod,weight='tau'))
    return merge_paths_and_lengths(shortest_paths, shortest_path_lengths)


# find the shortest paths from a source node to all other nodes in the graph and return them in a dictionary with the destination node as the key and the corresponding path and its time as the value
def shortest_paths(G, s, tau):
    G_mod=get_waits_included_graph(G, tau)

    shortest_paths = dict(nx.single_source_dijkstra_path(G_mod,s ,weight='tau'))
    shortest_path_lengths = dict(nx.single_source_dijkstra_path_length(G_mod, s, weight='tau'))
    return {key: {'path': shortest_paths[key], 'length': shortest_path_lengths[key]} for key in shortest_paths.keys()}


# find all shortest non-cooperative partial paths starting from v_s1 and return them in a dictionary with the ending node as the key and the corresponding path and its time as the value
def all_nodes_shortest_non_cooperative_partial_paths(G, V_C,v_s1, SP1_s2):
    open_nodes=[v_s1]
    paths={v_s1:{'path':[v_s1], 'length': 0} }
    while open_nodes:
        v=open_nodes.pop(0)
        if v not in V_C or SP1_s2[v]['length'] > paths[v]['length'] + G.nodes[v]['tau_1'] - G.nodes[v]['tau_2']:
            neighbors=G.neighbors(v) 
            for n in neighbors:
                if (n not in paths) or (paths[v]['length']+G.nodes[v]['tau_1']+G[v][n]['tau']<paths[n]['length']):
                    paths[n]={}
                    paths[n]['length']=paths[v]['length']+G.nodes[v]['tau_1']+G[v][n]['tau']
                    paths[n]['path']=paths[v]['path']+[n]
                    if(n in open_nodes):
                        open_nodes.remove(n)
                    bisect.insort(open_nodes,n,key=lambda x:paths[x]['length'])
    return paths


# find all shortest stable partial paths ending at v_cd and return them in a dictionary with the starting node as the key and the corresponding path and its time as the value
def all_nodes_shortest_stable_partial_paths(G, V_C,v_cd, SP1_g1, SP1_g2):
    open_nodes=[v_cd]
    closed_nodes=set()
    paths={v_cd:{'path':[v_cd], 'length': 0} }
    while open_nodes:
        v=open_nodes.pop(0)      
        closed_nodes.add(v)  
        neighbors=G.neighbors(v)
        for n in neighbors:
            if(n not in closed_nodes and G[v][n]['tau'] + G.nodes[v]['tau_2']+paths[v]['length']+SP1_g1[v_cd]['length'] <= SP1_g1[n]['length'] and G[v][n]['tau'] + G.nodes[v]['tau_2'] +paths[v]['length']+SP1_g2[v_cd]['length'] <= SP1_g2[n]['length']):
                if n not in paths or G[v][n]['tau'] + G.nodes[v]['tau_2']+paths[v]['length'] < paths[n]['length']:
                    paths[n]={}
                    paths[n]['length']=G[v][n]['tau'] + G.nodes[v]['tau_2']+paths[v]['length']
                    paths[n]['path']=[n]+paths[v]['path']
                    if(n in open_nodes):
                        open_nodes.remove(n)
                    bisect.insort(open_nodes,n,key=lambda x:paths[x]['length'])
    return {v:{'path': paths[v]['path'], 'length': paths[v]['length'] - G.nodes[v_cd]['tau_2'] } for v in paths}


# find optimal cooperation joint strategy for a given cooperation departure node v_cd and return it
def optimal_stable_js_to_cooperation_ending_node(G,V_C, v_cd, v_s1, v_g1, v_s2, v_g2):
    SP1_s1=shortest_paths(G,v_s1,'tau_1')
    SP1_s2=shortest_paths(G,v_s2,'tau_1')
    SP1_g1=shortest_paths(G,v_g1,'tau_1')
    SP1_g2=shortest_paths(G,v_g2,'tau_1')
    SPS_cd=all_nodes_shortest_stable_partial_paths(G,V_C,v_cd,SP1_g1, SP1_g2)
    SPNC_s1=all_nodes_shortest_non_cooperative_partial_paths(G,V_C,v_s1,SP1_s2)
    SPNC_s2=all_nodes_shortest_non_cooperative_partial_paths(G,V_C,v_s2,SP1_s1)
    v_cs_opt=None
    optimal_ne=float('inf')
    for v_cs in V_C:
        if v_cs not in SPNC_s1 or v_cs not in SPNC_s2 or v_cs not in SPS_cd:
            continue
        if v_cs in SPS_cd and max(SPNC_s1[v_cs]['length'],SPNC_s2[v_cs]['length'])+G.nodes[v_cs]['tau_2']+SPS_cd[v_cs]['length']<=optimal_ne:
            optimal_ne=max(SPNC_s1[v_cs]['length'],SPNC_s2[v_cs]['length'])+G.nodes[v_cs]['tau_2']+SPS_cd[v_cs]['length']
            v_cs_opt=v_cs
    if optimal_ne+G.nodes[v_cd]['tau_2']+SP1_g1[v_cd]['length']<=SP1_s1[v_g1]['length'] and optimal_ne+G.nodes[v_cd]['tau_2']+SP1_g2[v_cd]['length']<=SP1_s2[v_g2]['length']:
        path1={}
        path2={}
        path_from_s1_to_cs=SPNC_s1[v_cs_opt]['path'].copy()
        path_from_s2_to_cs=SPNC_s2[v_cs_opt]['path'].copy()

        if SPNC_s1[v_cs_opt]['length']>SPNC_s2[v_cs_opt]['length']:
            path_from_s2_to_cs.insert(-1,'WAIT_'+str( SPNC_s1[v_cs_opt]['length']-SPNC_s2[v_cs_opt]['length']))

        elif SPNC_s1[v_cs_opt]['length']<SPNC_s2[v_cs_opt]['length']:
             path_from_s1_to_cs.insert(-1,'WAIT_'+str( SPNC_s2[v_cs_opt]['length']-SPNC_s1[v_cs_opt]['length']))


        path1['path']=concat_paths([path_from_s1_to_cs,SPS_cd[v_cs_opt]['path'],list(reversed(SP1_g1[v_cd]['path']))])
        path1['length']=optimal_ne+G.nodes[v_cd]['tau_2']+SP1_g1[v_cd]['length']
        path2['path']=concat_paths([path_from_s2_to_cs,SPS_cd[v_cs_opt]['path'],list(reversed(SP1_g2[v_cd]['path']))])
        path2['length']=optimal_ne+G.nodes[v_cd]['tau_2']+SP1_g2[v_cd]['length']
        return (path1,path2)
    else:
        return (SP1_s1[v_g1],SP1_s2[v_g2])


# exposed to find the best response path for player 1 given player 2's path and return it (the best response path is the path that minimizes player 1's path time given player 2's path)
def best_response(G,V_C,v_s1,v_g1,path2):
    SP1_s1=shortest_paths(G,v_s1,'tau_1')
    SP1_g1=shortest_paths(G,v_g1,'tau_1')
    return _best_response(G,V_C,v_s1,v_g1,SP1_s1, SP1_g1, path2)


# private function for best_response - find the best response path for player 1 given player 2's path and return it (the best response path is the path that minimizes player 1's path time given player 2's path)
def _best_response(G, V_C, v_s1, v_g1, SP1_s1,SP1_g1,path2):
    v_c1=None
    v_d=None
    path2_time=0
    for i,v in enumerate(path2):
        if SP1_s1[v]['length']+G.nodes[v]['tau_2']<=path2_time and v in V_C:
            v_c1=v
            path2_time-=G.nodes[v]['tau_1']
            break
        if i<len(path2)-1:
            path2_time+=G[v][path2[i+1]]['tau']+G.nodes[path2[i+1]]['tau_1']
    else:
        return SP1_s1[v_g1]
    
    path2=path2[path2.index(v_c1):]
    coop=max(SP1_s1[v_c1]['length'],path2_time)
    optimal=float('inf')
    for i,v in enumerate(path2):
        coop+=G.nodes[v]['tau_2']
        if coop+SP1_g1[v]['length']<=optimal:
            optimal = coop+SP1_g1[v]['length']
            v_d=v
        if i<len(path2)-1:
            coop+=G[v][path2[i+1]]['tau']
    if optimal<=SP1_s1[v_g1]['length']:
        path_from_s1_to_c1=SP1_s1[v_c1]['path'].copy()
        if SP1_s1[v_c1]['length']<path2_time:
            path_from_s1_to_c1.insert(-1,'WAIT_'+str( path2_time-SP1_s1[v_c1]['length']))
        ret={}
        ret['path']=concat_paths([path_from_s1_to_c1,path2[path2.index(v_c1):path2.index(v_d)+1], list(reversed(SP1_g1[v_d]['path']))])
        ret['length']=optimal
        return ret
    else:
        return SP1_s1[v_g1]


# find the shortest independent path from v_s to v_g (assuming no cooperation at any node) and return its time
def shortest_independent_path(G,v_s,v_g):
    return shortest_paths(G,v_s,'tau_1')[v_g]


# find the shortest cooperation path from v_s to v_g (assuming cooperation in all cooperation nodes) and return its time
def shortest_cooperated_path(G,v_s,v_g):
    return shortest_paths(G,v_s,'tau_2')[v_g]


# find all non-dominated ecjs in the graph and return them in a dictionary with the cooperation departure node as the key and the corresponding ecjs as the value
def map_optimal_ecjs(G,V_C,v_s1,v_s2, v_g1, v_g2):
    SP1_s1=shortest_paths(G,v_s1,'tau_1')
    SP1_s2=shortest_paths(G,v_s2,'tau_1')
    SP1_g1=shortest_paths(G,v_g1,'tau_1')
    SP1_g2=shortest_paths(G,v_g2,'tau_1')
    if v_g1 not in SP1_s1.keys() or v_g2 not in SP1_s2.keys():
        return {None: None}
    result={None:(SP1_s1[v_g1],SP1_s2[v_g2])}
    dominated_nodes=set()
    for v_cd in V_C:
        if v_cd in SP1_g1.keys() and  v_cd in SP1_g2.keys() and v_cd not in dominated_nodes:
            result[v_cd]=optimal_stable_js_to_cooperation_ending_node(G,V_C,v_cd,v_s1,v_g1,v_s2, v_g2)
            stable_paths=all_nodes_shortest_stable_partial_paths(G,V_C,v_cd, SP1_g1, SP1_g2)
            dominated_nodes|={node for node in stable_paths.keys() if not v_cd==node}
    br1=_best_response(G,V_C,v_s1,v_g1,SP1_s1,SP1_g1,SP1_s2[v_g2]['path'])
    br2=_best_response(G,V_C,v_s2,v_g2,SP1_s2,SP1_g2,SP1_s1[v_g1]['path'])
    if br1['path']!=SP1_s1[v_g1]['path'] or br2['path']!=SP1_s2[v_g2]['path']:
        for v in list(result.keys()):
            if (result[v][0]['path']==SP1_s1[v_g1]['path'] and  result[v][1]['path']==SP1_s2[v_g2]['path']):
                result.pop(v)   
    for v in dominated_nodes:
        if v in result:
            result.pop(v)
    return result


# find the social welfare optimal path for both players (the path that minimizes the sum of the path times for both players)
def social_welfare_optimal_path(G,V_C,v_s1,v_s2, v_g1, v_g2, eval):
    SP1_s1=shortest_paths(G,v_s1,'tau_1')
    SP1_s2=shortest_paths(G,v_s2,'tau_1')
    SP1_g1=shortest_paths(G,v_g1,'tau_1')
    SP1_g2=shortest_paths(G,v_g2,'tau_1')
    T_C_opt={}
    D_opt={}
    for v in V_C:
        T_C_opt[v]=max(SP1_s1[v]['length'], SP1_s2[v]['length'])#+G.nodes[v]['tau_2']
        D_opt[v]=eval(SP1_g1[v]['length'],SP1_g2[v]['length'])
    cooperation_starting_nodes=sorted(V_C, key=lambda v: T_C_opt[v])
    path1=SP1_s1[v_g1]
    path2=SP1_s2[v_g2]

    opt=eval(path1['length'],path2['length'])
    dominated=set()
    for v_cs in cooperation_starting_nodes:
        if(v_cs in dominated):
            continue
        SP2_cs=shortest_paths(G,v_cs,'tau_2')
        for v_ci in V_C:
            if T_C_opt[v_cs]+SP2_cs[v_ci]['length']<=T_C_opt[v_ci]:
                if(v_ci in cooperation_starting_nodes and not v_ci in dominated):
                    dominated.add(v_ci)
                    pass
                total_path_time=eval(T_C_opt[v_cs]+SP2_cs[v_ci]['length']+G.nodes[v_ci]['tau_2']+SP1_g1[v_ci]['length'], T_C_opt[v_cs]+SP2_cs[v_ci]['length']+G.nodes[v_ci]['tau_2']+SP1_g2[v_ci]['length'])
                if total_path_time<=opt:
                    opt=total_path_time
                    path_from_s1_to_cs=SP1_s1[v_cs]['path'].copy()
                    path_from_s2_to_cs=SP1_s2[v_cs]['path'].copy()
                    if SP1_s1[v_cs]['length']>SP1_s2[v_cs]['length']:
                        path_from_s2_to_cs.insert(-1,'WAIT_'+str( SP1_s1[v_cs]['length']-SP1_s2[v_cs]['length']))

                    elif SP1_s1[v_cs]['length']<SP1_s2[v_cs]['length']:
                        path_from_s1_to_cs.insert(-1,'WAIT_'+str(SP1_s2[v_cs]['length']-SP1_s1[v_cs]['length']))
                    
                    path1['path']=concat_paths([path_from_s1_to_cs,SP2_cs[v_ci]['path'],list(reversed(SP1_g1[v_ci]['path']))])
                    path1['length']=T_C_opt[v_cs]+SP2_cs[v_ci]['length']+G.nodes[v_ci]['tau_2']+SP1_g1[v_ci]['length']
                    path2['path']=concat_paths([path_from_s2_to_cs,SP2_cs[v_ci]['path'],list(reversed(SP1_g2[v_ci]['path']))])
                    path2['length']=T_C_opt[v_cs]+SP2_cs[v_ci]['length']+G.nodes[v_ci]['tau_2']+SP1_g2[v_ci]['length']
    return path1, path2, opt


# remove dominated joint paths (a joint path is dominated if there is another joint path that is better for both players)
def clear_dominated_joint_paths(paths):
    toRemove=set()
    for v1,p1 in paths.items():
        if v1 in toRemove:
            continue
        for v2,p2 in paths.items():
            if(v2==v1):
                continue
            if(p1[0]['length']<=p2[0]['length'] and p1[1]['length']<=p2[1]['length']):
                toRemove.update([v2])
    for v in toRemove:
        paths.pop(v)

# concatenate paths if they are connected (the last node of the first path is the same as the first node of the second path) and return None if they are not connected
def concat_paths(paths):
    result=[paths[0][0]]
    for p in paths:
        if len(p)>0:
            if result[-1]==p[0]:
                result+=p[1:]
            else:
                return None
    return result