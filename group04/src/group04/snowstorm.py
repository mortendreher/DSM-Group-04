import numpy as np
import requests
import networkx as nx
import matplotlib.pyplot as plt
import time

G = nx.DiGraph()
request_count = 0

# LA / MD
# group server requests, add short pause (1 sec) after 20 requests
# call this method when doing server requests


def request_snowstorm_burst(url, params):
    if request_count % 20 == 0:
        time.sleep(1)
    request_count + 1
    return requests.get(url, params)


def find_concepts(keyword: str) -> dict:
    params = {"term": keyword}
    response = request_snowstorm_burst(
        "https://snowstorm.test-nictiz.nl/MAIN/concepts", params=params
    )
    return response.json()


# KK
def get_descriptionid_byconceptid(Conceptid):
    params = {"conceptId": Conceptid}
    response = request_snowstorm_burst(
        "https://snowstorm.test-nictiz.nl/MAIN/descriptions?", params=params)

    return response.json()


# MD: returns all relationships inbound to a node given conceptid
# 64572001
def get_inbound_relationships(conceptid):
    params = {"conceptId": conceptid}
    response = request_snowstorm_burst(
        "https://snowstorm.test-nictiz.nl/MAIN/concepts/"+conceptid+"/inbound-relationships", params=params)
    return response.json()


# result = get_inbound_relationships("10200004")
# print(result)
# print("a"+result["inboundRelationships"][0]["sourceId"])

# KK
def get_childern_ids(conceptid):
    params = {"conceptId": conceptid}
    response = request_snowstorm_burst(
        "https://snowstorm.test-nictiz.nl/browser/MAIN/concepts/" + conceptid +
        "/children?form =inferred&includeDescendantCount=false", params=params)
    return response.json()
# KK
def get_parents_ids(conceptid):
    params = {"conceptId": conceptid}
    response = request_snowstorm_burst(
        "https://snowstorm.test-nictiz.nl/browser/MAIN/concepts/" + conceptid +
        "/parents?form=inferred&includeDescendantCount=false", params=params)
    return response.json()


# KK
# childernids = get_childern_ids("10200004")
# for childid in childernids:
#    G.add_edge("10200004", childid['conceptId'], capacity=1.0)
    # print(childid["conceptId"])

# KK
# descriptionids = get_descriptionid_byconceptid(10200004)
# for descid in descriptionids["items"]:
#    print(descid["descriptionId"])

name = 'liver'

concepts = find_concepts(name)
for concept in concepts["items"]:
    # G.add_edge(name, concept['conceptId'], capacity=1.0)
    # name = concept["pt"]["term"]
    print("#" + concept["id"] + ": " + concept["fsn"]["term"])
    # flow_value, flow_dict = nx.maximum_flow(G, name, concept["pt"]["term"])
    # print(flow_value)
    # print(flow_dict)

# nx.draw_networkx(G)
# plt.show()

# starting point
# 272625005 # Entire body organ (PT)


# MD: recursive adding to graph with a maximum number of steps (>0)
G_m = nx.DiGraph()  # create graph
granddad_id = "138875005"  # id for root node (272625005, 272379006), snomed root: 138875005
G_m.add_node(granddad_id,)  # add root node to graph (not necessary)
color_map = []  # create map to color nodes later on

current_maxheight = 2  # fixed maximum for number of steps -> 3 or less can be displayed as a graph

# LA
# getting the height of a node in the given graph
# ---------------------------------------------------
# return value is the height of the node, given as parameter conceptid
# parameter height is by default 0 and is not mandatory when using the method


def get_height(conceptid, height):
    if conceptid != granddad_id:
        parent_ids = get_parents_ids(conceptid)
        for parent in parent_ids:
            height += 1
            get_height(parent['conceptId'], height)
    return height


# MD: Compute depth for a given conceptid
# --------------------------------------
# returns depth of the node in graph (number of steps from root node)
# parameter is a conceptid, returns 0 if conceptid is root node
def get_depth(conceptid):
    depth = 0
    while conceptid != granddad_id:
        conceptid = get_parents_ids(conceptid)[0]['conceptId']
        depth += 1
    return depth


# possible output below
# print("height", get_height("307824009",0))
print("depth", get_depth("83299001"))
print("depth 2: ", get_depth("307824009"))

# print(get_parents_ids("370136006")[0]['conceptId'])

# Filling graph
# --------------------
# add height levels of nodes connected to node "conceptid" recursively to graph
# height: additional steps from root node (does not work for 0!)


def add_children_to_graph_recursive(conceptid, height):
    if height > 0:
        children_ids = get_childern_ids(conceptid)  # get ids of children of current node
        for child in children_ids:
            G_m.add_edge(conceptid, child['conceptId'], capacity=1.0, weight=1.0)  # add edge from parent to child
            G_m.add_edge(child['conceptId'], conceptid, capacity=1.0, weight=1.0)
            # add edge from child to parent (cap might have to be changed to -1.0 later on)
            add_children_to_graph_recursive(child['conceptId'], height - 1)
            # call method recursively with height reduced by 1
    else:
        return
# KK :
def add_parents_to_graph(conceptid):
    #first  getting all of parents IDs by calling get_parents_ids function
   parents_ids=get_parents_ids(conceptid)
    #then add edges to graph ,their source parnet with target child ,the parents_ids are sorted by highst level index(0)
   for i in range (len(parents_ids)-1):
    G_m.add_edge(parents_ids[i].get("conceptId"), parents_ids[i+1].get("conceptId"), capacity=1.0)
   #after adding all edges between all parents , then last edge between root node and next level should be added
   G_m.add_edge(parents_ids[len(parents_ids)-1].get("conceptId"),conceptid, capacity=1.0)


add_children_to_graph_recursive(granddad_id, current_maxheight)  # call method once
# add_parents_to_graph("272625005") # Please don't do this to the same graph - it adds no information!!
# Coloring
# --------------
for node in G_m:
    if node == granddad_id:
        color_map.append("red")  # root node will be colored red
    elif node == "370136006":
        color_map.append("green")
    else:
        color_map.append("blue")  # other nodes will be colored blue

# nx.draw_networkx(G_m)  # draw graph without colors
print("Graph contains ", G_m.number_of_nodes(), " nodes.")
flow_value, flow_dict = nx.maximum_flow(G_m, granddad_id, "370136006")
# flow_value, flow_dict = nx.maximum_flow(G_m, "361716006", "361715005")
print("Max flow", flow_value)
# print(flow_dict)  # produces a LOT of output

nx.draw_networkx(G_m, node_color=color_map)  # draw graph with colors
plt.show()  # finally, show plot


