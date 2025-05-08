"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat Apr 26 2025

"""
            

import git
import sys
import networkx as nx
import pickle
import re
import os
from utils import utils
from utils.embed_skeleton import get_skeleton
import ast
import faiss
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

repo_name = "scikit-learn"

def neighbors_by_relation(G, node, relation_type):
    
    neighbors = []
    for u, v, data in G.edges(node, data=True):
        if data.get('relation') == relation_type:
            neighbor = v if u == node else u  # Handle undirected edges
            neighbors.append(neighbor)
    return neighbors




def find_function_or_class(path, name, graph):
    files = neighbors_by_relation(graph, "class_"+name, "class_path")
    for p in files:
        if p.startswith(path):
            return p
    return 

def filter_import_lines(code_lines):
    if isinstance(code_lines, str):
        lines = code_lines.splitlines()
    else:
        lines = code_lines

    import_pattern = re.compile(r'^\s*(import\s+\w|from\s+\w+(\.\w+)*\s+import\s+)')
    return "\n".join(line for line in lines if import_pattern.match(line.strip()))

def extract_imports(base, file_path, graph):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
    except:
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
                        found_name = find_function_or_class(base+node.module.replace(".", "/"), alias.name, graph=graph)
                        if found_name:
                            imports.add(found_name)
    return imports

def update_class_functions_file(files, graph):
    for file_path in files:
            if file_path.endswith(".py"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=file_path)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            if node.name:
                                insert_edge(graph, "class_"+node.name, file_path, relation="class_path", node_type_v="full_path", node_type_u="class_function")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return
    
    

def load_graph(pickle_path):
    """Loads a NetworkX DiGraph from a pickle file."""
    with open(pickle_path, "rb") as f:
        graph = pickle.load(f)
    return graph

def save_graph(graph, pickle_path):
    """Saves the updated NetworkX DiGraph to a pickle file."""
    with open(pickle_path, "wb") as f:
        pickle.dump(graph, f)


def checkout_commit(repo_path, base_commit):
    repo = git.Repo(repo_path)
    repo.git.checkout(base_commit)
    print(f"Checked out to {base_commit}")
    
    

def insert_edge(G, u, v, relation=None, node_type_v=None, node_type_u=None):
    if not G.has_node(u):
        G.add_node(u, type=node_type_u)
    if not G.has_node(v):
        G.add_node(v, type=node_type_v)

    edge_attrs = {}
    if relation:
        edge_attrs['relation'] = relation

    G.add_edge(u, v, **edge_attrs)
    
def delete_node_and_edges(G, node):
    if G.has_node(node):
        G.remove_node(node)
        return True
    else:
        print(f"Node '{node}' does not exist.")
        return False
def remove_isolated_nodes(G):
    isolated = list(nx.isolates(G))
    G.remove_nodes_from(isolated)
    return isolated

def update(repo_path, latest_commit):
    load_dotenv()
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    repo = git.Repo(repo_path)
    repo_name = repo_path.split("/")[-2]
    file_ids = utils.deserialize_json_to_dict(f"{repo_name}_file_ids.json")
    print(repo_name)
    base_commit = repo.head.commit.hexsha  # Get the latest commit hash
    graph = load_graph(f"../new_graph_{repo_name}.pkl")
    print(graph)
    diff_index = repo.git.diff('--name-status', base_commit, latest_commit)
    vector_store = FAISS.load_local(
    f"{repo_name}_faiss_index", embeddings, allow_dangerous_deserialization=True
    )
    

    renamed_files = {}
    added_files = []
    deleted_files = []
    
    
    for line in diff_index.split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        change_type = parts[0]
        
        if change_type.startswith("R"):  # Renamed file
            old_name = parts[1]
            new_name = parts[2]
            renamed_files[repo_path + old_name] = repo_path + new_name
            added_files.append(repo_path+new_name)
            deleted_files.append(repo_path+old_name)
    
        if change_type == "M":  # Modified file
            # changed_files.append(repo_path+parts[1])
            deleted_files.append(repo_path+parts[1])
            added_files.append(repo_path+parts[1])
        if change_type == "A":  # Added file
            added_files.append(repo_path+parts[1])
        if change_type == "D":  # Deleted file
            deleted_files.append(repo_path+parts[1])
    
    delete_ids_vc = []
    for file in deleted_files:
        if not file.endswith(".py"):
            continue
        delete_node_and_edges(graph, file)
        id = file_ids[file]
        delete_ids_vc.append(id)
        vector_store.delete([id])
    checkout_commit(repo_path, latest_commit)    
    update_class_functions_file(added_files, graph) 
    
    for file in added_files:
        if not file.endswith(".py"):
            continue
        if file in renamed_files:
            file = renamed_files[file_path]
        # print("kk")
        name = file.split("/")[-1].split(".")[0]
        # print(repo_path+file)
        insert_edge(graph, "module_"+name, file, relation="path", node_type_v="full_path", node_type_u="module_name")
    
    documents_vc = [] 
    id_vc = []
    for file_path in added_files:
        with open(file_path, "r") as f:
            content = f.read()
        if sketch:
            sketch = get_skeleton(content, keep_constant = False, keep_indent=True, total_lines =30, prefix_lines=15,suffix_lines=10)
            doc = Document(page_content= sketch, metadata = {"filename": file_path})
            if delete_ids_vc:
                id = delete_ids_vc.pop(0)
            else:
                id = max(file_ids.values()) + 1
            file_ids[file_path] = id
            documents_vc.append(doc)
            id_vc.append(id)
        
        # print(file_path, "kk")
        if file_path in renamed_files:
            file_path = renamed_files[file_path]
        if not file_path.endswith(".py"):
            continue
        import_files = extract_imports(repo_path, file_path, graph)
        # print("j", import_files)
                
        for i in import_files:
            # print(i)
            if not i.endswith(".py"):
                continue
            insert_edge(graph, file_path, i, relation="imports", node_type_v="full_path", node_type_u="full_path")
    vector_store.add_documents(documents=documents_vc, ids=id_vc)
    vector_store.save_local(f"{repo_name}_faiss_index")
    remove_isolated_nodes(graph)         
    print(graph)
    save_graph(graph, f"new_graph_{repo_name}.pkl")
    # checkout_commit(repo_path, latest_commit)

    return
repo_name = "django"
repo_path = f"test/{repo_name}/"
# ch, ren, ad, de, import_ch, import_dict, import_delete_dict = 
# update(repo_path, "b34751b7ed02b2cfcc36037fb729d4360480a299")
# checkout_commit("test/django", "66f9eb0ff1e7147406318c5ba609729678e4e6f6")
