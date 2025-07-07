

import json
import asyncio
from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
from utils.utils import generate_code_skeleton
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI  # or your preferred LLM
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from sandbox import bash_session, docker_build
import os
import tempfile
from pathlib import Path
from git import Repo
from sandbox.specs import (
    MAP_REPO_TO_REQS_PATHS,
    MAP_REPO_VERSION_TO_SPECS_PY,
)
import prompts, schema
from datasets import load_dataset
import json
from utils.utils import apply_changes_to_file, remove_main_code, read_patch_as_string, apply_patch_string
import ast

dataset = load_dataset("lahirum/SWE_Experimental", split="train")
# @dataclass
# class CodeExecution:
#     """Represents a code execution event"""
#     deleted_lines: List[str]
#     added_lines: List[str]
#     main_command: str
#     output: str
   

# @dataclass
# class LearningMemory:
#     """Stores what the agent learns from each execution"""
#     insights: List[str]


class AgentState(TypedDict):
    """State of the React agent"""
    skeleton_code: str
    file_path: str
    hint: str
    issue_description: str
    step_count: int
    candiate_count: int
    experience: str
    actions: List[Dict[str, Any]]
    patch: str
    failed_pass_to_pass: List[str]
    failed_fail_to_pass: List[str]

llm_o4 = ChatOpenAI(
    model="o4-mini",
)
model_window_select = llm_o4.bind(
    functions=[convert_pydantic_to_openai_function(schema.CodeWindow)],
    function_call="auto",
)
window_select_chain = prompts.window_select_template | model_window_select

model_edit = llm_o4.bind(
    functions=[convert_pydantic_to_openai_function(schema.FileOperations)],
    function_call="auto",
)
file_edit_chain = prompts.file_edit_template | model_edit

model_learn = llm_o4.bind(
    functions=[convert_pydantic_to_openai_function(schema.ResolutionFeedback)],
    function_call="auto",
)
experience_get_chain = prompts.learn_from_experience_prompt | model_learn

analyze_chain = prompts.action_analysis_prompt | llm_o4

candidates = [{'file': 'django/django/core/validators.py', 'confidence': 95, 'reason': "The stack trace, error message, and Django's architectural pattern of translating low-level parsing exceptions into ValidationErrors all indicate that the bug is in this file. It directly contains the URLValidator logic and currently fails to convert ValueError arising from urllib.parse.urlsplit, violating Django's validation contract. This is confirmed by traceback mentions and the occurrence of the 'Invalid IPv6 URL' message."},
              {'file': 'django/django/forms/fields.py', 'confidence': 25, 'reason': "Although this file is in the call stack, its role is to invoke validators and catch ValidationError, not ValueError. Modifying it to address this issue would break separation of concerns and scatter redundant error-handling logic, which opposes Django's architecture. Low confidence, as the underlying root cause is not meant to be fixed here."}, {'file': 'django/django/core/exceptions.py', 'confidence': 0, 'reason': 'This file simply defines the ValidationError class, which works as intended and has no bearing on the conversion of ValueError in validation logic. The issue is not related to the structure or definition of exceptions, and this file does not appear in the traceback.'}]
class CodeAgent:
    def __init__(self, index=0, candidates=candidates, max_steps=20):
        # self.llm = ChatOpenAI(model=llm_model)
        self.max_steps_before_analysis =4 
        self.max_steps = max_steps
        self.terminal = self._initialize_terminal()
        self.graph = self._build_graph()
        self.index = index
        self.candidates = candidates
        
        # self.candidate_count = 1
        # self.llm_o4 = ChatOpenAI(model="o4-mini")
        
        
    
    def _initialize_terminal(self):
        bash = bash_session.BashSession()
        specs = MAP_REPO_VERSION_TO_SPECS_PY[dataset[self.index]['repo']][dataset[self.index]['version']]
        host_dir = os.path.abspath(".") + "/testbed"
        container_dir = "/testbed"
        
        if "pre_install" in specs:
            pre_install_commands = "\n".join(specs["pre_install"])
        else:
            pre_install_commands = ""
        dockerfile_str = docker_build.generate_dockerfile_packages(
            python_version= specs["python"],
            pre_install= pre_install_commands,      
        )
        name = dataset[self.index]['instance_id'].split("__")[0]
        version = dataset[self.index]['version']
        commit_id = dataset[self.index]['base_commit']
        repo = Repo(name)
        print(repo.git.reset('--hard', commit_id))
        bash.run_command("rm -rf testbed")
        bash.run_command("mkdir testbed")
        bash.run_command(f"mkdir testbed/agent")
        bash.run_command(f"cp -r {name} testbed")
        bash.run_command(f"cp -r {name} testbed/agent")

        tmpdir = tempfile.mkdtemp()
        Path(f"{tmpdir}/Dockerfile").write_text(dockerfile_str)
        print(f"Generated Dockerfile for {name}_{version}")
        bash.run_command(f"docker build -t swe-ubuntu-base {tmpdir}")

        bash.run_command(f"docker run --mount type=bind,src={host_dir},dst={container_dir} -it swe-ubuntu-base bash", new_env=True, timeout=250)
        bash.run_command(f"source /opt/miniconda3/bin/activate py_{specs['python']}")
        bash.run_command(f"cd {name}")
        if "pip_packages" in specs:
            pip_packages = " ".join(specs["pip_packages"])
            bash.run_command(f"pip install {pip_packages}")
        
        if "install" in specs:
            bash.run_command(specs["install"])
        if "packages" in specs:
            if not specs["packages"].startswith("requiremen"):
                bash.run_command(f"pip install {specs['packages']}")
            else:
                if dataset[self.index]['repo'] in MAP_REPO_TO_REQS_PATHS:
                    requirements_path = MAP_REPO_TO_REQS_PATHS[dataset[self.index]['repo']]
                    requirements_path = " ".join(requirements_path)
                else:
                    requirements_path = specs['packages']
                bash.run_command(f"pip install -r {requirements_path}")
        
        bash.run_command("cd ..")           
        return bash
    
    def start(self, state: AgentState) -> AgentState:
        file_path = self.candidates[state['candiate_count']]['file']
        # issue_description = dataset[state["candiate_count"]]["problem_statement"]
        hint = self.candidate_count[state['candiate_count']]['reason']
        skeleton = generate_code_skeleton(file_path, start=-1, end=-1)
        window_ans = window_select_chain.invoke({"issue_description": state['issue_description'], "code_skeleton": skeleton})
        window_ans = json.loads(window_ans.additional_kwargs["function_call"]["arguments"])
        skeleton = generate_code_skeleton("testbed/"+file_path, start=window_ans['start_line'], end=window_ans['end_line'])
        
        updated_state = state.copy()  # Create a copy to avoid mutating the input directly
        updated_state.update({
            "skeleton_code": skeleton,
            "file_path": file_path,
            "hint": hint,
            "step_count": 0, # Increment step_count or initialize to 1
            "experience": "No instruction yet",
            "actions": []
        })
        return updated_state
        
        
    
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("start", self.start)
        workflow.add_node("edit", self.edit)
        workflow.add_node("analyze", self.analyze_action)
        workflow.add_node("next_candidate", self.get_next_candidate)
        workflow.add_node("test", self.test)
       
        
        # Define the flow
        workflow.set_entry_point("start")
        workflow.add_edge("start", "edit")
        workflow.add_edge("analyze", "edit")
        workflow.add_edge("next_candidate", "start")
        
        workflow.add_conditional_edges(
        source="edit",
        path=lambda x: x["next"],  # Use the 'next' field to determine routing
        path_map={
            "CONTINUE": "edit",
            "ANALYZE": "analyze",
            "NEXT": "next_candidate",
            "END": END
        }
    )
        
        workflow.add_edge("analyze_memory", "edit_file")
        
        return workflow.compile()

    def edit(self, state: AgentState) -> Dict[str, Any]:
        edit_ans = file_edit_chain.invoke({
        "issue_description": state['issue_description'],
        "skeleton_code": state['skeleton'],
        "hint": state['hint'],
        "instruction": state["experience"]
        })
        edit_ans = json.loads(edit_ans.additional_kwargs["function_call"]["arguments"])
        inserted = []
        for added in edit_ans['inserted']:
            inserted.append((int(added['line_num']), added['content']))
        deleted = []
        for dele in edit_ans['deleted']:
            deleted.append((int(dele['start']), int(dele['end'])))
        apply_changes_to_file(
            file_path="testbed/agent/"+state['file_path'],
            inserted=inserted,
            deleted=deleted,
            main_code=edit_ans['main_code'],
        )
        
        output = self.terminal.run_command("python agent/"+state['file_path'], timeout=5000)
        
        exp = experience_get_chain.invoke({
            "issue_description": state['issue_description'],
            "skeleton_code": state['skeleton_code'],
            "changes_dictionary": edit_ans,
            "execution_output": output
        })
        exp = json.loads(exp.additional_kwargs["function_call"]["arguments"])
        updated_state = state.copy()  # Create a copy to avoid mutating the input directly
        updated_state.update({
            "step_count": state["step_count"]+1,  # Increment step_count or initialize to 1
            "experience": exp['learning_experience'],
            "actions": state["actions"]+[{"action": edit_ans, "output": output}],
        })
        if exp['next_step'] == "end":
            next_step = "END"
        elif updated_state["step_count"]>self.max_steps:
            if state["candiate_count"]<len(self.candidates):
                next_step = "NEXT"
            else:
                next_step = "END"
        elif updated_state['step_count']>self.max_steps_before_analysis:
            next_step = "ANALYZE"
        else:
            next_step = "CONTINUE"
        return {
            "state": updated_state,
            "next": next_step
        }
        
    def analyze_action(self, state: AgentState) -> AgentState:
        instruct = analyze_chain.invoke({
            "issue_description": state['issue_description'],
            "skeleton_code": state['skeleton_code'],
            "actions": state['actions'],
        })
        updated_state = state.copy()  # Create a copy to avoid mutating the input directly
        updated_state.update({
            "experience": instruct,
            "actions": []
        })
        return updated_state
    
    def get_next_candidate(self, state: AgentState) -> AgentState:
        self.max_steps = max(4, self.max_steps-4)
        updated_state = state.copy()  # Create a copy to avoid mutating the input directly
        updated_state.update({
            "candiate_count": state['candiate_count'] + 1,
        })
        return updated_state
    
    def test(self, state: AgentState) -> AgentState:
        fail_to_pass = dataset[self.index]['FAIL_TO_PASS']
        fail_to_pass = ast.literal_eval(fail_to_pass)
        pass_to_pass = dataset[self.index]['PASS_TO_PASS']
        pass_to_pass = ast.literal_eval(pass_to_pass)
        name = dataset[self.index]['instance_id'].split("__")[0]
        test_patch = dataset[self.index]['test_patch']
        remove_main_code("testbed/agent/"+state['file_path'])
        bash = bash_session.BashSession()
        bash.run_command(f"cp testbed/agent/{state['file_path']} testbed/{state['file_path']}")
        bash.run_command(f"git add testbed/{state['file_path']}")
        bash.run_command("git diff --cached > testbed/change.patch")
        bash.close()
        generated_patch = read_patch_as_string(f"testbed/{state['file_path']}")
        failed_pass_to_pass = []
        failed_fail_to_pass = []
        self.terminal.run_command(f"cd {name}")
        
        specs = MAP_REPO_VERSION_TO_SPECS_PY[dataset[self.index]['repo']][dataset[self.index]['version']]
        count = 0
        skip_count = 0
        for pas in pass_to_pass:
            te = pas.split("(")
            
            if len(te) != 2:
                skip_count += 1
                continue
            if not te[1].endswith(")"):
                # print("Skipping malformed test:", pas)
                skip_count += 1
                continue
            
            res = self.terminal.run_command(f"{specs['test_cmd']} {te[1][:len(te[1])-1].strip()}")
            res = res.strip().split("\n")
            found = False
            for r in res:
                if r.startswith(te[0].strip()):
                    if r.split("...")[1].strip().startswith("ok"):
                        print("Test passed:", r)
                        count += 1
                        found= True
                        break
            if not found:
                failed_pass_to_pass.append(pas)
                # print("Test failed:", res)
        apply_patch_string(test_patch, f"testbed/{name}")   
        count = 0
        skip_count = 0
        for pas in fail_to_pass:
            te = pas.split("(")
            
            if len(te) != 2:
                skip_count += 1
                continue
            if not te[1].endswith(")"):
                # print("Skipping malformed test:", pas)
                skip_count += 1
                continue
            
            res = self.terminal.run_command(f"{specs['test_cmd']} {te[1][:len(te[1])-1].strip()}")
            res = res.strip().split("\n")
            found = False
            for r in res:
                if r.startswith(te[0].strip()):
                    if r.split("...")[1].strip().startswith("ok"):
                        print("Test passed:", r)
                        count += 1
                        found= True
                        break
            if not found:
                failed_fail_to_pass.append(pas)
        
        updated_state = state.copy()  # Create a copy to avoid mutating the input directly
        updated_state.update({
            "patch": generated_patch,
            "failed_pass_to_pass": failed_pass_to_pass,
            "failed_fail_to_pass": failed_fail_to_pass,
        })
        return updated_state
    
    
        
    def run_agent(self, index=0, candidates = ""):
        """Run the agent with given inputs"""
        print("🚀 Starting React Code Agent...")
        self.index = index
        
        if not candidates:
            self.candidates = candidates
        issue_description = dataset[self.index]["problem_statement"]
        
        # Initialize state
        initial_state = {
            "skeleton_code": "",
            "file_path": "",
            "hint": "",
            "issue_description": issue_description,
            "step_count": 0,  # Increment step_count or initialize to 1
            "candidate_count": 0,
            "experience": [],
            "actions": [],
            "patch":"",
            "failed_pass_to_pass": [],
            "failed_fail_to_pass": []
        
        }
        
        # Run the graph
        config = {"configurable": {"thread_id": "react-agent-session"}}
        
        try:
            final_state = None
            for state in self.graph.stream(initial_state, config):
                print(f"🔄 Current state: {state}")
                # print(f"Current state keys: {list(state.keys())}")
                final_state = state
            
            return final_state
            
        except Exception as e:
            print(f"❌ Agent execution failed: {e}")
            return initial_state


if __name__ == "__main__":
    agent = ReactCodeAgent(index=0)
    final_state = agent.run_agent(index=0, candidates=candidates)
    print(f"Final state: {final_state}")
    
    # Example of how to use the test method
    # test_state = agent.test(final_state)
    # print(f"Test state: {test_state}")