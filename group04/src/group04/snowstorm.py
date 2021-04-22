import requests
import networkx as nx
import matplotlib.pyplot as plt
G = nx.DiGraph()
def find_concepts(keyword: str) -> dict:
    params = {"term": keyword}
    response = requests.get(
        "https://snowstorm.test-nictiz.nl/MAIN/concepts", params=params
    )
    return response.json()

# KK
def get_descriptionid_byconceptid(Conceptid):
    response = requests.get(
        "https://snowstorm.test-nictiz.nl/MAIN/descriptions?", params={"conceptId": Conceptid})

    return response.json()

# KK
def get_childern_ids(conceptid):
    response = requests.get(
        "https://snowstorm.test-nictiz.nl/browser/MAIN/concepts/" + conceptid + "/children?form =inferred&includeDescendantCount=false")
    return response.json()

# KK
childernids = get_childern_ids("10200004")
for childid in childernids:
    G.add_edge("10200004", childid['conceptId'], capacity=1.0)
    # print(childid["conceptId"])

# KK
descriptionids = get_descriptionid_byconceptid(10200004)
for descid in descriptionids["items"]:
    print(descid["descriptionId"])


name = 'liver'

concepts = find_concepts(name)
for concept in concepts["items"]:
    # G.add_edge(name, concept['conceptId'], capacity=1.0)
    # name = concept["pt"]["term"]
    print("#" + concept["id"] + ": " + concept["fsn"]["term"])
    # flow_value, flow_dict = nx.maximum_flow(G, name, concept["pt"]["term"])
    # print(flow_value)
    # print(flow_dict)

nx.draw_networkx(G)
plt.show()

# starting point
# 272625005 # Entire body organ (PT)



