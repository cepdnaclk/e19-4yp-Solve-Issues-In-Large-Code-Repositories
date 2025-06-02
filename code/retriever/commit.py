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
import ast
import chromadb
import traceback
# import faiss
# from utils.embed_skeleton import get_skeleton
from utils.chunk import SimpleFixedLengthChunker
from collections import deque
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from langchain_chroma import Chroma
# from langchain_community.vectorstores import FAISS


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
    repo_name = repo_path #repo_path.split("/")[-2]
    repo_path = repo_path+"/"
    file_ids = utils.deserialize_json_to_dict(f"{repo_name}_file_ids.json")

    print(repo_name)

    base_commit = repo.head.commit.hexsha  # Get the latest commit hash
    graph = load_graph(f"graph_{repo_name}.pkl")

    print(graph)
    
    diff_index = repo.git.diff('--name-status', base_commit, latest_commit)

    chroma_client = chromadb.PersistentClient(f"chroma_db")
    collection = chroma_client.get_collection(name=f"{repo_name}_chroma_index")

    vector_store = Chroma(
        client=chroma_client,
        collection_name=f"{repo_name}_chroma_index",
        embedding_function=embeddings,
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
    
    delete_ids_vc = deque([])

    for file in deleted_files:
        if not file.endswith(".py"):
            continue
        delete_node_and_edges(graph, file)
        if file in file_ids:
            ids = file_ids[file]
            del file_ids[file]
            for i in ids.split(":"):
                delete_ids_vc.append(i)

    if delete_ids_vc:
        batch_ids = []
        try:
            if len(delete_ids_vc) > chroma_client.get_max_batch_size():
                batch_size = 4000
            else:
                batch_size = len(delete_ids_vc)
            for i in range(0, len(delete_ids_vc), batch_size):
                batch_ids = list(delete_ids_vc)[i:i+batch_size]
                vector_store.delete(batch_ids)
        except Exception as e:
            traceback.print_exc()

    utils.serialize_dict_to_json(file_ids, f"{repo_name}_file_ids.json")
    checkout_commit(repo_path, latest_commit)    
    update_class_functions_file(added_files, graph) 
    
    documents_vc = [] 
    id_vc = []
    # max_id = max(int(num) for val in file_ids.values() for num in val.split(":")) + 1
    max_id = file_ids["max_id"] + 1
    for file_path in added_files:
        if not file_path.endswith(".py"):
            continue
        name = file.split("/")[-1].split(".")[0]
        # print(repo_path+file)
        insert_edge(graph, "module_"+name, file, relation="path", node_type_v="full_path", node_type_u="module_name")
        try:
            # TODO: Use Multi Threding to Chunk each File Parallely
            chunker = SimpleFixedLengthChunker()
            with open(file_path, "r") as f:
                content = f.read()
            if content:
                if "tests" in file_path.split("/") or "test" in file_path.split("/"):
                    # print("from comit test")
                    continue
                chunks = chunker.chunk_file(code=content)
                if chunks:
                    chunk_ids = []
                    for chunk in chunks:
                        doc = Document(page_content=chunk, metadata={"filename": file_path})
                        if delete_ids_vc:
                            id = delete_ids_vc.popleft()
                        else:
                            id = max_id
                            max_id += 1
                        chunk_ids.append(str(id))
                        documents_vc.append(doc)
                        id_vc.append(str(id))
                    file_ids[file_path] = ":".join(chunk_ids)
        except Exception as e:
            print(f"[!] Error adding file '{file_path}': {e}")
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

    if documents_vc and id_vc:
        batch_ids = []
        try:
            if len(documents_vc) > chroma_client.get_max_batch_size():
                batch_size = 4000
            else:
                batch_size = len(documents_vc)
            for i in range(0, len(documents_vc), batch_size):
                batch_documents = documents_vc[i:i+batch_size]
                batch_ids = id_vc[i:i+batch_size]
                vector_store.add_documents(documents=batch_documents, ids=batch_ids)
        except Exception as e:
            traceback.print_exc()
    
        # vector_store.save_local(f"{repo_name}_chroma_index")
    file_ids["max_id"] = max_id
    utils.serialize_dict_to_json(file_ids, f"{repo_name}_file_ids.json")
    remove_isolated_nodes(graph)         
    print(graph)
    save_graph(graph, f"graph_{repo_name}.pkl")
    # checkout_commit(repo_path, latest_commit)

    return

repo_name = "django"
repo_path = f"test/{repo_name}/"
# ch, ren, ad, de, import_ch, import_dict, import_delete_dict = 
# update(repo_path, "b34751b7ed02b2cfcc36037fb729d4360480a299")
# checkout_commit("django", "66f9eb0ff1e7147406318c5ba609729678e4e6f6")

