from email import parser
import os

import isc2pp
import csv
import argparse
import time
import pickle
import uuid
import bargaining_solutions 
from iscpp_simulator import gui
from iscpp_simulator import mapf_benchmark_provider
from iscpp_simulator import simulation
import evaluation_functions
ARCHIVE_PATH='../archive'
RESULTS_PATH='../results/'
dataset=['johnson8-2-4.mtx','road-chesapeake.mtx','road-euroroad.edges','Berlin_1_256.map']


# parse arguments
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-m','--map', type=str, required=False, default="empty-8-8", help="Map name")
    parser.add_argument('-s','--scenario', type=str, required=False, help="Scenario name")
    parser.add_argument('-d','--density', type=float, required=False, default=0.5, help="Density value")
    parser.add_argument('-mt','--magnitude', type=int, required=False, default=10, help="Magnitude value")
    parser.add_argument('-e','--extent', type=int, required=False, default=15, help="Extent value")
    parser.add_argument('-se','--seperation', type=int, required=False, default=4, help="Seperation value")
    parser.add_argument('-i','--iterations', type=int, required=False, default=1, help="Number of iterations")
    parser.add_argument('-o','--output', type=str, required=False, default="results", help="Output file name")
    parser.add_argument('-de','--description', type=str, required=False, help="Description file name")
    parser.add_argument('-v', '--visualization', action='store_true', help="Visualize the scenario")
    parser.add_argument('-l','--load',type=str, required=False, help="Experiment file to load")
    parser.add_argument('-r','--rerun',type=str, required=False, help="Rerun full experiment (given a csv file)")
    parser.add_argument('-si','--size',type=str, required=False, help="Map size")


    return parser.parse_args()

# get EID values from experiment csv file
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


evaluators=evaluation_functions.evaluators
social_evaluators=evaluation_functions.social_evaluators
bargaining_evaluators=["Nash", "Kalai_Smorodinsky", "Egalitarian", "Utilitarian"]

# find the optimal social welfare path
def calc_social_welfare(G):
    V_C=[n for n in G.nodes if G.nodes[n]['tau_1']>G.nodes[n]['tau_2']]
    return isc2pp.social_welfare_optimal_path(G,V_C,'s_1','s_2','g_1','g_2',evaluation_functions.social_welfare)

# calculate the price of anarchy
def price_of_anarchy(potential, optimal_sw):
    worst_eq=max(potential, key=lambda p: p[0]+p[1])
    worst_eq_sw=worst_eq[0]+worst_eq[1]
    return float(worst_eq_sw)/(optimal_sw)

# calculate the price of stability
def price_of_stability(potential, optimal_sw):
    best_eq=min(potential, key=lambda p: p[0]+p[1])
    best_eq_sw=best_eq[0]+best_eq[1]
    return float(best_eq_sw)/(optimal_sw)

# calculate the manhatten distance
def manhatten_distance(p1, p2):
    return abs(p1[0]-p2[0])+abs(p1[1]-p2[1])


# given a graph, the positions of the nodes, the grid, the experiment id, the solver and the map, run the experiment and return the paths, social paths and the final row to be written in the csv file
def run_experiment(G, positions, grid, eid, solver, map):

    # build the set of cooperation vertices
    V_C=[n for n in G.nodes if G.nodes[n]['tau_1']>G.nodes[n]['tau_2']]
                
    # find the optimal equilibrium cooperation joint strategies from both players' perspectives
    paths=isc2pp.map_optimal_ecjs(G,V_C,'s_1','s_2','g_1','g_2')
    
    # find the shortest independent paths, shortest cooperated paths, best responses and check if the shortest independent paths form a pure Nash equilibrium
    SIP1,SIP2=(isc2pp.shortest_independent_path(G,'s_1','g_1'),isc2pp.shortest_independent_path(G,'s_2','g_2'))
    SCP1, SCP2=(isc2pp.shortest_cooperated_path(G,'s_1','g_1'),isc2pp.shortest_cooperated_path(G,'s_2','g_2'))
   
    BR1=isc2pp.best_response(G,V_C,'s_1','g_1',SIP2['path'])
    BR2=isc2pp.best_response(G,V_C,'s_2','g_2',SIP1['path'])
    
    is_sp_pne=BR1['length']==SIP1['length'] and BR2['length']==SIP2['length']
    
    # calculate the path time divergence between the two shortest independent paths
    path_time_div=calculate_divergance(G,SIP1,SIP2)
   
    # calculate the optimal social welfare path
    social_paths=calc_social_welfare(G)

    # store the experiment data in a pickle file
    data={"grid":grid, "graph":G, "pos":positions, "paths":paths,"args":args, "social_paths":social_paths, "map":map}
    
    if not os.path.exists(ARCHIVE_PATH):
        os.makedirs(ARCHIVE_PATH)
    with open(f'{ARCHIVE_PATH}/{eid}.pkl', 'wb') as f:
        pickle.dump(data, f)

    # clear dominated joint paths and convert to list
    isc2pp.clear_dominated_joint_paths(paths)
    paths=list(paths.values()) 
    
    # if there are no optimal equilibrium cooperation joint strategies, something is wrong - print the experiment id for debugging
    if(len(paths)==0):
        print()
        print(eid)

    paths2=[(x,y) for (y,x) in paths]


    # extract the path times for both players from the optimal equilibrium cooperation joint strategies and their reversed version (for player 2's perspective)
    potential=[(p[0]['length'],p[1]['length']) for p in paths]
    potential2=[(x,y) for (y,x) in potential]

    #evaluate the path times of the shortest independent paths given both players are using it
    SIPSIP=simulation.evaluate_paths(G,SIP1['path'],SIP2['path'])

    # prepare the final row to be written in the csv file
    final_row1=[eid,path_time_div,is_sp_pne,potential, SIP1['length'], SIP2['length'],SCP1['length'],SCP2['length'], SIPSIP[0],social_paths[0]['length'],social_paths[2]]
    final_row2=[eid,path_time_div,is_sp_pne,potential2, SIP2['length'], SIP1['length'],SCP2['length'],SCP1['length'], SIPSIP[1],social_paths[1]['length'],social_paths[2]]

    # evaluate the path times of the optimal equilibrium cooperation joint strategies given both players are using it (from both players' perspectives) and append the results to the final row
    for description, eval in evaluators.items():
        result=simulation.evaluate_paths(G,min(paths,key=lambda p:eval(p,(SIP1,SIP2), G))[0]['path'],min(paths2,key=lambda p: eval(p,(SIP2,SIP1), G))[0]['path'])
        final_row1.append(result[0]+result[1])
        final_row1.append(result[0])

        final_row2.append(result[0]+result[1])
        final_row2.append(result[1])


    # evaluate the path times of the bargaining solutions given both players are using it (from both players' perspectives) and append the results to the final row
    sol1=solver.find_bargaining_solutions(potential,  SIP1['length'],SIP2['length'], SIPSIP)
    sol2=solver.find_bargaining_solutions(potential2,  SIP2['length'], SIP1['length'], reversed(SIPSIP))
    
    for bargaining_solution in bargaining_evaluators:
        final_row1.append(sum(sol1[bargaining_solution+"_point"]))
        final_row1.append(sol1[bargaining_solution+"_point"][0])

        final_row2.append(sum(sol2[bargaining_solution+"_point"]))
        final_row2.append(sol2[bargaining_solution+"_point"][0])


    # calculate the price of anarchy and price of stability and append the results to the final row
    poa=price_of_anarchy(potential, social_paths[2])
    pos=price_of_stability(potential, social_paths[2])

    final_row1.extend([poa,pos])
    final_row2.extend([poa,pos])

        
    return paths, social_paths, final_row1, final_row2


# run a full experiment given the arguments, the solver and the writer to write the results in the csv file
def run_full_experiment(args, solver, writer):
    G, grid, pos, paths, social_paths, eid=None, None, None, None, None, None
    
    count=0
    # run the experiment for the given number of iterations and write the results in the csv file
    while(count<args.iterations):
        
        # generate a unique experiment id for each iteration
        eid = uuid.uuid4()
        
        # print the progress of the experiment
        percent = count / args.iterations * 100
        bar = ('#' * int(percent // 2)).ljust(50)  # 50 characters wide
        print(f"\rProgress: |{bar}| {percent:.1f}% ({count}/{args.iterations}) complete", end="")
        
        # generate the graph, positions, grid and map for the experiment using the mapf_benchmark_provider
        G, pos, grid, map = mapf_benchmark_provider.get_graph_with_timeout(args.map, args.scenario, args.density, args.magnitude, args.seperation, args.extent, 3, args.size)

        # run the experiment and get the paths, social paths and the final row to be written in the csv file
        paths, social_paths, final_row1, final_row2=run_experiment(G, pos, grid, eid, solver, map)
        if len(paths)>1 or True:
            writer.writerow(final_row1)
            writer.writerow(final_row2)
            count+=1

    return G, grid, pos, paths, social_paths, eid


# rerun a full experiment given an input csv file, the solver and the writer to write the results in the csv file
def rerun_full_experiment(input_fname, solver, final_writer):
    
    # get the experiment ids from the input csv file
    eids=get_eid_values(input_fname)

    # run the experiment for each experiment id and write the results in the csv file
    for i,eid in enumerate(eids):
    
        # print the progress of the experiment
        percent = (i) / len(eids) * 100
        bar = ('#' * int(percent // 2)).ljust(50)  # 50 characters wide
        print(f"\rProgress: |{bar}| {percent:.1f}% ({i+1}/{len(eids)}) complete", end="")
    
        # load the graph, positions, grid, paths and arguments for the experiment from the pickle file
        with open(f'{ARCHIVE_PATH}/{eid}.pkl', 'rb') as f:
            loaded_data = pickle.load(f)
            G=loaded_data["graph"]
            grid=loaded_data["grid"]
            pos=loaded_data["pos"]
            paths=loaded_data["paths"]
            args=loaded_data["args"]
        
        # run the experiment and store the results in the csv file
        paths, social_paths, final_row1, final_row2=run_experiment(G, pos, grid, eid, solver)
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
    return node


def calculate_divergance(G,path1, path2):
    G=simulation.relabel_nodes(G)
    all_pairs_sp1=isc2pp.all_pairs_shortest_paths(G,'tau_1')
    p1,p2=simulation.relabel_path(path1['path']),simulation.relabel_path(path2['path'])
    state1, state2=simulation.interpolate_paths(G,p1,p2)
    minimal_path_time=float('inf')
    for i in range(max(len(state1),len(state2))):
        if(i>=len(state1)):
            state1.append(state1[-1])
        if(i>=len(state2)):
            state2.append(state2[-1])
       
        (node1, node2)=get_node_cell(G,state1[i]),get_node_cell(G,state2[i])
        path_time=all_pairs_sp1[node1][node2]['length']

        if(path_time<minimal_path_time):
            minimal_path_time=path_time

    return minimal_path_time


# store the full experiment data in a text file for future reference
def store_experiemnt_description(args):
    if not os.path.exists(RESULTS_PATH):
        os.makedirs(RESULTS_PATH)
    f=args.description if args.description else args.output
    description_path = RESULTS_PATH+f+".txt"
    os.makedirs(os.path.dirname(description_path), exist_ok=True)
    with open(description_path, mode='w', newline='') as file:
            file.write(str(args)+"\n")
            file.write(f"Date: {time.ctime()}\n")
            file.write(f"Archive path: {ARCHIVE_PATH}\n")
            file.write(f"Evaluators: {list(evaluators.keys())}\n")
            file.write(f"Social Evaluators: {list(social_evaluators.keys())}\n")
            file.write("\n")


if __name__ == "__main__":
   
    args = parse_args()

    # if a file is given to load, load the graph, positions, grid, paths and arguments for the experiment from the pickle file
    if args.load:
        eid=args.load
        with open(f'{ARCHIVE_PATH}/{args.load}.pkl', 'rb') as f:
            show=args.visualization
            loaded_data = pickle.load(f)
            G=loaded_data["graph"]
            grid=loaded_data["grid"]
            pos=loaded_data["pos"]
            paths=loaded_data["paths"]

            social_paths=None
            social_paths=loaded_data['social_paths']
            args=loaded_data["args"]
            args.visualization=show
        isc2pp.clear_dominated_joint_paths(paths)
        paths=list(paths.values()) 

    # if no file is given to load, run a full experiment and store the results in the csv file
    else:
        store_experiemnt_description(args)
        
        output_path = RESULTS_PATH+args.output+".csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, mode='w', newline='') as final_file:
            # write the header of the csv file
            final_writer = csv.writer(final_file)
            final_writer.writerow(["eid","path_time_div","is_sp_pne","Potential", "SIP1", "SIP2","SCP1","SCP2", "SIP1|SIP2", "Individual Time In Optimal Social Welfare","Optimal Social Welfare", ]+[item for k in evaluators.keys() for item in (f"{k}", f"Individual Time In {k}")] + [item for k in bargaining_evaluators for item in (k, f"Individual Time In {k}")] + ["PoA","PoS"])

            # initialize the MATLAB solver for bargaining solutions
            solver = bargaining_solutions.MATLABBargainingSolutions()

            # if a file is given to rerun, rerun the full experiment for each experiment id in the input csv file and store the results in the csv file, otherwise run a new full experiment and store the results in the csv file
            if not args.rerun is None:
                input=args.rerun+".csv"
                G, grid, pos, paths, social_paths, eid=rerun_full_experiment(input, solver, final_writer)
            
            else:
                G, grid, pos, paths, social_paths, eid=run_full_experiment(args, solver, final_writer)
            
            # clean up the MATLAB solver
            del solver

    # if visualization is enabled, visualize the scenario using the GUI
    if args.visualization:
        SIP1,SIP2=(isc2pp.shortest_independent_path(G,'s_1','g_1'),isc2pp.shortest_independent_path(G,'s_2','g_2'))
        V_C=[n for n in G.nodes if G.nodes[n]['tau_1']>G.nodes[n]['tau_2']]         
        BR1,BR2=(isc2pp.best_response(G,V_C,'s_1','g_1',SIP2['path']),isc2pp.best_response(G,V_C,'s_2','g_2',SIP1['path']))
        SW1,SW2,_=social_paths
        all_paths=dict()
        all_paths["SIP"]=(SIP1,SIP2)
        all_paths["BR"]=(SIP1,BR2)
        all_paths["Optimal SW"]=social_paths        
        for i, p in enumerate(paths):
            all_paths[f"Path {i}"]=p

        g = gui.GUI(G, pos, grid, all_paths, args, eid)
        # g=gui.GUI(G,pos,grid, paths,{"Social Sum": social_paths}, args, eid, (SIP1,SIP2), (SIP1,BR2))
        g.show()
