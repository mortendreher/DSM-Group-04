__version__ = '0.1.0'
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
flow_value, flow_dict = nx.maximum_flow(G, "x", "d")
print(flow_value)
print(flow_dict)
nx.draw_networkx(G)
plt.show()
