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
    
    main_found = False

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        
        if stripped.startswith("if __name__"):
            main_found = True
        if main_found:
            skeleton_lines.append(f"{idx:4}: {line.rstrip()}")
            continue

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


def process_line_operations(lines, deleted, inserted):
  
    operations = [] 
    for start, end in deleted:
        # for i in range(start, end + 1):
        operations.append({
            'type': 'delete',
            'original_start': start,  # Keep original 1-indexed
            'original_end': end,      # Keep original 1-indexed
            'start':start - 1,       # 0-indexed for processing
            'end': end - 1           # 0-indexed for processing
        })
  
    for line_num, content in inserted:
        content  = content.split("\n")
        content = [con.rstrip() for con in content ]
        content = [line for line in content if line.strip() != ""]

        
        
       
        operations.append({
            'type': 'insert',
            'original_start': line_num, 
            'original_position': line_num,  # Keep original 1-indexed
            'position': line_num - 1,       # 0-indexed for processing
            'content': content
        })
    
    
    operations.sort(key=lambda x: (x['original_start'], 0 if x['type'] == 'delete' else 1))
    
    result = lines.copy()
    offset = 0  
    
    for op in operations:
         
        if op['type'] == 'delete':
            actual_start = op['start'] + offset
            actual_end = op['end'] + offset
    
            # del result[actual_start:actual_end + 1]
            # result[actual_start] = ""
            
            for i in range(actual_start, actual_end + 1):
                result[i] = "#"+ result[i]
            
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
    # main_list = main_code.split("\n")
    # prefix_main = ""
    # main_list = [line for line in main_list if line.strip()]
    # if not main_list[0].strip().startswith("if __name__"):
    #     result.insert(len(result), "if __name__ == '__main__':")
    #     # result.append("\t"+main_list[0].strip())
    #     prefix_main = "\t"
    # # else:
    # #     result.insert(len(result), main_list[0].strip())
    # for i in range(len(main_list)):
        
    #     result.append(prefix_main+main_list[i])
    
    
    return result, offset


def apply_changes_to_file(read_file_path, write_file_path, deleted, inserted):
    
    try:
        with open(read_file_path, 'r') as f:
            lines = f.readlines()
        
        lines = [line.rstrip('\n') for line in lines]
        

        result, offset = process_line_operations(lines, deleted, inserted)
        with open(write_file_path, 'w') as f:
            for line in result:
                f.write(line + '\n')
                
        print(f"Successfully applied changes to {write_file_path}")
        return offset
    except FileNotFoundError:
        print(f"Error: File {read_file_path} not found")
    except Exception as e:
        print(f"Error processing file: {e}")
        
def remove_main_code(file_path):
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        lines = [line.rstrip('\n') for line in lines]
        
        while lines:
            if lines[-1].startswith("if __name__"):
                lines.pop()
                break
            lines.pop()
            
        if lines:
            with open(file_path, 'w') as f:
                for line in lines:
                    f.write(line + '\n')
        
                
        print(f"Successfully applied changes to {file_path}")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
    except Exception as e:
        print(f"Error processing file: {e}")
        
def add_main_code(file_path, main_code):
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        lines = [line.rstrip('\n') for line in lines]
        
        
        main_list = main_code.split("\n")
        prefix_main = ""
        main_list = [line for line in main_list if line.strip()]
        # if not main_list[0].strip().startswith("if __name__"):
        #     lines.append("if __name__ == '__main__':")
        #     prefix_main = "\t"
        for i in range(len(main_list)):
            
            lines.append(prefix_main+main_list[i])
            
        if lines:
            with open(file_path, 'w') as f:
                for line in lines:
                    f.write(line + '\n')
        
                
        print(f"Successfully applied changes to {file_path}")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
    except Exception as e:
        print(f"Error processing file: {e}")

def read_patch_as_string(patch_path):
    with open(patch_path, 'r', encoding='utf-8') as f:
        patch_str = f.read()
    return patch_str


import subprocess
import tempfile

def apply_patch_string(patch_str, repo_path='.'):
    # Create a temporary patch file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.patch', delete=False) as temp_patch:
        temp_patch.write(patch_str)
        temp_patch_path = temp_patch.name

    # Run `git apply` on the patch
    result = subprocess.run(
        ['git', 'apply', temp_patch_path],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode == 0:
        print("✅ Patch applied successfully.")
    else:
        print("❌ Failed to apply patch:")
        print(result.stderr)

    return result.returncode == 0  # Returns True if successful

def replace_line_operations(lines, replaces):
  

    
    for op in replaces:
        
         
        if op['type'] == 'delete':
            actual_start = op['start'] + offset
            actual_end = op['end'] + offset
    
            # del result[actual_start:actual_end + 1]
            # result[actual_start] = ""
            
            for i in range(actual_start, actual_end + 1):
                result[i] = "#"+ result[i]
            
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