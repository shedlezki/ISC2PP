import networkx as nx
import icmpp
import gui
import random
from scipy.io import mmread
import mapfBenchmarkProvider
import csv
import argparse
import concurrent.futures
import time
import pickle
import uuid
import bargaining_solutions 
import visualization
import os
ARCHIVE_PATH='../archive'
RESULTS_PATH='../final_results2/'
dataset=['johnson8-2-4.mtx','road-chesapeake.mtx','road-euroroad.edges','Berlin_1_256.map']

path_to_graphs_folder='../graphs'

def generate_weights(G):
    labels={}
    for n in G.nodes():
        labels[n]=f'v_{n}'
    v_s1, v_s2, v_g1, v_g2=random.sample(list(G.nodes()),k=4)
    labels[v_s1]='s_1'
    labels[v_s2]='s_2'
    labels[v_g1]='g_1'
    labels[v_g2]='g_2'
    G = nx.relabel_nodes(G, labels)
    for node in G.nodes():
        if(node=='s_1' or node=='s_2' or node=='g_1' or node=='g_2'):
            t1=0
            t2=0      
        elif random.choice([True,False]):
            t1=random.randrange(10)
            t2=random.randrange(10)
        else:
            t1=random.randrange(10)
            t2=t1
        G.nodes[node]['tau_1']=max(t1,t2)
        G.nodes[node]['tau_2']=min(t1,t2)
    for u, v, data in G.edges(data=True):
        data['tau']=random.randrange(10)
    return G


# def provide_graph():
#     # graph_file=random.choice(dataset)
#     graph_file=dataset[-1]
#     path=f'{path_to_graphs_folder}/{graph_file}'
#     if graph_file.endswith('mtx'):
#         a = mmread(path)
#         return generate_weights(nx.Graph(a))
#     elif graph_file.endswith('gml'):
#          return nx.read_gml(path)
#     elif graph_file.endswith('edges'):
#         return generate_weights(nx.read_edgelist(path, nodetype=int))
#     elif graph_file.endswith('map'):
#         G, pos, grid=grid2graph.read_map_file(path)
#         G=generate_weights(G)
#         return G, pos, grid

def social_avg(ptime1, ptime2):
    return (ptime1+ptime2)/2

def social_welfare(ptime1, ptime2):
    return (ptime1+ptime2)  

def greedy(joint_path, sp, G):
    return joint_path[0]['length']

def altroist(joint_path, sp, G):
    return joint_path[1]['length']

def max_min_surplus(joint_path, sp, G):
    return -min(sp[0]['length']-joint_path[0]['length'],sp[1]['length']-joint_path[1]['length'])

def max_max_surplus(joint_path, sp, G):
    return -max(sp[0]['length']-joint_path[0]['length'],sp[1]['length']-joint_path[1]['length'])

def max_sum_surplus(joint_path, sp, G):
    return -(sp[0]['length']-joint_path[0]['length']+sp[1]['length']-joint_path[1]['length'])

def max_avg_surplus(joint_path, sp, G):
    return -(sp[0]['length']-joint_path[0]['length']+sp[1]['length']-joint_path[1]['length'])/2


def min_min(joint_path, sp, G):
    return min(joint_path[0]['length'],joint_path[1]['length'])

def min_max(joint_path, sp, G):
     return max(joint_path[0]['length'],joint_path[1]['length'])

def min_sum(joint_path, sp, G):
    return joint_path[0]['length']+joint_path[1]['length']

def min_avg(joint_path, sp, G):
    return (joint_path[0]['length']+joint_path[1]['length'])/2

def min_abs(joint_path, sp, G):
    return abs(joint_path[0]['length']-joint_path[1]['length'])

def sp_min(joint_path, sp, G):
    return icmpp.evaluate_paths(G,joint_path[0]['path'],joint_path[1]['path'])

def max_min_improvement(joint_path, sp, G):
    improvement1=(sp[0]['length']-joint_path[0]['length'])/sp[0]['length']
    improvement2=(sp[1]['length']-joint_path[1]['length'])/sp[1]['length']
    return -min(improvement1,improvement2)

def max_avg_improvement(joint_path, sp, G):
    improvement1=(sp[0]['length']-joint_path[0]['length'])/sp[0]['length']
    improvement2=(sp[1]['length']-joint_path[1]['length'])/sp[1]['length']
    return -(improvement1+improvement2)/2


def gain_risk_metric(path, sp, G):
    gain=(sp['length']-path['length'])
    risk=(icmpp.independent_path_time(G, path['path'])-sp['length'])
    if risk==0:
        return float('inf')
    return gain/risk

def max_gain_for_risk(joint_path, sp, G):
    return -gain_risk_metric(joint_path[0],sp[0],G)
    

def max_min_gain_for_risk(joint_path, sp, G):
    gr_1=gain_risk_metric(joint_path[0],sp[0],G)
    gr_2=gain_risk_metric(joint_path[1],sp[1],G)
    return -min(gr_1,gr_2)

def max_nash_value(joint_path, sp, G):
    return -(sp[0]['length']-joint_path[0]['length'])*(sp[1]['length']-joint_path[1]['length'])

def min_nash_value(joint_path, sp, G):
    return (sp[0]['length']-joint_path[0]['length'])*(sp[1]['length']-joint_path[1]['length'])

def social_avg(ptime1, ptime2):
    return (ptime1+ptime2)/2

def social_welfare(ptime1, ptime2):
    return (ptime1+ptime2)

def social_min_max(ptime1, ptime2):
    return max(ptime1,ptime2)

def social_min_min(ptime1, ptime2):
    return max(ptime1,ptime2)



# if __name__ == "__main2__":
#     G, pos, grid=mapfBenchmarkProvider.get_graph('empty-8-8','even-1')
#     V_C=[n for n in G.nodes if G.nodes[n]['tau_1']>G.nodes[n]['tau_2']]
#     paths=icmpp.map_optimal_ecjs(G,V_C,'s_1','s_2','g_1','g_2')
#     icmpp.clear_dominated_joint_paths(paths)
   
#     paths=list(paths.values()) 
#     print(len(paths))
#     for p in paths:
#         print('p1:',p[0])
#         print('p2:',p[1])
#     visualization.visualize(G,pos,paths[0], grid)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m','--map', type=str, required=False, default="empty-8-8", help="Map name")
    parser.add_argument('-s','--scenario', type=str, required=False, help="Scenario name")
    parser.add_argument('-d','--density', type=float, required=False, default=0.5, help="Density value")
    parser.add_argument('-mt','--magnitude', type=int, required=False, default=10, help="Magnitude value")
    parser.add_argument('-e','--extent', type=int, required=False, default=15, help="Extent value")
    parser.add_argument('-c','--correlation', type=int, required=False, default=4, help="Correlation value")
    parser.add_argument('-i','--iterations', type=int, required=False, default=1, help="Number of iterations")
    parser.add_argument('-o','--output', type=str, required=False, default="results", help="Output file name")
    parser.add_argument('-v','--visualization',action='store_true', help="Visualize the scenario")
    parser.add_argument('-l','--load',type=str, required=False, help="Experiment file to load")
    parser.add_argument('-r','--rerun',type=str, required=False, help="Rerun full experiment (given a csv file)")
    parser.add_argument('-si','--size',type=str, required=False, help="Map size")


    return parser.parse_args()



def get_random_map_by_size(size):
    folder_path=path_to_graphs_folder+"/mapf-map/mapf-by-size/"+size
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if not files:
        return None  # or raise an error
    selected_file = random.choice(files)
    basename, _ = os.path.splitext(selected_file)
    return "mapf-by-size/"+size+"/"+basename


def get_graph_with_timeout(map_name,scenario_name, density, magnitude, correlation, extent, timeout=1, size=None):
    if size is not None:
        map_name=get_random_map_by_size(size)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        while True:
            future = executor.submit(
                mapfBenchmarkProvider.get_graph,
                map_name, scenario_name,
                ratio=density,
                coopertion_strength=magnitude,
                distance=correlation,
                length=extent,
                cooperation_setup=scenario_name!=None
            )
            try:
                G, pos, grid = future.result(timeout=timeout)  # wait 1 sec
                return G, pos, grid, map_name
            except concurrent.futures.TimeoutError:
                print("Timeout! Retrying...")
                time.sleep(0.1)  # optional small wait


def get_eid_values(csv_filename):
    eid_values = []
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        if "EID" not in reader.fieldnames:
            raise ValueError("Column 'EID' not found in the CSV file.")
        for row in reader:
            if(row["EID"] not in eid_values):
                eid_values.append(row["EID"])
    return eid_values


evaluators={"Greedy":greedy,"Altroist":altroist, "Max_G/R": max_gain_for_risk, "Min-Min":min_min, "Min-Max":min_max, "Min-Sum":min_sum, "Min-Avg":min_avg, "Min-Abs":min_abs, "Max-Min-Improvement": max_min_improvement, "Max-Avg-Improvement": max_avg_improvement, "Max-Min-G/R": max_min_gain_for_risk, "MAX-Nash-Value":max_nash_value,"MIN-Nash-Value":min_nash_value, "Max-Avg-Surplus":max_avg_surplus, "Max-Min-Surplus":max_min_surplus, "Max-Max-Surplus":max_max_surplus, "MIN-Sum-Surplus":max_sum_surplus}
evaluators={"Min-Min":min_min, "Min-Max":min_max, "Min-Sum":min_sum, "Min-Avg":min_avg, "Min-Abs":min_abs, "Max-Min-Surplus":max_min_surplus,"Max-Min-Improvement": max_min_improvement, "Max-Avg-Improvement": max_avg_improvement, "MAX-Nash-Value":max_nash_value,"MIN-Nash-Value":min_nash_value, "MIN-Sum-Surplus":max_sum_surplus}

social_evaluators={"Social Sum": social_welfare} # ,"Social Avg": social_avg,"Social Min-Min": social_min_min,"Social Min-Max": social_min_max}

greedy_evaluators=["Greedy","Altroist","Max_G/R"]

values=non_greedy_keys = set(evaluators) - set(greedy_evaluators)


def run_social_experiemnt(G, pos, grid):
    V_C=[n for n in G.nodes if G.nodes[n]['tau_1']>G.nodes[n]['tau_2']]
    results=[]
    for description, eval in social_evaluators.items():
        result=icmpp.social_welfare_optimal_path(G,V_C,'s_1','s_2','g_1','g_2',eval)
        results.append(result)
    return results


def run_experiment(G, pos, grid, eid, solver, map):
    V_C=[n for n in G.nodes if G.nodes[n]['tau_1']>G.nodes[n]['tau_2']]
                
    paths=icmpp.map_optimal_ecjs(G,V_C,'s_1','s_2','g_1','g_2')
    SP1,SP2=(icmpp.shortest_independent_path(G,'s_1','g_1'),icmpp.shortest_independent_path(G,'s_2','g_2'))
    SP21, SP22=(icmpp.shortest_cooperated_path(G,'s_1','g_1'),icmpp.shortest_cooperated_path(G,'s_2','g_2'))
    manhatten_div, path_time_div=calculate_divergance(G,SP1,SP2)
   

    BR1=icmpp.best_response(G,V_C,'s_1','g_1',SP2['path'])
    BR2=icmpp.best_response(G,V_C,'s_2','g_2',SP1['path'])
    is_sp_pne=BR1['length']==SP1['length'] and BR2['length']==SP2['length']
      
    social_paths=run_social_experiemnt(G,pos,grid)
    data={"grid":grid, "graph":G, "pos":pos, "paths":paths,"args":args, "social_paths":social_paths, "map":map}
    with open(f'{ARCHIVE_PATH}/{eid}.pkl', 'wb') as f:
        pickle.dump(data, f)

    p_before=list(paths.values())
    icmpp.clear_dominated_joint_paths(paths)
    paths=list(paths.values()) 


    if(len(paths)==0):
        print()
        print(eid)
    if(len(paths)>1 or True):
        paths2=[(x,y) for (y,x) in paths]
        Potential=[(p[0]['length'],p[1]['length']) for p in paths]
        reversed_potential=[(x,y) for (y,x) in Potential]
        SP=icmpp.evaluate_paths(G,SP1['path'],SP2['path'])
        final_row1=[eid,manhatten_div,path_time_div,is_sp_pne,Potential, SP1['length'], SP2['length'],SP21['length'],SP22['length'], SP[0],social_paths[0][0]['length'],social_paths[0][2]]
        final_row2=[eid,manhatten_div,path_time_div,is_sp_pne,reversed_potential, SP2['length'], SP1['length'],SP22['length'],SP21['length'], SP[1],social_paths[0][1]['length'],social_paths[0][2]]
        row1=[eid,is_sp_pne,Potential, SP1['length'], SP[0]]
        row2=[eid,is_sp_pne,reversed_potential, SP2['length'], SP[1]]
        social_values=[tuple[2] for tuple in social_paths]
        for description, eval in evaluators.items():
            result=icmpp.evaluate_paths(G,min(paths,key=lambda p:eval(p,(SP1,SP2), G))[0]['path'],min(paths2,key=lambda p: eval(p,(SP2,SP1), G))[0]['path'])
            final_row1.append(result[0]+result[1])
            final_row1.append(result[0])

            final_row2.append(result[0]+result[1])
            final_row2.append(result[1])

            row1.append(result[0])
            row2.append(result[1])
            # if(description not in greedy_evaluators):
            #     for v in values:
            #         m=[min(paths,key=lambda p:eval(p,(SP1,SP2), G)),min(paths2,key=lambda p: eval(p,(SP2,SP1), G))]
            #         e=[evaluators[v](m[0],(SP1,SP2), G),evaluators[v](m[1],(SP2,SP1), G)]
            #         row1.append(e[0])
            #         row2.append(e[1])
        
        # social_values=[tuple[2] for tuple in social_paths]
        row1.extend(social_values)
        row2.extend(social_values)
        sol1=solver.find_bargaining_solutions(Potential,  SP1['length'],SP2['length'], SP)
        
        poa=price_of_anarchy(Potential, social_paths[0][2], SP1['length'],SP2['length'])
        pos=price_of_stability(Potential, social_paths[0][2], SP1['length'],SP2['length'])

        sol2=solver.find_bargaining_solutions(reversed_potential,  SP2['length'], SP1['length'], reversed(SP))
        row1.extend([sol1['nash_point'], sol1['nash_ratio'],sum(sol1['nash_point']), sol1['ks_point'], sol1['ks_ratio'],sum(sol1['ks_point']), sol1['egal_point'], sol1['egal_ratio'],sum(sol1['egal_point']), sol1['util_point'], sol1['util_ratio'],sum(sol1['util_point'])])
        row2.extend([sol2['nash_point'], sol2['nash_ratio'],sum(sol2['nash_point']), sol2['ks_point'], sol2['ks_ratio'],sum(sol2['ks_point']), sol2['egal_point'], sol2['egal_ratio'],sum(sol2['egal_point']), sol2['util_point'], sol2['util_ratio'],sum(sol2['util_point'])])
        row1.extend([poa,pos])
        row2.extend([poa,pos])
        final_row1.extend([SP1['length']+SP2['length']-sum(sol1['nash_point']),SP1['length']-sol1['nash_point'][0],SP1['length']+SP2['length']-sum(sol1['ks_point']),SP1['length']-sol1['ks_point'][0],SP1['length']+SP2['length']-sum(sol1['egal_point']),SP1['length']-sol1['egal_point'][0],SP1['length']+SP2['length']-sum(sol1['util_point']),SP1['length']-sol1['util_point'][0]])
        final_row2.extend([SP1['length']+SP2['length']-sum(sol2['nash_point']),SP2['length']-sol2['nash_point'][0],SP1['length']+SP2['length']-sum(sol2['ks_point']),SP2['length']-sol2['ks_point'][0],SP1['length']+SP2['length']-sum(sol2['egal_point']),SP2['length']-sol2['egal_point'][0],SP1['length']+SP2['length']-sum(sol2['util_point']),SP2['length']-sol2['util_point'][0]])
        
        # final_row2.extend([(SP1['length']+SP2['length']-social_paths[0][2])/sum(sol2['nash_point']),sol2['nash_point'][0],(SP1['length']+SP2['length']-social_paths[0][2])/sum(sol2['ks_point']),sol2['ks_point'][0],(SP1['length']+SP2['length']-social_paths[0][2])/sum(sol2['egal_point']),sol2['egal_point'][0],(SP1['length']+SP2['length']-social_paths[0][2])/sum(sol2['util_point']),sol2['util_point'][0]])

        final_row1.extend([poa,pos])
        final_row2.extend([poa,pos])

        
    return row1, row2, paths, social_paths, final_row1, final_row2


def price_of_anarchy(potential, optimal_sw, SP1, SP2):
    worst_eq=max(potential, key=lambda p: p[0]+p[1])
    worst_eq_sw=worst_eq[0]+worst_eq[1]
    return (optimal_sw)/float(worst_eq_sw)

def price_of_stability(potential, optimal_sw, SP1, SP2):
    best_eq=min(potential, key=lambda p: p[0]+p[1])
    best_eq_sw=best_eq[0]+best_eq[1]
    return (optimal_sw)/float(best_eq_sw)  

def rerun_full_experiment(input_fname, writer, solver, final_writer):
    eids=get_eid_values(input_fname)

    for i,eid in enumerate(eids):
        percent = (i) / len(eids) * 100
        bar = ('#' * int(percent // 2)).ljust(50)  # 50 characters wide
        print(f"\rProgress: |{bar}| {percent:.1f}% ({i+1}/{len(eids)}) complete", end="")
        with open(f'{ARCHIVE_PATH}/{eid}.pkl', 'rb') as f:
            loaded_data = pickle.load(f)
            G=loaded_data["graph"]
            grid=loaded_data["grid"]
            pos=loaded_data["pos"]
            paths=loaded_data["paths"]
            args=loaded_data["args"]
        row1, row2,paths, social_paths, final_row1, final_row2=run_experiment(G, pos, grid, eid, solver)
        writer.writerow(row1)
        writer.writerow(row2)
        final_writer.writerow(final_row1)
        final_writer.writerow(final_row2)
    return G, grid, pos, paths, social_paths, eid


def get_node_cell(G, state):
    if(state[0]=='E'):
        node=state[1][0]
    elif(state[0]=='T' or state[0]=='F' or state[0]=='C' or state[0]=='W'):
        node=state[1]
    else:
        node=(0,0)
    
    return (0,0),node

    # if(',' not in node):
    #     neighbors={tuple(map(int, n.strip('$()').split(','))) for n in set(G.neighbors(node))}
    #     xs = sorted(x for x, _ in neighbors)
    #     ys = sorted(y for _, y in neighbors)
    #     mid_x = xs[len(xs)//2]
    #     mid_y = ys[len(ys)//2]
    #     return (mid_x, mid_y), node
    # else:
    #     return tuple(map(int, node.strip('$()').split(','))), node


def calculate_divergance(G,path1, path2):
    G=visualization.relabel_nodes(G)
    all_pairs_sp1=icmpp.all_pairs_shortest_paths(G,'tau_1')
    p1,p2=visualization.relabel_path(path1['path']),visualization.relabel_path(path2['path'])
    state1, state2=visualization.interpolate_paths(G,p1,p2)
    minimal_manhatten_distance=float('inf')
    minimal_path_time=float('inf')
    for i in range(max(len(state1),len(state2))):
        if(i>=len(state1)):
            state1.append(state1[-1])
        if(i>=len(state2)):
            state2.append(state2[-1])
       
        ((n1, node1), (n2, node2))=get_node_cell(G,state1[i]),get_node_cell(G,state2[i])
        d=icmpp.manhatten_distance(n1,n2)
        path_time=all_pairs_sp1[node1][node2]['length']

        # print(state1[i],"-----",state2[i],': ',d,path_time)
        if(path_time<minimal_path_time):
            minimal_path_time=path_time
        if(d<minimal_manhatten_distance):
            minimal_manhatten_distance=d
    # print("Minimal manhatten distance:", minimal_manhatten_distance)
    # print("Minimal path time:", minimal_path_time)
    return minimal_manhatten_distance, minimal_path_time

def run_full_experiment(args, writer, solver, final_writer):
    G, grid, pos, paths, social_paths, eid=None, None, None, None, None, None
    for _ in range(args.iterations):
                # G = nx.read_gml("2.gml")

        eid = uuid.uuid4()
        percent = (_) / args.iterations * 100
        bar = ('#' * int(percent // 2)).ljust(50)  # 50 characters wide
        print(f"\rProgress: |{bar}| {percent:.1f}% ({_}/{args.iterations}) complete", end="")
        

        G, pos, grid, map = get_graph_with_timeout(args.map, args.scenario, args.density, args.magnitude, args.correlation, args.extent, 3, args.size)
        # print(G.nodes['s_1'], G.nodes['s_2'], G.nodes['g_1'], G.nodes['g_2'])
        # G, pos, grid=mapfBenchmarkProvider.get_graph(args.map,'even-1',ratio=args.density, coopertion_strength=args.magnitude, distance=args.correlation, length=args.extent, cooperation_setup=False)
        
        row1,row2, paths, social_paths, final_row1, final_row2=run_experiment(G, pos, grid, eid, solver, map)
        if len(paths)>1:
            writer.writerow(row1)
            writer.writerow(row2)
            final_writer.writerow(final_row1)
            final_writer.writerow(final_row2)
    return G, grid, pos, paths, social_paths, eid

if __name__ == "__main__":
   
    args = parse_args()

    if not args.load is None:
        eid=args.load
        with open(f'{ARCHIVE_PATH}/{args.load}.pkl', 'rb') as f:
            show=args.visualization
            loaded_data = pickle.load(f)
            G=loaded_data["graph"]
            grid=loaded_data["grid"]
            pos=loaded_data["pos"]
            paths=loaded_data["paths"]

            social_paths=None
            # social_paths=loaded_data['social_paths']
            args=loaded_data["args"]
            args.visualization=show
        icmpp.clear_dominated_joint_paths(paths)
        paths=list(paths.values()) 

    else:
        with open(RESULTS_PATH+args.output+".txt", mode='w', newline='') as file:
            file.write(str(args)+"\n")
            file.write(f"Date: {time.ctime()}\n")
            file.write(f"Archive path: {ARCHIVE_PATH}\n")
            file.write(f"Evaluators: {list(evaluators.keys())}\n")
            file.write(f"Social Evaluators: {list(social_evaluators.keys())}\n")
            file.write("\n")
        
        with open(RESULTS_PATH+args.output+"_final.csv", mode='w', newline='') as final_file:
            final_writer = csv.writer(final_file)
            final_writer.writerow(["eid","manhatten_div","path_time_div","is_sp_pne","Potential", "SP1(1)", "SP(2)","SP2(1)","SP2(2)", "SP1|SP2", "Individual Time In Optimal Social Welfare","Optimal Social Welfare", ]+[item for k in evaluators.keys() for item in (f"{k}", f"Individual Time In {k}")] +['Nash', 'Individual Time In Nash',
 'Kalai', 'Individual Time In Kalai',
 'Egalitarian', 'Individual Time In Egalitarian',
 'Utilitarian', 'Individual Time In Utilitarian',"PoA","PoS"])

        
            with open(RESULTS_PATH+args.output+".csv", mode='w', newline='') as file:
                    writer = csv.writer(file)
                    headers=[]
                    for e in evaluators:
                        if e in greedy_evaluators:
                            headers.append(e)
                        else:
                            headers.append(e)
                            # for v in values:
                            #    headers.append((e+" - "+v))
                    # print( headers)    
                    # headers = [key if key in greedy_evaluators else [key, key] for key in evaluators]
                
                    # headers = [item for sublist in headers for item in (sublist if isinstance(sublist, list) else [sublist])]

                    writer.writerow(["EID","SP1 is PNE" ,"Potential", "SP1", "SP1|SP1"]+list(headers)+list(social_evaluators.keys())+["Nash","Nash-Ratio","Nash-Value","Kalai","Kalai-Ratio","Kalai-Value","Egalitarian","Egalitarian-Ratio","Egalitarian-Value","Utilitarian","Utilitarian-Ratio","Utilitarian-Value", "PoS", "PoA"])

                    solver = bargaining_solutions.MATLABBargainingSolutions()

                    if not args.rerun is None:
                        input=args.rerun+".csv"
                        G, grid, pos, paths, social_paths, eid=rerun_full_experiment(input, writer, solver, final_writer)
                    
                    else:
                        G, grid, pos, paths, social_paths, eid=run_full_experiment(args, writer, solver, final_writer)

                    del solver

                    # SP=icmpp.evaluate_paths(G,SP1['path'],SP2['path'])
                    # Greedy=icmpp.evaluate_paths(G,min(paths,key=greedy)[0]['path'],min(paths2,key=greedy)[0]['path'])
                    # Altroist=icmpp.evaluate_paths(G,min(paths,key=altroist)[0]['path'],min(paths2,key=altroist)[0]['path'])
                    # MinMin=icmpp.evaluate_paths(G,min(paths,key=min_min)[0]['path'],min(paths2,key=min_min)[0]['path'])
                    # MinMax=icmpp.evaluate_paths(G,min(paths,key=min_max)[0]['path'],min(paths2,key=min_max)[0]['path'])
                    # MinSum=icmpp.evaluate_paths(G,min(paths,key=min_sum)[0]['path'],min(paths2,key=min_sum)[0]['path'])
                    # MinAvg=icmpp.evaluate_paths(G,min(paths,key=min_avg)[0]['path'],min(paths2,key=min_avg)[0]['path'])
                    # MinAbs=icmpp.evaluate_paths(G,min(paths,key=min_abs)[0]['path'],min(paths2,key=min_abs)[0]['path'])
                    # Line=[SP,Greedy,Altroist, MinMin,MinMax, MinSum, MinAvg,MinAbs]
                    # Lines.a


                    # paths2=[(x,y) for (y,x) in paths]
                    # print(_,"Potential:",[(p[0]['length'],p[1]['length']) for p in paths])
                    # print(_,"SP:",icmpp.evaluate_paths(G,SP1['path'],SP2['path']))
                    # print(_,"Greedy:",Greedy)
                    # print(_,"Altroist:",Altroist)
                    # print(_,"Min-Min:",MinMin)
                    # print(_,"Min-Max:",MinMax)
                    # print(_,"Min-Sum:",MinSum)
                    # print(_,"Min-Avg:",MinAvg)
                    # print(_,"Min-Abs:",MinAbs)
                    # # print(_,"SP-Min:",icmpp.evaluate_paths(G,min(paths,key=lambda x: sp_min(G, x))[0]['path'],min(paths2,key=lambda x: sp_min(G, x))[0]['path']))
                # elif paths[0] != None:
                #     print(paths)
                #         print(_,p[0]['length'],p[1]['length'])
   
    if args.visualization:
        SP1,SP2=(icmpp.shortest_independent_path(G,'s_1','g_1'),icmpp.shortest_independent_path(G,'s_2','g_2'))
        V_C=[n for n in G.nodes if G.nodes[n]['tau_1']>G.nodes[n]['tau_2']]         
        BR1,BR2=(icmpp.best_response(G,V_C,'s_1','g_1',SP2['path']),icmpp.best_response(G,V_C,'s_2','g_2',SP1['path']))
        

        g=gui.GUI(G,pos,grid, paths,social_paths, args, eid, (SP1,SP2), (SP1,BR2))
        g.show()



