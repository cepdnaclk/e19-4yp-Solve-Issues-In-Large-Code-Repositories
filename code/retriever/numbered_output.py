   1: """
   2: * Author: Lahiru Menikdiwela
   3: * Email: lahirumenik@gmail.com
   4: ___________________________________________________________
   5: * Date: Sat Apr 26 2025
   6: 
   7: """
   8:             
   9: 
  10: # Added by AI
  11: def foo():
  12:     print('Hello')
  13:     return
  14: # !!!
  15: 
  16: import git
  17: import sys
  18: import networkx as nx
  19: import pickle
  20: import re
  21: import os
  22: from utils import utils
  23: from utils.embed_skeleton import get_skeleton
  24: import ast
  25: import faiss
  26: from dotenv import load_dotenv
  27: from langchain.embeddings import OpenAIEmbeddings
  28: from langchain_community.docstore.in_memory import InMemoryDocstore
  29: from langchain_community.vectorstores import FAISS
  30: from langchain_core.documents import Document
  31: 
  32: 
  33: def neighbors_by_relation(G, node, relation_type):
  34:     
  35:     neighbors = []
  36:     for u, v, data in G.edges(node, data=True):
  37:         if data.get('relation') == relation_type:
  38:             neighbor = v if u == node else u  # Handle undirected edges
  39:             neighbors.append(neighbor)
  40:     return neighbors
  41: 
  42: 
  43: 
  44: 
  45: def find_function_or_class(path, name, graph):
  46:     files = neighbors_by_relation(graph, "class_"+name, "class_path")
  47:     for p in files:
  48:         if p.startswith(path):
  49:             return p
  50:     return 
  51: 
  52: def filter_import_lines(code_lines):
  53:     if isinstance(code_lines, str):
  54:         lines = code_lines.splitlines()
  55:     else:
  56:         lines = code_lines
  57: 
  58:     import_pattern = re.compile(r'^\s*(import\s+\w|from\s+\w+(\.\w+)*\s+import\s+)')
  59:     return "\n".join(line for line in lines if import_pattern.match(line.strip()))
  60: 
  61: def extract_imports(base, file_path, graph):
  62:     try:
  63:         with open(file_path, "r", encoding="utf-8") as f:
  64:             tree = ast.parse(f.read(), filename=file_path)
  65:     except:
  66:         return set()
  67:     imports = set()
  68:     for node in ast.walk(tree):
  69:         if isinstance(node, ast.Import):
  70:             pass
  71:         elif isinstance(node, ast.ImportFrom) and node.module:
  72:             if node.level > 0:
  73:                 path_arr = file_path.split("/")
  74:                 for i in range(node.level):
  75:                     path_arr.pop()
  76:                 path = "/".join(path_arr)
  77:                 node.module = path[len(base):]
  78:           
  79:                 
  80:             for alias in node.names:
  81:                 if os.path.exists(base + node.module.replace(".", "/")+ "/" + alias.name+".py"):
  82:                         imports.add(base + node.module.replace(".", "/")+ "/" + alias.name+".py")
  83:                 else:
  84:                     if os.path.exists(base +node.module.replace(".", "/") +".py"):#name in file_map:
  85:                         imports.add(base +node.module.replace(".", "/") +".py")
  86:                     else:
  87:                         found_name = find_function_or_class(base+node.module.replace(".", "/"), alias.name, graph=graph)
  88:                         if found_name:
  89:                             imports.add(found_name)
  90:     return imports
  91: 
  92: def update_class_functions_file(files, graph):
  93:     for file_path in files:
  94:             if file_path.endswith(".py"):
  95:                 try:
  96:                     with open(file_path, "r", encoding="utf-8") as f:
  97:                         tree = ast.parse(f.read(), filename=file_path)
  98:                     for node in ast.walk(tree):
  99:                         if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
 100:                             if node.name:
 101:                                 insert_edge(graph, "class_"+node.name, file_path, relation="class_path", node_type_v="full_path", node_type_u="class_function")
 102:                 except Exception as e:
 103:                     print(f"Error reading {file_path}: {e}")
 104:     return
 105:     
 106:     
 107: 
 108: def load_graph(pickle_path):
 109:     """Loads a NetworkX DiGraph from a pickle file."""
 110:     with open(pickle_path, "rb") as f:
 111:         graph = pickle.load(f)
 112:     return graph
 113: 
 114: def save_graph(graph, pickle_path):
 115:     """Saves the updated NetworkX DiGraph to a pickle file."""
 116:     with open(pickle_path, "wb") as f:
 117:         pickle.dump(graph, f)
 118: 
 119: 
 120: def checkout_commit(repo_path, base_commit):
 121:     repo = git.Repo(repo_path)
 122:     repo.git.checkout(base_commit)
 123:     print(f"Checked out to {base_commit}")
 124:     
 125:     
 126: 
 127: def insert_edge(G, u, v, relation=None, node_type_v=None, node_type_u=None):
 128:     if not G.has_node(u):
 129:         G.add_node(u, type=node_type_u)
 130:     if not G.has_node(v):
 131:         G.add_node(v, type=node_type_v)
 132: 
 133:     edge_attrs = {}
 134:     if relation:
 135:         edge_attrs['relation'] = relation
 136: 
 137:     G.add_edge(u, v, **edge_attrs)
 138:     
 139: def delete_node_and_edges(G, node):
 140:     if G.has_node(node):
 141:         G.remove_node(node)
 142:         return True
 143:     else:
 144:         print(f"Node '{node}' does not exist.")
 145:         return False
 146: def remove_isolated_nodes(G):
 147:     isolated = list(nx.isolates(G))
 148:     G.remove_nodes_from(isolated)
 149:     return isolated
 150: 
 151: def update(repo_path, latest_commit):
 152:     load_dotenv()
 153:     embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
 154:     repo = git.Repo(repo_path)
 155:     repo_name = repo_path #repo_path.split("/")[-2]
 156:     repo_path = repo_path+"/"
 157:     file_ids = utils.deserialize_json_to_dict(f"{repo_name}_file_ids.json")
 158:     print(repo_name)
 159:     base_commit = repo.head.commit.hexsha  # Get the latest commit hash
 160:     graph = load_graph(f"graph_{repo_name}.pkl")
 161:     print(graph)
 162:     diff_index = repo.git.diff('--name-status', base_commit, latest_commit)
 163:     vector_store = FAISS.load_local(
 164:     f"{repo_name}_faiss_index", embeddings, allow_dangerous_deserialization=True
 165:     )
 166:     
 167: 
 168:     renamed_files = {}
 169:     added_files = []
 170:     deleted_files = []
 171:     
 172:     
 173:     for line in diff_index.split("\n"):
 174:         if not line.strip():
 175:             continue
 176:         parts = line.split("\t")
 177:         change_type = parts[0]
 178:         
 179:         if change_type.startswith("R"):  # Renamed file
 180:             old_name = parts[1]
 181:             new_name = parts[2]
 182:             renamed_files[repo_path + old_name] = repo_path + new_name
 183:             added_files.append(repo_path+new_name)
 184:             deleted_files.append(repo_path+old_name)
 185:     
 186:         if change_type == "M":  # Modified file
 187:             # changed_files.append(repo_path+parts[1])
 188:             deleted_files.append(repo_path+parts[1])
 189:             added_files.append(repo_path+parts[1])
 190:         if change_type == "A":  # Added file
 191:             added_files.append(repo_path+parts[1])
 192:         if change_type == "D":  # Deleted file
 193:             deleted_files.append(repo_path+parts[1])
 194:     
 195:     delete_ids_vc = []
 196:     for file in deleted_files:
 197:         if not file.endswith(".py"):
 198:             continue
 199:         delete_node_and_edges(graph, file)
 200:         if file in file_ids:
 201:             id = file_ids[file]
 202:             del file_ids[file]
 203:             delete_ids_vc.append(id)
 204:             vector_store.delete([id])
 205:     utils.serialize_dict_to_json(file_ids, f"{repo_name}_file_ids.json")
 206:     checkout_commit(repo_path, latest_commit)    
 207:     update_class_functions_file(added_files, graph) 
 208:     
 209:     for file in added_files:
 210:         if not file.endswith(".py"):
 211:             continue
 212:         if file in renamed_files:
 213:             file = renamed_files[file_path]
 214:         # print("kk")
 215:         name = file.split("/")[-1].split(".")[0]
 216:         # print(repo_path+file)
 217:         insert_edge(graph, "module_"+name, file, relation="path", node_type_v="full_path", node_type_u="module_name")
 218:     
 219:     documents_vc = [] 
 220:     id_vc = []
 221:     for file_path in added_files:
 222:         if not file_path.endswith(".py"):
 223:             continue
 224:         try:
 225:             with open(file_path, "r") as f:
 226:                 content = f.read()
 227:             if content:
 228:                 sketch = get_skeleton(content, keep_constant = False, keep_indent=True, total_lines =30, prefix_lines=15,suffix_lines=10)
 229:                 doc = Document(page_content= sketch, metadata = {"filename": file_path})
 230:                 if delete_ids_vc:
 231:                     id = delete_ids_vc.pop(0)
 232:                 else:
 233:                     id = max(file_ids.values()) + 1
 234:                 file_ids[file_path] = id
 235:                 documents_vc.append(doc)
 236:                 id_vc.append(id)
 237:         except Exception as e:
 238:             print(f"[!] Error adding file '{file_path}': {e}")
 239:         # print(file_path, "kk")
 240:         if file_path in renamed_files:
 241:             file_path = renamed_files[file_path]
 242:         if not file_path.endswith(".py"):
 243:             continue
 244:         import_files = extract_imports(repo_path, file_path, graph)
 245:         # print("j", import_files)
 246:                 
 247:         for i in import_files:
 248:             # print(i)
 249:             if not i.endswith(".py"):
 250:                 continue
 251:             insert_edge(graph, file_path, i, relation="imports", node_type_v="full_path", node_type_u="full_path")
 252:     if documents_vc and id_vc:
 253:         vector_store.add_documents(documents=documents_vc, ids=id_vc)
 254:         vector_store.save_local(f"{repo_name}_faiss_index")
 255:         utils.serialize_dict_to_json(file_ids, f"{repo_name}_file_ids.json")
 256:     remove_isolated_nodes(graph)         
 257:     print(graph)
 258:     save_graph(graph, f"graph_{repo_name}.pkl")
 259:     # checkout_commit(repo_path, latest_commit)
 260: 
 261:     return
 262: repo_name = "django"
 263: repo_path = f"test/{repo_name}/"
 264: # ch, ren, ad, de, import_ch, import_dict, import_delete_dict = 
 265: # update(repo_path, "b34751b7ed02b2cfcc36037fb729d4360480a299")
 266: # checkout_commit("django", "66f9eb0ff1e7147406318c5ba609729678e4e6f6")
 267: 
