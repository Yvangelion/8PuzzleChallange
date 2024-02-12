import heapq
import random
import time
import tkinter as tk
from tkinter import ttk
from functools import partial
import time
from collections import deque


# contstuct 
class Node:
    def __init__(self, state, parent=None, action=None, cost=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.heuristic = heuristic

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

# gui for answer
def update_gui(textbox, content):
    textbox.config(state=tk.NORMAL)
    textbox.delete(1.0, tk.END)
    textbox.insert(tk.END, content)
    textbox.config(state=tk.DISABLED)
    
# print matrix to terminal
def view_matrix(state):
    for row in state:
        print(" ".join(map(str, row)))
    print()

# where is this number in stack
def find_number(state, number):
    for i, row in enumerate(state):
        for j, value in enumerate(row):
            if value == number:
                return i, j
    return None

# create our start state randomly
def generate_random_state():
    numbers = list(range(1, 9)) + [0]
    random.shuffle(numbers)
    ans = [numbers[i:i+3] for i in range(0, 9, 3)]
    return ans

def manhattan_distance(state, goal_state):
    distance = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != goal_state[i][j]:
                goal_row, goal_col = find_number(goal_state, state[i][j])
                distance += abs(i - goal_row) + abs(j - goal_col)
    return distance

#start astar
def astar(initial_state, goal_state):
    # set starting parameters
    viewed = set()
    nodes_vis = 0
    priority_queue = [Node(initial_state, heuristic=manhattan_distance(initial_state, goal_state))]

    while priority_queue:
        pointer_node = heapq.heappop(priority_queue)

        # if we start with the goal state, just end.
        if pointer_node.state == goal_state:
            path = []
            while pointer_node:
                path.append(pointer_node.state)
                pointer_node = pointer_node.parent
            path.reverse()
            return path, nodes_vis
        
        # ensure it's not viewed
        if tuple(map(tuple, pointer_node.state)) not in viewed:
            viewed.add(tuple(map(tuple, pointer_node.state)))
            nodes_vis += 1

            # view the held node and push the unviewed child nodes to the priority queue
            empty_row, empty_col = find_number(pointer_node.state, 0)

            # travel n,s,e,w as needed
            travels = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            for travel in travels:
                new_row, new_col = empty_row + travel[0], empty_col + travel[1]

                if 0 <= new_row < 3 and 0 <= new_col < 3:
                    newest_state = [list(row) for row in pointer_node.state]
                    newest_state[empty_row][empty_col], newest_state[new_row][new_col] = newest_state[new_row][new_col], 0

                    new_node = Node(newest_state, pointer_node, travel, pointer_node.cost + 1,
                                          heuristic=manhattan_distance(newest_state, goal_state))
                    heapq.heappush(priority_queue, new_node)

    # no solution
    return None, nodes_vis
 


# goal state
goal_state = [[1, 2, 3], [8, 0, 4], [7, 6, 5]]

#
def run_algorithm(result_textbox, runs_entry, treeview):
    N = int(runs_entry.get())
    total_nodes_viewed = 0
    total_elapsed_time = 0

    # restart after each run
    for item in treeview.get_children():
        treeview.delete(item)

    for i in range(N):
        initial_state = generate_random_state()
        #print(initial_state)

        start_time_algorithm = time.time()
        algorithm_result, nodes_viewed = astar(initial_state, goal_state)
        end_time = time.time()

        if algorithm_result:
            # found sol
            treeview.insert("", "end", values=(f"Test {i+1}","True",str(initial_state), nodes_viewed, round((end_time - start_time_algorithm) * 1000, 3)))
        else:
            # no sol
            #treeview.insert("", "end", values=(f"Test {i+1}","Solution Found", str(initial_state), "No solution found", "N/A"))
            treeview.insert("", "end", values=(f"Test {i+1}","False",str(initial_state), nodes_viewed, round((end_time - start_time_algorithm) * 1000, 3)))

        # calc values
        total_nodes_viewed += nodes_viewed
        total_elapsed_time += (end_time - start_time_algorithm)

    # calc avgs
    average_nodes_viewed = total_nodes_viewed / N
    average_elapsed_time = (total_elapsed_time * 1000) / N

    #can add avg to table instead 
    #treeview.insert("", "end", values=("Average", round(average_nodes_viewed, 3), round(average_elapsed_time, 3)))
    
    # for answer in its own textbox
    update_gui(result_textbox, f"Average Nodes viewed: {round(average_nodes_viewed, 3)}\nAverage Elapsed Time: {round(average_elapsed_time, 3)} miliseconds")

# GUI setup
def create_gui():
    root = tk.Tk()
    # program title
    root.title("AStar 8 Puzzle Solver")

    # goal state
    goal_state_label = ttk.Label(root, text="Current Goal State: [[1, 2, 3], [8, 0, 4], [7, 6, 5]]")
    goal_state_label.grid(row=0, column=0, pady=10)

    #number of runs for tests
    runs_label = ttk.Label(root, text="Number of Runs:")
    runs_label.grid(row=2, column=0, pady=10)

    runs_entry = ttk.Entry(root)
    runs_entry.grid(row=2, column=1, pady=10)
    
    # restult for tableview 
    result_treeview = ttk.Treeview(root, columns=("Test","Solution Found","Start State", "Nodes viewed", "Elapsed Time (ms)"), show="headings")
    result_treeview.heading("Test", text="Test")
    result_treeview.heading("Solution Found", text="Solution Found")
    result_treeview.heading("Start State", text="Start State")
    result_treeview.heading("Nodes viewed", text="Nodes viewed")
    result_treeview.heading("Elapsed Time (ms)", text="Elapsed Time (ms)")
    result_treeview.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    
    #calcuated result for avag time and avag viewed nodes textbox
    result_textbox = tk.Text(root, height=2, width=100, state=tk.DISABLED)
    result_textbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    # start button
    #run_button = ttk.Button(root, text="Run algorithm", command=partial(run_algorithm, 1, runs_entry, result_textbox))
    run_button = ttk.Button(root, text="Run algorithm", command=partial(run_algorithm, result_textbox, runs_entry, result_treeview))
    run_button.grid(row=5, column=0, columnspan=2, pady=10)

    root.mainloop()
    
#create gui interface
create_gui()