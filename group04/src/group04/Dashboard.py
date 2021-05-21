from bokeh.layouts import widgetbox
from bokeh.models import Slider
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import CustomJS, TextInput
import pandas as pd
import networkx
import networkx  as nx
import requests

from bokeh.io import output_file, show
from bokeh.models import (BoxSelectTool, Circle, EdgesAndLinkedNodes, HoverTool,
                          MultiLine, NodesAndLinkedEdges, Plot, Range1d, TapTool, )
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx

import numpy as np
from bokeh.io import output_notebook, show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, HoverTool
from bokeh.plotting import figure
from bokeh.plotting import from_networkx


############################



def get_parents_ids(conceptid):
    response = requests.get(
        "https://snowstorm.test-nictiz.nl/browser/MAIN/concepts/" + conceptid + "/parents?form=inferred&includeDescendantCount=false")
    js = response.json()
    ids = list()
    for i in range(len(js)):
        ids.append(js[i].get("conceptId"))
    return ids


def get_parents_to_root_node_dict(conceptid):
    ids0_dict = dict()
    ids_dict = dict()
    ids0_dict[conceptid] = get_parents_ids(conceptid)
    vals = ids0_dict.values()
    for ix in range(len(vals)):
        vals_list = list(vals)[ix]
        for i in vals_list:
            for x in get_parents_ids(i):
                vals_list.append(x)
    vals_set = set(vals_list)
    for elem in vals_set:
        ids_dict[elem] = get_parents_ids(elem)
    ids_dict[conceptid] = get_parents_ids(conceptid)
    return ids_dict


def get_all_parents_edges_from_dict(conceptid):
    e_dict = get_parents_to_root_node_dict(conceptid)
    edges = pd.DataFrame()
    sources = []
    targets = []
    for i in e_dict.keys():
        for n in e_dict.get(i):
            sources.append(i)
            targets.append(n)
    sources_as_series = pd.Series(sources)
    targets_as_series = pd.Series(targets)
    edges = pd.DataFrame({"source": sources_as_series.values, "target": targets_as_series.values})
    return edges





def get_term_by_conceptID(conceptid):
    response = requests.get(
        "https://snowstorm.test-nictiz.nl/browser/MAIN/concepts?conceptIds=" + conceptid + "&number=0&size=1")
    js = response.json()
    term = js.get("items")[0].get("fsn").get("term")
    return term


######################
print(get_all_parents_edges_from_dict("83299001"))
G = networkx.from_pandas_edgelist(get_all_parents_edges_from_dict("83299001"), source='source', target='target',
                                  edge_attr=["source", "target"])
networkx.draw(G)
# Choose a title!

title = 'SNOMED CT Graph'
# Establish which categories will appear when hovering over each node


# Create a plot — set dimensions, toolbar, and title
plot = figure(sizing_mode="stretch_width",
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
              x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title)

for n in G.nodes():
    G.nodes[n]["term"] = get_term_by_conceptID(n)
# Create a network graph object with spring layout
network_graph = from_networkx(G, networkx.spring_layout, scale=13, center=(0, 0))
node_hover_tool = HoverTool(tooltips=[("Concept ID", "@index"), ("Term", "@term")],
                            renderers=[network_graph.node_renderer])
plot.add_tools(node_hover_tool)


# Add network graph to the plot
# plot.renderers.append(network_graph)
network_graph.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
network_graph.node_renderer.selection_glyph = Circle(size=15, fill_color=Spectral4[2])
network_graph.node_renderer.hover_glyph = Circle(size=15, fill_color=Spectral4[1])
height_slider = Slider(start=1, end=10, value=1, step=1, title="Height")
network_graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=5)
network_graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=5)
network_graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=5)

network_graph.selection_policy = NodesAndLinkedEdges()
network_graph.inspection_policy = EdgesAndLinkedNodes()

plot.renderers.append(network_graph)

text_input = TextInput(value="Enter Concept ID", title="Concept ID:")
layout = column(row(height_slider, plot), row(text_input), sizing_mode="stretch_both")
curdoc().add_root(layout)


def find_shortest_path(G, start, end, path=[]):
    if start not in G.nodes():
        return None
    elif end not in G.nodes():
        return None
    path = path + [start]
    if start == end:
        return path

    shortest = None
    for node in G[start]:
        if node not in path:
            newpath = find_longest_path(G, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest


def find_longest_path(G, start, end, path=[]):
    if start not in G.nodes():
        return None
    elif end not in G.nodes():
        return None
    path = path + [start]
    if start == end:
        return path

    longest = None
    for node in G[start]:
        if node not in path:
            newpath = find_longest_path(G, node, end, path)
            if newpath:
                if not longest or len(newpath) > len(longest):
                    longest = newpath
    return longest


def get_distance_between_two_nodes(G, start, end, path=[]):
    if start not in G.nodes():
        return None
    elif end not in G.nodes():
        return None
    else:
        return len(find_shortest_path(G, start, end, path=[])) - 1



print(find_longest_path(G, "83299001", "138875005", path=[]))
print(find_shortest_path(G, "83299001", "138875005", path=[]))
print(get_distance_between_two_nodes(G, "83299001", "138875005", path=[]))