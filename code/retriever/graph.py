
import os
import ast
import networkx as nx
import matplotlib.pyplot as plt
import pickle

repo_name = "django"

def get_rel_fname(fname, root):
    return os.path.relpath(fname, root)

def serialize_function_or_class():
    path = repo_name
    class_func_dict = {}
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # print(file_path)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=file_path)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):#and file_path.split("/")[-1]!="__init__.py":
                            if node.name not in class_func_dict:
                                class_func_dict[node.name] = []
                            class_func_dict[node.name].append(file_path)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    # serialize.serialize_dict_to_json(class_func_dict, f"class_func_dict_{repo_name}.json")
    return class_func_dict

def find_function_or_class(path, name, class_function_map):
    if name in class_function_map:
        for p in class_function_map[name]:
            if p.startswith(path):
                return p
    return 


def extract_imports(file_path, class_fuction_map):
    base = f"{repo_name}/"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
    except:
        print("error", file_path)
        return set()
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            pass
           
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.level > 0:
                path_arr = file_path.split("/")
                for i in range(node.level):
                    path_arr.pop()
                path = "/".join(path_arr)
                node.module = path[len(base):]
          
                
            for alias in node.names:
                if os.path.exists(base + node.module.replace(".", "/")+ "/" + alias.name+".py"):
                    imports.add(base + node.module.replace(".", "/")+ "/" + alias.name+".py")
                        
                else:
                    if os.path.exists(base +node.module.replace(".", "/") +".py"):#name in file_map:
                        imports.add(base +node.module.replace(".", "/") +".py")
                    else:
                        found_name = find_function_or_class(base+node.module.replace(".", "/"), alias.name, class_function_map=class_fuction_map)
                        if found_name:
                            # print("p")
                            imports.add(found_name)
                      
    return imports


    



def build_dependency_graph(repo_path, class_function_map):
    graph = nx.DiGraph()
    file_map = {}  # Map module names to file paths
    full_path_arr = set()

    # Traverse repository and collect files
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]
                if module_name not in file_map:
                    file_map[module_name] = []
                file_map[module_name].append(full_path)
                full_path_arr.add(full_path)
                graph.add_node(full_path, type='full_path')
    
    
    for file_path in full_path_arr:
        imports = extract_imports(file_path, class_function_map)
        for imp in imports:
            graph.add_edge(file_path, imp, relation = 'imports')
    print("imp gra", graph)
    for key in file_map:
        graph.add_node("module_"+key, type='module_name')
        for full_path in file_map[key]:
            graph.add_edge("module_"+key, full_path, relation = 'path')
    return graph


from pyvis.network import Network

def visualize_graph(graph):
    net = Network(height="850px", width="100%", directed=True, notebook=True)
    
    for node in graph.nodes:
        net.add_node(node, label=node.split("/")[-1], title=node)

    for src, dst in graph.edges:
        net.add_edge(src, dst)

    net.show(f"dependency_graph_{repo_name}.html")







def built(repo_path):
    class_func_map = serialize_function_or_class()
    graph = build_dependency_graph(repo_path, class_func_map)
    for name in class_func_map:
        graph.add_node("class_"+name, type='class_function')
        for file_path in class_func_map[name]:
            # print(file_path)
            graph.add_edge("class_"+name, file_path, relation = 'class_path')
    
    print(graph)
    with open(f"graph_{repo_name}.pkl", "wb") as f:
       pickle.dump(graph, f)
    return graph


# Run on a repository
repo_path = repo_name
graph = built(repo_path)



def neighbors_by_relation(G, node, relation_type):
    
    neighbors = []
    for u, v, data in G.edges(node, data=True):
        if data.get('relation') == relation_type:
            neighbor = v if u == node else u  # Handle undirected edges
            neighbors.append(neighbor)
    return neighbors

