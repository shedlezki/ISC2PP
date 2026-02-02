import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import visualization


social_evaluators=["Social Sum","Social Avg","Social Min-Min","Social Min-Max"]

class GUI:
    def __init__(self, G, pos, grid, paths, social_paths, args, eid, sp, br):
        self.root = tk.Tk()
        self.vis=visualization.GraphVisualizer(G,pos, grid)
        self.paths=paths
        self.social_paths=social_paths
        self.anim=None
        self.args=args
        self.eid=eid
        self.sp=sp
        self.br=br

    def copy_to_clipboard(self, event):
        text = self.eid
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()  # Keeps the clipboard content after the program exits
        


    def show(self):

        self.root.title("Graph Visualizer")
        self.canvas = FigureCanvasTkAgg(self.vis.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=4)

        label = tk.Label(text=f"Map: {self.args.map} Density: {self.args.density} Magnitude: {self.args.magnitude} Extent: {self.args.extent} Correlation: {self.args.correlation} EID: {self.eid}", fg="black", cursor="hand2")
        label.grid(row=1, column=0)
        label.bind("<Button-1>", lambda event:self.copy_to_clipboard(event))
        # clear_buttin = tk.Button(self.root, text="Clear", command=lambda: self.vis.d())
        # clear_buttin.grid(row=1, column=0, pady=10)

        # self.canvas.create_text(150, 50, text=f"Map: {self.args.map}", fill="black", font=("Arial", 14))
        # self.canvas.create_text(150, 50, text=f"Density: {self.args.density}", fill="black", font=("Arial", 14))
        # self.canvas.create_text(150, 50, text=f"Magnitude: {self.args.magnitude}", fill="black", font=("Arial", 14))
        # self.canvas.create_text(150, 50, text=f"Extent: {self.args.extent}", fill="black", font=("Arial", 14))
        # self.canvas.create_text(150, 50, text=f"Correlation: {self.args.correlation}", fill="black", font=("Arial", 14))
        # self.canvas.create_text(150, 50, text=f"EID: {self.eid}", fill="black", font=("Arial", 14))


        # self.vis.draw_path(self.paths[0][0]['path'],'red')
#  parser.add_argument('-m','--map', type=str, required=False, default="empty-8-8", help="Map name")
#     parser.add_argument('-d','--density', type=float, required=False, default=0.5, help="Density value")
#     parser.add_argument('-mt','--magnitude', type=int, required=False, default=10, help="Magnitude value")
#     parser.add_argument('-e','--extent', type=int, required=False, default=15, help="Extent value")
#     parser.add_argument('-c','--correlation', type=int, required=False, default=4, help="Correlation value")
#     parser.add_argument('-i','--iterations', type=int, required=False, default=1, help="Number of iterations")
#     parser.add_argument('-o','--output', type=str, required=False, default="results", help="Output file name")
#     parser.add_argument('-v','--visualization',action='store_true', help="Visualize the scenario")
#     parser.add_argument('-l','--load',type=str, required=False, help="Experiment file to load")


        colors=["#FFB84C","#F266AB","#A459D1","#2CD3E1","#0079FF","#00DFA2","#F6FA70","#FF0060"]

        def on_check(var, p1, p2,i, color):
            if var.get():
                if(i not in drawn_paths.keys()):
                    drawn_paths[i]=[]
                drawn_paths[i].extend(self.vis.draw_path(p1['path'], color, i*0.02))
                drawn_paths[i].extend(self.vis.draw_path(p2['path'], color,i*0.02))
            else:
                self.vis.clear_path(drawn_paths[i])  # optional: remove path if unchecked
                drawn_paths[i].clear()
            self.canvas.draw()
        
        all_paths=[self.sp,self.br]+self.paths 
        check_states = {p: tk.BooleanVar() for p in range(len(all_paths))}
        if self.social_paths:
            check_states_social = {p: tk.BooleanVar() for p in range(len(self.social_paths))}        
        drawn_paths={}

        def play_animation(p1,p2):
            self.vis.set_animation(p1,p2)
            self.anim=self.vis.ani
            self.canvas.draw()


            self.canvas.draw()



        for i, paths in enumerate(all_paths):
            var = check_states[i]
            cb = tk.Checkbutton(
                self.root,
                text=f"path {i-1} ({paths[0]['length']},{paths[1]['length']})" if i>1 else f"SP ({paths[0]['length']},{paths[1]['length']})" if i==0 else f"BR ({paths[0]['length']},{paths[1]['length']})",
                variable=var,
                fg=colors[i],
                command=lambda v=var, p1=paths[0], p2=paths[1], index=i: on_check(v, p1, p2, index, colors[index])
            )
            cb.grid(row=1+1 + i, column=0, sticky='w')
            play_button = tk.Button(self.root, text="Play", command=lambda p1=paths[0], p2=paths[1]: play_animation(p1,p2))
            play_button.grid(row=1+i+1, column=0, pady=10)

        if self.social_paths:
            for i, paths in enumerate(self.social_paths):
                var = check_states_social[i]
                cb = tk.Checkbutton(
                    self.root,
                    text=f"{social_evaluators[i]} ({paths[0]['length']},{paths[1]['length']})={paths[2]}",
                    variable=var,
                    fg=colors[(len(all_paths)+i)%len(colors)],
                    command=lambda v=var, p1=paths[0], p2=paths[1], index=(len(all_paths)+i): on_check(v, p1, p2, index, colors[index%len(colors)])
                )
                cb.grid(row=1+1 + i+len(all_paths), column=0, sticky='w')
                play_button = tk.Button(self.root, text="Play", command=lambda p1=paths[0], p2=paths[1]: play_animation(p1,p2))
                play_button.grid(row=1+i+1+len(all_paths), column=0, pady=10)
       

        self.root.mainloop()

        # self.vis.show()
        


        





# if __name__ == "__main__":
#     g= GUI()



# # Checkboxes


# for i, group in enumerate(edge_groups):
#     cb = ttk.Checkbutton(
#         root, text=group, variable=check_states[group],
#         command=draw_graph
#     )
#     cb.grid(row=1, column=i)

# draw_graph()


