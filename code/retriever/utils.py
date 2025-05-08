"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat Apr 25 2025

"""

def neighbors_by_relation(G, node, relation_type):
    
    neighbors = []
    for u, v, data in G.edges(node, data=True):
        if data.get('relation') == relation_type:
            neighbor = v if u == node else u 
            neighbors.append(neighbor)
    return neighbors