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
        
        
if __name__ == "__main__":

    file_path = 'example.py'

    deleted = [(2, 3), (5, 5)]

    inserted = [(1, "Inserted line 1"), (4, """print(Inserted line 2)\nprint("Inserted line 3")"""), (6, """a=4\nprint(a)""")]
    main_code = """
        if __name__ == "__main__":
            print("Main code block executed")
        """
    
    apply_changes_to_file(file_path, deleted, inserted, main_code)