import networkx as nx
import random
import bisect 



def generate_graph(m, k, n, e):
    G = nx.Graph()
    starting_nodes=[]
    target_nodes=[]
    cooperation_nodes=[]
    for i in range(k):
        G.add_node('s_{}'.format(i+1), tau_1=0, tau_2=0)
        G.add_node('g_{}'.format(i+1), tau_1=0, tau_2=0)
        starting_nodes.append(G.nodes['s_{}'.format(i+1)])
        target_nodes.append(G.nodes['g_{}'.format(i+1)])

    for i in range(m):
        t1=random.randint(0,20)
        G.add_node('v_{}'.format(i+1), tau_1=t1, tau_2=t1)

    for i in range(m):
        t2=random.randint(0,10)
        t1=random.randint(1,10)+t2
        G.add_node('c_{}'.format(i+1), tau_1=t1, tau_2=t2)
        cooperation_nodes.append(G.nodes['c_{}'.format(i+1)])

    nodes = list(G.nodes())
    while e > 0:
        u, v = random.sample(nodes, 2)
        if not G.has_edge(u, v):
            G.add_edge(u, v, tau=random.randint(1,20))
            e -= 1
    
    return G, starting_nodes, target_nodes, cooperation_nodes


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


def get_waits_included_graph(G, tau):
    G_mod = G.copy()
    for node in G.nodes:
        for neighbor in G.neighbors(node):
            if('visited' not in G_mod[node][neighbor]):
                G_mod[node][neighbor]['visited']=True
                G_mod[node][neighbor]['tau'] += G_mod.nodes[node][tau]
    return G_mod


def all_pairs_shortest_paths(G, tau):
    G_mod=get_waits_included_graph(G, tau)
    shortest_paths = dict(nx.all_pairs_dijkstra_path(G_mod,weight='tau'))
    shortest_path_lengths = dict(nx.all_pairs_dijkstra_path_length(G_mod,weight='tau'))
    return merge_paths_and_lengths(shortest_paths, shortest_path_lengths)


def shortest_paths(G, s, tau):
    G_mod=get_waits_included_graph(G, tau)

    shortest_paths = dict(nx.single_source_dijkstra_path(G_mod,s ,weight='tau'))
    shortest_path_lengths = dict(nx.single_source_dijkstra_path_length(G_mod, s, weight='tau'))
    return {key: {'path': shortest_paths[key], 'length': shortest_path_lengths[key]} for key in shortest_paths.keys()}


def manhatten_distance(p1, p2):
    return abs(p1[0]-p2[0])+abs(p1[1]-p2[1])

def evaluate_paths(G, path1, path2):
    t1=0
    t2=0
    node1=0
    node2=0
    minimal_manhatten_distance=float('inf')
  
    while(node1<len(path1) or node2<len(path2)):
        
        if(node1<len(path1)-1):
            if isinstance(path1[node1+1], str) and path1[node1+1].startswith("WAIT_"):
                next_node=node1+2
                # print("OOO")
            else:
                next_node=node1+1
            next1=t1+G.edges[(path1[node1],path1[next_node])]['tau']+G.nodes[path1[next_node]]['tau_1']
            if node1+2<len(path1) and isinstance(path1[node1+2], str) and path1[node1+2].startswith("WAIT_"):
                next1+=int(path1[node1+2][len("WAIT_"):])
            if node1+1<len(path1) and isinstance(path1[node1+1], str) and path1[node1+1].startswith("WAIT_") and node1==0:
                next1+=int(path1[node1+1][len("WAIT_"):])

        if(node2<len(path2)-1):
            next_node=(node2+1) if not (isinstance(path2[node2+1], str) and path2[node2+1].startswith("WAIT_")) else (node2+2)
            next2=t2+G.edges[(path2[node2],path2[next_node])]['tau']+G.nodes[path2[next_node]]['tau_1']
            if node2+2<len(path2) and isinstance(path2[node2+2], str) and path2[node2+2].startswith("WAIT_"):
                next2+=int(path2[node2+2][len("WAIT_"):])
            if(node2+1<len(path2) and isinstance(path2[node2+1], str) and path2[node2+1].startswith("WAIT_")) and node2==0:
                next2+=int(path2[node2+1][len("WAIT_"):])   


        if((next1<=next2 and node1<len(path1)) or node2==len(path2)):
            t1=next1
            node1+=1 if not (node1+1<len(path1) and isinstance(path1[node1+1], str) and path1[node1+1].startswith("WAIT_")) else 2
        else:
            t2=next2
            node2+= 1 if not (node2+1<len(path2) and isinstance(path2[node2+1], str) and path2[node2+1].startswith("WAIT_")) else 2
        
        if(node2<len(path2) and node1<len(path1) and path1[node1]==path2[node2]):
            if(abs(t2-t1)<G.nodes[path1[node1]]['tau_1']-G.nodes[path1[node1]]['tau_2']): # if(t2>t1 and abs(t2-t1)<G.nodes[path1[node1]]['tau_1']-G.nodes[path1[node1]]['tau_2']):
                t2=max(t2,t1)-G.nodes[path1[node1]]['tau_1']+G.nodes[path1[node1]]['tau_2']
                t1=t2
    return t1, t2


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


def optimal_ecjs(G,V_C, v_cd, v_s1, v_g1, v_s2, v_g2):
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


def find_optimal_stable_cooperation_path(G,V_C, s1,s2,g1,g2):
    SP1_s1=shortest_paths(G,s1,'tau_1')
    SP1_s2=shortest_paths(G,s2,'tau_1')
    SP1_g1=shortest_paths(G,g1,'tau_1')
    SP1_g2=shortest_paths(G,g2,'tau_1')

    SP2_s1=shortest_paths(G,s1,'tau_2')
    SP2_s2=shortest_paths(G,s2,'tau_2')

    potential_vds=[]
    for n in G.nodes:
        G.nodes[n]['t_star']=max(SP1_s1[n]['length'],SP1_s2[n]['length'])+G.nodes[n]['tau_2']
        G.nodes[n]['d_star']=max(SP1_g1[n]['length'],SP1_g2[n]['length'])
        if(G.nodes[n]['tau_1']>G.nodes[n]['tau_2']):
            potential_vds.append(n)
    potential_vds=sorted(potential_vds, key= lambda v: G.nodes[v]['d_star'])

    T1_opt=float('inf')
    T2_opt=float('inf')
    while potential_vds:
        vd=potential_vds.pop(0)
        paths, T1, T2, stable_nodes=a_star_evaluate(G,vd,SP1_s1, SP1_s2, SP1_g1, SP1_g2, SP2_s1, SP2_s2)
        potential_vds=[i for i in potential_vds if i not in stable_nodes]
        if(max(T1,T2)<max(T1_opt,T2_opt)):
            T1_opt=T1
            T2_opt=T2
            optimal_paths=paths    
    return optimal_paths, T1, T2


def best_response(G,V_C,v_s1,v_g1,path2):
    SP1_s1=shortest_paths(G,v_s1,'tau_1')
    SP1_g1=shortest_paths(G,v_g1,'tau_1')
    return _best_response(G,V_C,v_s1,v_g1,SP1_s1, SP1_g1, path2)


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


def shortest_independent_path(G,v_s,v_g):
    return shortest_paths(G,v_s,'tau_1')[v_g]

def shortest_cooperated_path(G,v_s,v_g):
    return shortest_paths(G,v_s,'tau_2')[v_g]


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
            result[v_cd]=optimal_ecjs(G,V_C,v_cd,v_s1,v_g1,v_s2, v_g2)
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


def concat_paths(paths):
    result=[paths[0][0]]
    for p in paths:
        if len(p)>0:
            if result[-1]==p[0]:
                result+=p[1:]
            else:
                return None
    return result



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
    v_cs_opt=None
    v_cd_opt=None
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
                    # cooperation_starting_nodes.remove(v_ci)
                    pass
                # total_path_time=2*(T_C_opt[v_cs]+SP2_cs[v_ci]['length']+v_ci['tau_2'])+D_opt[v_ci]
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


def clear_dominated_joint_paths(paths):
    keys=enumerate(list(paths.keys()))
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
    # for i, p in keys:
    #         if(i==0):
    #             continue



    #         p2=paths[v2]
    #         if(p1[0]['length']>=p2[0]['length'] and p1[1]['length']>=p2[1]['length']):
    #             paths.pop(v2)
    #             k.remove(v2)


#   DEPRECATED

def expand_path(pi, SP1_s1, SP1_s2, SP1_g1, SP1_g2):
    if not pi:
        return SP1_s1['g_1']['path'], SP1_s2['g_g']['path']
    vs=pi[0]
    vd=pi[len(pi)-1]
    return SP1_s1[vs]['path'][:len(SP1_s1[vs]['path'])-1]+pi+SP1_g1[vd]['path'][::-1][1:], SP1_s2[vs]['path'][:len(SP1_s1[vs]['path'])-1]+pi+SP1_g2[vd]['path'][::-1][1:]


def a_star_evaluate(G, vd, SP1_s1, SP1_s2, SP1_g1, SP1_g2, SP2_s1, SP2_s2):
    open_nodes=[vd, 'end']
    closed_nodes=[]
    h={key:{'s_1':SP2_s1[key]['length'],'s_2':SP2_s2[key]['length']} for key in SP2_s1.keys()}
    h['end']={'s_1':0,'s_2':0}
    
    g={vd:{'g_1':SP1_g1[vd]['length']+G.nodes[vd]['tau_2'],'g_2':SP1_g2[vd]['length']+G.nodes[vd]['tau_2']}}  
    g['end']={'g_1':SP1_s1['g_1']['length'],'g_2':SP1_s2['g_2']['length']}
    
    f={key:{'r_1':h[key]['s_1']+g[key]['g_1'],'r_2':h[key]['s_2']+g[key]['g_2']} for key in g.keys()}
    path={vd:[], 'end': []}
    stable_nodes=[]
      
    while open_nodes:
        v=open_nodes.pop(0)
        closed_nodes.append(v)
        if(v=='end'):
            return expand_path(path['end'], SP1_s1, SP1_s2, SP1_g1, SP1_g2), f['end']['r_1'], f['end']['r_2'], stable_nodes
              
       
        tentative_end={'g_1':g[v]['g_1']+SP1_s1[v]['length'], 'g_2':g[v]['g_2']+SP1_s2[v]['length']}
        if(max(g['end']['g_1'],g['end']['g_2'])>=max(tentative_end['g_1'],tentative_end['g_2'])):
            g['end']=tentative_end
            f['end']={'r_1':g['end']['g_1'],'r_2':g['end']['g_2']}
            path['end']=[v]+path[v]
            bisect.insort(open_nodes,'end',key=lambda x:max(f[x]['r_1'],f[x]['r_2']))
        
        neighbors=G.neighbors(v) 
        for n in neighbors:
            if n not in closed_nodes and SP1_g1[n]['length']>=g[v]['g_1']+G[v][n]['tau'] and SP1_g2[n]['length']>=g[v]['g_2']+G[v][n]['tau']:
                if(G.nodes[n]['tau_2']<G.nodes[n]['tau_1']):
                    stable_nodes.append(n)
                tentative_g={'g_1':g[v]['g_1']+G[v][n]['tau']+G.nodes[n]['tau_2'],'g_2':g[v]['g_2']+G[v][n]['tau']+G.nodes[n]['tau_2']}
                if(n not in g or (n in g and max(g[n]['g_1'],g[n]['g_2'])>=max(tentative_g['g_1'],tentative_g['g_2']))):
                    g[n]=tentative_g
                    path[n]=[v]+path[v]
                    f[n]={'r_1':g[n]['g_1']+h[n]['s_1'],'r_2':g[n]['g_2']+h[n]['s_2']}
                    bisect.insort(open_nodes,n,key=lambda x:max(f[x]['r_1'],f[x]['r_2']))


def independent_path_time(G,path):
    path_time=0
    for i in range(len(path)-1):
        if(isinstance(path[i+1],str) and path[i+1].startswith('WAIT_')):
            path_time+=G.nodes[path[i]]['tau_1']+int(path[i+1][len('WAIT_'):])+G[path[i]][path[i+2]]['tau']
        elif(isinstance(path[i],str) and path[i].startswith('WAIT_')):
            pass
        else:
            path_time+=G.nodes[path[i]]['tau_1']+G[path[i]][path[i+1]]['tau']
    
    return path_time
    

if __name__ == "__main__":
    # G=geneate_graph_from_mat('johnson8-2-4/johnson8-2-4.mtx')
    # # G = nx.read_gml("2.gml")
    # V_C=[n for n in G.nodes if G.nodes[n]['tau_1']>G.nodes[n]['tau_2']]
    # SP1_s2=shortest_paths(G,'s_2','tau_1')
    # SP1_g1=shortest_paths(G,'g_1','tau_1')
    # SP1_g2=shortest_paths(G,'g_2','tau_1')
    # # print(SP1_g1)
    # # # print(SP1_g2)
    # # # print(G['c_1']['g_2']['tau'])
    # # paths=all_nodes_shortest_non_cooperative_partial_paths(G,V_C,'s_1', SP1_s2)
    # # print(paths)
    # # paths=all_nodes_shortest_stable_partial_paths(G,V_C,'c_2',SP1_g1, SP1_g2)
    # # print(paths)
    # # paths=optimal_ecjs(G,V_C,'v_3','s_1','g_1','s_2','g_2')
    # # print(paths)
    # # path=best_response(G,V_C,'s_2','g_2',SP1_s2, SP1_g2, paths[0]['path'])
    # # # print(path)
    # paths=map_optimal_ecjs(G,V_C,'s_1','s_2','g_1','g_2')
    # # print(paths)
    # clear_dominated_joint_paths(paths)
    # for p in paths.values():
    #     print(p)
    


        # if(len(paths)>0):
        #     for p in paths.values():
        #         print(_,p)
    # optimal_paths, T1, T2=find_optimal_stable_cooperation_path(G, V_C, 's_1','s_2','g_1','g_2')
    # pos={'s_1': np.array([0,  1]), 's_2': np.array([0,-1]), 'g_1': np.array([4,  1]), 'g_2': np.array([4, -1]), 'c_1': np.array([1, 0]), 'c_2': np.array([2,  0]), 'c_3': np.array([3, 0]), 'a': np.array([ 2, -1 ])}
    # visualization.visualize(G,pos,optimal_paths)
    pass