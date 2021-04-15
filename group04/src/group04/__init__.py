__version__ = '0.1.0'
import maxflow
from tkinter import *
import networkx as nx
import matplotlib.pyplot as plt
G = nx.DiGraph()
G.add_edge("x", "a", capacity=3.0)
G.add_edge("x", "b", capacity=1.0)
G.add_edge("a", "c", capacity=3.0)
G.add_edge("b", "c", capacity=5.0)
G.add_edge("b", "d", capacity=4.0)
G.add_edge("x", "d", capacity=3.0)
G.add_edge("d", "e", capacity=2.0)
G.add_edge("c", "y", capacity=2.0)
G.add_edge("e", "y", capacity=3.0)
from tkinter import *

# adding functionality to the button
def button_action():
    entry_text1 = input_node_1.get()
    entry_text2 = input_node_2.get()
    if entry_text1 == "" or entry_text2 == "":
        welcome_label.config(foreground='red')          #background='black',
        welcome_label.config(text="You have to type in values")
    elif entry_text1 != "" and entry_text2 != "":
        flow_value, flow_dict = nx.maximum_flow(G, entry_text1, entry_text2)
        entry_text = "MaxFlow: " + str(flow_value)
        output_label.config(text=entry_text)
    else:
        welcome_label.config(foreground='black')
        entry_text = "Hello !"
        welcome_label.config(text=entry_text)


def button_action_graph():
    nx.draw_networkx(G)
    plt.show()


window = Tk()
window.title("Graph")
window.geometry("400x200")

# Instruction-Label
node_1_label = Label(window, text="first node: ")
# node_1_label.config(foreground='BLACK', background='white')
node_2_label = Label(window, text="second node: ")
# node_2_label.config(foreground='BLACK', background='white')
# Welcomes the user with his entered name after pressing the button
welcome_label = Label(window)
output_label = Label(window, text="MaxFlow: ")

# userinput
input_node_1 = Entry(window, bd=0, width=40)
input_node_2 = Entry(window, bd=0, width=40)

maxflow_button = Button(window, text="Maxflow", command=button_action)
maxflow_button.config(foreground='BLACK', background='white')
exit_button = Button(window, text="Quit", command=window.quit)
exit_button.config(foreground='BLACK', background='white')
graph_button = Button(window, text="Graph", command=button_action_graph)

# add the components to the window
node_1_label.place(x=0, y=20, width=100,  height=20)
node_2_label.place(x=200, y=20, width=100,  height=20)

input_node_1.place(x=120, y=20, width=50,  height=20)
input_node_2.place(x=320, y=20, width=50,  height=20)
maxflow_button.place(x=0, y=50, width=60,  height=30)
exit_button.place(x=240, y=50, width=60,  height=30)
welcome_label.place(x=80, y=50, width=150,  height=30)
output_label.place(x=0, y=100, width=100,  height=30)
graph_button.place(x=200, y=100, width=50,  height=30)

mainloop()
# flow_value, flow_dict = nx.maximum_flow(G, "x", "d")
# print(flow_value)
# print(flow_dict)

