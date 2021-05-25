import zipfile
from io import StringIO, BytesIO

import requests
import csv
granddad_id = "138875005"


# doesn't actually burst, but we are too lazy to rewrite the other methods
def request_snowstorm_burst(url, params):
    return requests.get(url, params)


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


def write_graph_to_csv():
    children = get_children_ids(granddad_id)
    with open('graph_keno.csv', 'w', newline='') as csvfile:
        graphwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        graphwriter.writerow({granddad_id + get_node_row(granddad_id)})
        killswitch = 500000  # -> max number of rows
        while len(children) > 0 and killswitch > 0:
            children_todo = []
            for child in children:
                children_row = get_node_row(child)
                graphwriter.writerow({child + children_row})
                killswitch = killswitch - 1
                if len(children_row) > 0:
                    children_todo.extend(get_node_row_list(children_row[1:len(children_row)]))  # omit comma
            children = children_todo


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


write_graph_to_csv()
