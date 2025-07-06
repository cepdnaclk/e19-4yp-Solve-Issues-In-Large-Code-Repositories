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
            '''You are a expert in regenerating github issues descriptions .'''),
        (
            "human",
            '''### **Given GitHub issue description**:
     
```{problem_description}```

`With the help of above description generate 15 similar descriptions.`
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

#####################Agent ##############
# from langchain.prompts import PromptTemplate
file_edit_template = ChatPromptTemplate.from_messages([
    (
        "system",
        ''' You are an expert Software Engineer Specialized in solving github issues. Given a skeleton code file, issue description and a hint,  
        you need to generate the file operations (deletions, insertions, and main code additions(for testing))  required to fix the issue.'''

),
    (
        "human",
    '''
       SKELETON CODE:
    ```python
    {skeleton_code}
    ```

    ISSUE DESCRIPTION:
    ```{issue_description}```
    
    HINT:
    ```{hint}```

    INSTRUCTIONS:
    1. Analyze the skeleton code and the issue description
    2. Determine which lines need to be deleted  to solve the issue
    3. Determine what new lines need to be inserted and where to solve the issue
    4. Determine what main code block should be added at the end to verify the issue is resolved
    5. Provide clear reasoning for your changes
    6. Think about syntax correctness of the coded after delete and insert operations.


    EXAMPLE OUTPUT FORMAT:
    - deleted: [(2, 8), (5, 5)] means delete lines 2-3 and line 5
    - inserted: [(1, "new line"), (4, "line1\\nline2")] means insert at line 1 and insert two lines at line 4
    - main_code: the code block for the main section


    Generate the file operations:
'''
        
    )])


window_select_template = ChatPromptTemplate.from_messages([
    (
        "system",
        '''
            You are an expert code analyst tasked with identifying specific code windows (line ranges) that need to be examined to solve a given issue.
        '''
    ),
    (
        "human",
        '''
        Given the following issue description and numbered skeleton code, identify the 
        **most suspicious code windows** that need to be examined to solve the issue.

        ISSUE DESCRIPTION:
        ```{issue_description}```
        
        
        NUMBERED CODE SKELETON:
        ```{code_skeleton}```

        INSTRUCTIONS:
        - Analyze the issue description and the numbered skeleton code carefully.
        - Identify specific line ranges in the code that are likely related to the issue.
        - Provide a single large window (start line number and end line number) that covers the suspicious code sections that needs to be fix.
        
        '''
    )
])

learn_from_experience_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        '''You are an expert software engineering mentor analyzing a code modification attempt to extract valuable learning insights.
        Your goal is to help developers learn from both successful and failed attempts'''
    ),
    (
        "human",
        '''
        ISSUE DESCRIPTION:
    {issue_description}

    ORIGINAL CODE SKELETON (before modifications):
    {skeleton_code}

    ATTEMPTED CHANGES:
    {changes_dictionary}

    EXECUTION RESULT/OUTPUT:
    {execution_output}
    
    ANALYSIS TASK:
    1. Determine whether this attempt fully resolved the issue.
    - If you are confident it is fixed, set `next_step` to `"end"`.
    - Otherwise, set `next_step` to `"continue"`.

    2. Provide `learning_experience` from the actions taken:
    - These are concise lessons, insights, or debugging principles learned from this specific attempt.
    - Include technical insights, observed pitfalls, and what should be done differently in future attempts.

   
        
        '''
    )
])

action_analysis_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        '''
        You are an expert code debugger and problem solver. Your task is to analyze the provided skeleton code, issue description, actions taken, and relevant output to identify what went wrong and suggest the next suitable steps to resolve the issue.
        '''
    ),
    (
        "human",
        '''
        ### Inputs:
    1. **Skeleton Code**:
    ```
    {skeleton_code}
    ```

    2. **Issue Description**:
    {issue_description}

    3. **Actions Taken**:
    {actions_taken}


    ### Task:
    - Analyze the skeleton code, issue description, actions taken, and relevant output.
    - Identify the root cause of the issue based on the provided information.
    - For each action taken, evaluate its effectiveness and explain why it did or did not help resolve the issue.
    - Provide a clear explanation of what went wrong in the code or process.
    - Suggest the next suitable steps to resolve the issue, including specific code changes or debugging strategies if applicable.
    - Ensure the suggestions are actionable, precise, and tailored to the provided context.
            
        '''
    )
])