"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat Apr 25 2025

"""

import os
import git
import networkx as nx
from typing import Annotated, List, Dict
import re

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

def is_invalid_path(file_path):
    """
    Check if the file path provided is useful to be analysed or added to the dependecy graph.
    Modify this when you want to change the logic.
    """
    return not file_path.endswith(".py") or \
            "tests" in file_path.split("/") or \
                "test" in file_path.split("/")
                
                
def generate_code_skeleton(
    file_path: Annotated[str, "Path to the Python file whose skeleton is to be extracted."],
    start: Annotated[int, "Start line number (1-indexed). Use -1 to indicate the beginning."],
    end: Annotated[int, "End line number (1-indexed). Use -1 to indicate the end of the file."]
) -> str:
    
    skeleton_lines = []

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return f"Error: File not found - {file_path}"
    except Exception as e:
        return f"Error while reading file: {e}"

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Basic structure: imports, class, def
        if (
            stripped.startswith("import") or
            stripped.startswith("from") or
            stripped.startswith("class ") or
            re.match(r"(async\s+)?def\s+\w+\s*\(", stripped)
        ):
    
            skeleton_lines.append(f"{idx:4}: {line.rstrip()}")
            
        elif start != -1 and end != -1 and idx>=start and idx<=end:
            skeleton_lines.append(f"{idx:4}: {line.rstrip()}")

    return "\n".join(skeleton_lines) if skeleton_lines else "No skeleton elements found."


def process_line_operations(lines, deleted, inserted, main_code):
  
    operations = [] 
    for start, end in deleted:
        for i in range(start, end + 1):
            operations.append({
                'type': 'delete',
                'original_start': i,  # Keep original 1-indexed
                'original_end': i,      # Keep original 1-indexed
                'start':i - 1,       # 0-indexed for processing
                'end': i - 1           # 0-indexed for processing
            })
  
    for line_num, content in inserted:
        
       
        operations.append({
            'type': 'insert',
            'original_start': line_num, 
            'original_position': line_num,  # Keep original 1-indexed
            'position': line_num - 1,       # 0-indexed for processing
            'content': content.split("\n")
        })
    
    
    operations.sort(key=lambda x: x.get('original_start'))
    
    result = lines.copy()
    offset = 0  
    
    for op in operations:
         
        if op['type'] == 'delete':
            actual_start = op['start'] + offset
            actual_end = op['end'] + offset
    
            # del result[actual_start:actual_end + 1]
            result[actual_start] = ""
            
            lines_deleted = (op['end'] - op['start'] + 1)
            # offset -= lines_deleted
            
        elif op['type'] == 'insert':
           
            actual_position = op['position'] + offset
            
            if isinstance(op['content'], list):
                for i, line in enumerate(op['content']):
                    result.insert(actual_position + i, line)
                offset += len(op['content'])
            else:
                result.insert(actual_position, op['content'])
                offset += 1
    main_list = main_code.split("\n")
    prefix_main = ""
    main_list = [line for line in main_list if line.strip()]
    if not main_list[0].strip().startswith("if __name__"):
        result.insert(len(result), "if __name__ == '__main__':")
        # result.append("\t"+main_list[0].strip())
        prefix_main = "\t"
    # else:
    #     result.insert(len(result), main_list[0].strip())
    for i in range(len(main_list)):
        
        result.append(prefix_main+main_list[i])
    
    
    return result


def apply_changes_to_file(file_path, deleted, inserted, main_code):
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        lines = [line.rstrip('\n') for line in lines]
        

        result = process_line_operations(lines, deleted, inserted, main_code)
        with open(file_path, 'w') as f:
            for line in result:
                f.write(line + '\n')
                
        print(f"Successfully applied changes to {file_path}")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
    except Exception as e:
        print(f"Error processing file: {e}")