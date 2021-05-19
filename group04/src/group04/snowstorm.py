import numpy as np
import requests
import networkx as nx
import matplotlib.pyplot as plt
import time
import csv
import pandas as pd

# LA
# class Node
# Variables: conceptid, parentid, descriptionid, active (default True)
# Variables outside of the constructor: depth


class Node(object):
    depth = None

    def __init__(self, conceptid, parentid, descriptionid, active=True):
        self.conceptid = conceptid
        self.parentid = parentid
        self.descriptionid = descriptionid
        self.active = active
        self.depth = get_depth(conceptid)


G = nx.DiGraph()
request_count = 0
granddad_id = "138875005"  # id for root node (272625005, 272379006), snomed root: 138875005
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
def get_descriptionid_byconceptid(conceptid):
    params = {"conceptId": conceptid}
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


# RA
def get_descendant_count(conceptid):
    params = {"conceptId": conceptid}
    response = requests.get(
        "https://snowstorm.test-nictiz.nl/browser/MAIN/concepts/" + conceptid +
        "?descendantCountForm=additional", params=params)

    resp = response.json()
    return str(resp["descendantCount"])


# des_count_liver = get_descendant_count("10200004")


# KK
def get_children(conceptid):
    params = {"conceptId": conceptid}
    response = request_snowstorm_burst(
        "https://snowstorm.test-nictiz.nl/browser/MAIN/concepts/" + conceptid +
        "/children?form =inferred&includeDescendantCount=false", params=params)
    return response.json()


# MD: get IDs of children nodes instead of entire children nodes
def get_children_ids(conceptid):
    params = {"conceptId": str(conceptid)}
    response = request_snowstorm_burst(
        "https://snowstorm.test-nictiz.nl/browser/MAIN/concepts/" + str(conceptid) +
        "/children?form =inferred&includeDescendantCount=false", params=params)
    children = response.json()
    children_ids = []
    for child in children:
        children_ids.append(child['conceptId'])
    return children_ids


# print(get_children_ids(granddad_id))
# print(len(get_children_ids("409766009")))  # node with no children -> len = 0


# KK
def get_parents_ids(conceptid):
    params = {"conceptId": conceptid}
    response = request_snowstorm_burst(
        "https://snowstorm.test-nictiz.nl/browser/MAIN/concepts/" + conceptid +
        "/parents?form=inferred&includeDescendantCount=false", params=params)
    return response.json()


def get_conceptid_by_term(term):
    try:
        response = requests.get(
            "https://snowstorm.test-nictiz.nl/MAIN/concepts?term=" + term + "%20&offset=0&limit=50")
        return response.json()["items"][0].get("conceptId")
    except IndexError:
        return None


# MD: find lowest common parent for two nodes
def get_common_parent(conceptid_1, conceptid_2):
    if conceptid_1 == conceptid_2 or conceptid_1 == granddad_id or conceptid_2 == granddad_id:
        return conceptid_1
    else:
        list_1 = walk_to_granddad(conceptid_1)
        list_2 = walk_to_granddad(conceptid_2)
        # consider re-writing this in case of runtime issues
        for i in list_1:
            for j in list_2:
                if i == j:
                    return i
        return None
        # if None is ever returned, something is really wrong


# MD: method that returns the ID of a parent node rather than the entire parent node
def get_parent_id_only(conceptid):
    params = {"conceptId": conceptid}
    response = request_snowstorm_burst(
        "https://snowstorm.test-nictiz.nl/browser/MAIN/concepts/" + conceptid +
        "/parents", params=params)
    return response.json()[0]['conceptId']


# MD: a method that saves all nodes traversed on a path from a conceptid to SNOMED root to a list and returns it
# includes both conceptid and granddad_id
def walk_to_granddad(conceptid):
    nodes_list = []
    while conceptid != granddad_id:
        nodes_list.append(conceptid)
        conceptid = get_parent_id_only(conceptid)
    nodes_list.append(granddad_id)
    return nodes_list


# MD: a method that saves all nodes traversed on a path from a conceptid to a given ancestor node to a list
# and returns it. conceptid is included, ancestor id is not included
def walk_to_ancestor(conceptid_start, ancestorid):
    nodes_list = []
    conceptid = conceptid_start
    cutoff = 0
    while conceptid != ancestorid and cutoff < 500:
        nodes_list.append(conceptid)
        conceptid = get_parent_id_only(conceptid)
        cutoff += 1
    return nodes_list


#print(get_common_parent("266474003", "197402000"))  # should print 404684003 (Clinical finding)


# MD: create a graph ranging from two conceptids to their lowest common parent
def create_spanning_tree(conceptid_1, conceptid_2):
    tree_root = get_common_parent(conceptid_1, conceptid_2)
    path_node1 = walk_to_ancestor(conceptid_1, tree_root)
    path_node2 = walk_to_ancestor(conceptid_2, tree_root)
    G_span = nx.DiGraph()
    G_span.add_node(tree_root)
    current_knot = tree_root
    # for both paths, add node from current knot (at start: lowest common parent) to last element of list
    # last element of list becomes current knot and is removed afterwards. continue until list empty
    while len(path_node1) > 0:
        G_span.add_edge(current_knot, path_node1[(len(path_node1)-1)], weight=1.0, capacity=1.0)
        G_span.add_edge(path_node1[(len(path_node1) - 1)], current_knot, weight=1.0, capacity=1.0)
        current_knot = path_node1[(len(path_node1)-1)]
        del path_node1[-1]
    current_knot = tree_root
    while len(path_node2) > 0:
        G_span.add_edge(current_knot, path_node2[(len(path_node2)-1)], weight=1.0, capacity=1.0)
        G_span.add_edge(path_node2[(len(path_node2) - 1)], current_knot,  weight=1.0, capacity=1.0)
        current_knot = path_node2[(len(path_node2)-1)]
        del path_node2[-1]

    return G_span


color_map = []
# example_node = get_common_parent("266474003", "197402000")
# G_span = create_spanning_tree("266474003", "197402000")
# for node in G_span:
#   if node == granddad_id:
#        color_map.append("red")  # root node will be colored red (if exists in graph)
#    elif node == example_node:
#        color_map.append("green")  # example node (lowest common parent) marked green
#    else:
#        color_map.append("blue")  # other nodes will be colored blue

# nx.draw_networkx(G_span, node_color=color_map)  # draw graph
# plt.show()


# LA / MD: write graph or parts of it to a csv file
def write_graph_to_csv():
    index = 0
    children = get_children_ids(granddad_id)
    children_todo = []
    with open('graph.csv', 'w', newline='') as csvfile:
        graphwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        graphwriter.writerow({granddad_id + get_node_row(granddad_id)})
        count = 1000
        foo = True
        while foo or (len(children_todo) > 0 and count > 0):
            foo = False
            print(count)
            children_todo = []
            for child in children:
                children_row = get_node_row(child)
                graphwriter.writerow({child + children_row})
                if len(children_row) > 0:
                    children_todo.extend(get_node_row_list(children_row[1:len(children_row)]))  # omit comma
            children = children_todo
            count = count - 1

    print("(Should be) done writing!", count)


def get_node_row(conceptid):
    children = get_children_ids(conceptid)
    children_string = ""
    for child in children:
        children_string += "," + child

    return children_string


def get_node_row_list(node_row):
    children_list = []
    for child in node_row.split(","):
        children_list.append(child)
    return children_list

#KK :read csv file ,with droping first empty column
def get_Ihccontology_as_df():
    df = pd.read_csv("ihCCOntology_Excerpt.csv")
    df_after_dropping = df.drop(df.columns[0], axis=1, inplace=True)
    return df

#KK:getting just all parameter name
def get_all_parameternames():
    return get_Ihccontology_as_df()["Parametername"]

#KK:check if path to granddad without unexpected glichtes is built
def check_possible_parent(conceptid):
    try:
        walk_to_granddad(conceptid)
        return True
    except KeyError:
        return False
    except ValueError:
        return False

#KK:find concept id for each parameter name and save in new column
def get_parameternames_with_conceptids():
    Parameternames = list(get_all_parameternames())
    conceptids = list()
    for term in Parameternames:
        conceptids.append(get_conceptid_by_term(term))
    df = pd.DataFrame(list(zip(Parameternames, conceptids)),
                      columns=['Parametername', 'conceptid'])
    return df

#KK: save all edges sources and targets of parameters in DataFrame to suit with a from_pandas_edgelist function
def get_all_edges_between_parameters():
    df = get_parameternames_with_conceptids()
    not_found_concepts = df[(df["conceptid"].isnull())]
    df = df.dropna()
    failed_request = []
    paths = []
    for i in df["conceptid"]:
        if check_possible_parent(i):
            single_list = walk_to_granddad(i)
            paths.append(single_list)
        else:
            failed_request.append(i)
    sources = []
    targets = []

    for m in paths:
        for n in range(len(m)):
            try:
                targets.append(m[n + 1])
                sources.append(m[n])
            except IndexError:
                continue

    sources_as_series = pd.Series(sources)
    targets_as_series = pd.Series(targets)
    edges = pd.DataFrame({"source": sources_as_series.values, "target": targets_as_series.values})
    print("Not Found", not_found_concepts)
    print("Failed request", failed_request)
    return edges


#write_graph_to_csv()
get_all_edges_between_parameters()
# to calculate the distance between parameters you can use get_distance_between_two_nodes from Dashboard
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
print("depth 1: ", get_depth("83299001"))
print("depth 2: ", get_depth("307824009"))

# print(get_parents_ids("370136006")[0]['conceptId'])

# Filling graph
# --------------------
# add height levels of nodes connected to node "conceptid" recursively to graph
# height: additional steps from root node (does not work for 0!)


def add_children_to_graph_recursive(conceptid, height):
    if height > 0:
        children_ids = get_children_ids(conceptid)  # get ids of children of current node
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



# RA:
# adds the first found id to the entered dataframe using the function "find_concepts"
def add_first_id_found(file):
    counter = 0
    for x in file["Parametername"]:
        datas = find_concepts(file.loc[counter][0])
        # if something was found
        if(len(datas['items']) > 0):
#             print(datas["items"][0]["id"],datas["items"][0]["fsn"]["term"], '\t',  file.loc[counter][1])
            #create new columns and enter the first id and term
            file.loc[counter,['id']] = datas["items"][0]["id"]
            file.loc[counter,['term']] = datas["items"][0]["fsn"]["term"]

        counter += 1

    return(file)

# read csv file
# ihCCOntology_Excerpt = pd.read_csv('ihCCOntology_Excerpt.csv')
# ihCCOntology_Excerpt.drop(columns=['Unnamed: 0'], inplace=True)

# ihc = add_first_id_found(ihCCOntology_Excerpt)
# print(ihc)



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




