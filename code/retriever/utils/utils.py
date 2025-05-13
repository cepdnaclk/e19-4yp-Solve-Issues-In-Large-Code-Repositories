"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat Apr 25 2025

"""

import os
import git
import networkx as nx

def neighbors_by_relation(G, node, relation_type):
    
    neighbors = []
    for u, v, data in G.edges(node, data=True):
        if data.get('relation') == relation_type:
            neighbor = v if u == node else u 
            neighbors.append(neighbor)
    return neighbors

def find_function_or_class(path, name, graph):
    files = neighbors_by_relation(graph, "class_"+name, "class_path")
    for p in files:
        if p.startswith(path):
            return p          
    return 

def checkout_commit(repo_path, base_commit):
    repo = git.Repo(repo_path)
    repo.git.checkout(base_commit)
    print(f"Checked out to {base_commit}")
    
import json

def serialize_dict_to_json(data: dict, filename: str):
    """
    Serializes a dictionary into a JSON file.
    :param data: Dictionary with string keys and list values
    :param filename: Name of the JSON file to store data
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def deserialize_json_to_dict(filename: str) -> dict:
    """
    Deserializes a JSON file back into a dictionary.
    :param filename: Name of the JSON file to read data from
    :return: Dictionary with string keys and list values
    """
    with open(filename, 'r') as f:
        return json.load(f)
