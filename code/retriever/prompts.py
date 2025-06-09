from langchain_core.prompts import ChatPromptTemplate

prompt_extract = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            '''You are a helpful assistant with expertise in diagnosing root cause of GitHub issues.
            Given the following GitHub issue description, identify the **most suspicious file path** and the **most suspicious class or function name** that has leads to the issue.

Instructions:
- Carefully analyze the issue description.
- identify most suspicious files only using the analyze of information provided in the issue description. suspicious file should be in the repository not the user derived file.
- Based on this, infer:
  1. Most suspicious files path which needs to be fix to solve the issue. Note that fix should be done to the github repository, not for user derived files.
  2. The most suspicious class or function name which needs to be fix to solve the issue Note that fix should be done to the github repository, not for user derived files.'''),
        (
            "human",
            '''

Input:
Problem:
```{problem_description}```
'''
        )
    ]
)

file_path_filter_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        '''You are an AI assistant specialized in diagnosing the root cause of GitHub issues by analyzing file lists and issue descriptions.
        You are given:

- A list of file paths from a GitHub repository
- A GitHub issue description

Your task is to select the **single most suspicious file** that is most likely related to the root cause of the issue.

Guidelines:
- Analyze the issue description carefully.
- Cross-reference it with the given file paths.
- Pick the most relevant file from the list.
- Do not include user-generated, config, or unrelated files unless clearly relevant.

        '''
    ),
    (
        "human",
        '''
Input:
Problem:
```{problem_description}```
candidate files:
```{file_list}```
'''
    )
])

get_suspicious_file_list_from_list_of_files_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        '''You are an AI assistant specialized in diagnosing the root cause of GitHub issues by analyzing file lists and issue descriptions.
        You are given:

- A list of file paths from a GitHub repository
- A GitHub issue description

Your task is to select the **most suspicious files** that is most likely related to the root cause of the issue.

Guidelines:
- Analyze the issue description carefully.
- Cross-reference it with the given file paths.
- Pick the most relevant files from the list.
- Do not include user-generated, config, or unrelated files unless clearly relevant.

        '''
    ),
    (
        "human",
        '''
Input:
Problem:
```{problem_description}```
candidate files:
```{file_list}```
'''
    )
])

suspicious_files_filter_list_usingclfn_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        '''You are an AI assistant that identifies which source files in a GitHub repository are most likely related to a reported issue.
        You are given:

- A file structure from a GitHub repository. Each entry includes:
  - A file path
  - A list of class or function names within that file
- A GitHub issue description

Your task is to return a **list of file paths** that are possible to responsible for the issue.

Instructions:
- Analyze the problem description.
- Examine the classes and function names in each file with problem description.
- Omit only unrelated or non-suspicious files.
'''
    ),
    (
        "human",
        '''

Input:
Problem:
```{problem_description}```

File Structure:
```json
{file_structure}

'''
    )
])

suspicious_directory_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        '''You are an intelligent assistant that identifies the most suspicious directory in a GitHub repository likely related to a given issue.
        
        You are given:

    - A list of directory paths from a GitHub repository
    - A problem description from a GitHub issue

    Your task is to identify the **single most suspicious directory** from the guven directory paths where the issue is most likely originating from.

    Instructions:
    - Analyze the problem description closely.
    - Use your reasoning to determine which directory is most likely to contain the root cause.
    - Choose only one directory from the list.
    - Do not include explanations or other text — just return the most likely directory path.
            
            '''
    ),
    (
        "human",
        '''

Input:
Directory List:
```json
{directory_list}

Problem:
```{problem_description}```
'''
    )
])

suspicious_files_with_reason_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        '''You are an expert debugging assistant. You analyze GitHub issues and source code structure to identify the most suspicious files causing the issue, 
        with detailed reasoning.
        
        You are given:

    - A file structure of a GitHub repository. Each file includes:
    - Its file path
    - A skeleton of the code (e.g., class/function names, structure)
    - A GitHub issue description

    Your task is to identify *multiple most suspicious files (if applicable)** and provide a **clear reason** why each file might be related to the issue.

    Instructions:
    - Analyze the issue description carefully.
    - Examine the provided code skeletons.
    - Identify files that are highly likely to contain the root cause.
    - For each suspicious file, explain your reasoning.
    - Do not include less confodent files files.

        
        '''
    ),
    (
        "human",
        '''


Input:
Problem:
```{problem_description}```

File Structure:
```json
{file_structure}


'''
    )
])


deep_reasoning_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        '''You are a highly intelligent assistant with deep expertise in software debugging. You evaluate how likely a given file is responsible for a
        GitHub issue.
        '''
    ),
    (
        "human",
        '''
You are given a **GitHub issue description** and a list of **candidate files**, each with an associated reason for being suspected.
note that it is expected to find the file which needs to modify to solve the problem description. high score file means the most possible 
file which needs to modify to solve the problem description.

Your task is to:
- Carefully analyze the issue description.
- Evaluate the strength of the reasoning for each file.
- Provide a **confidence score out of 100** for each file based on how likely it is the root cause.
- Justify each score with **detailed technical reasoning**.
- Be critical — low confidence scores are valid if the reasoning or evidence is weak.

Input:

Problem Description:
```{problem_description}```

Candidate Files (with initial reasoning):
```json
{candidates}
```
'''
    )
])

prompt_embedding_retriver = ChatPromptTemplate.from_messages([
        (
            "system",
            '''You are a expert in generating descriptions including both text and codes that are simantically similar to the given description.'''),
        (
            "human",
            '''### **Given GitHub issue description**:
     
```{problem_description}```

`With the help of above description generate 15 simantically similar descriptions.`
'''
        )
])



prompt_extract_reasoning = ChatPromptTemplate.from_messages([
    (
        "system",
        '''You are an AI assistant specialized in analyzing technical reports to identify root causes of bugs in code repositories.
        You will extract a structured list of files with their confidence scores and reasoning based on the provided analysis.
        '''
    ),
    (
        "human",
        '''
        ```{analysis}```
        
        '''
    )
])
