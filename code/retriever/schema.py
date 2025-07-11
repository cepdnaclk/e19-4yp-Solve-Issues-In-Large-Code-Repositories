"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat May 04 2025

"""


from pydantic import BaseModel, Field
from typing import List, Tuple, Optional
class SuspiciousComponentOutput(BaseModel):
    """Identify most suspicious file name and class/function name related to the issue."""
    file: str = Field(..., description="The most suspicious file path related to the issue.")
    class_function_name: str = Field(..., description="The most suspicious class or function name related to the issue.")



class FileSuspicionOutput(BaseModel):
    suspicious_file: str = Field(
        ...,
        description="The most suspicious file path that likely needs to be fixed to resolve the issue."
    )

class SuspiciousFilesOutputList(BaseModel):
    suspicious_files: List[str] = Field(
        ...,
        description="A list of file paths that are most suspicious and likely to contain the root cause of the issue."
    )
    
class SuspiciousDirectoryOutput(BaseModel):
    suspicious_directory: str = Field(
        ...,
        description="The most suspicious directory likely containing the root cause of the issue."
    )
    
class SuspiciousFileReason(BaseModel):
    file: str = Field(..., description="The path to the suspicious file.")
    reason: str = Field(..., description="The reasoning behind selecting this file as suspicious.")

class SuspiciousFileReasoningOutput(BaseModel):
    suspicious_files: List[SuspiciousFileReason] = Field(
        ...,
        description="A list of suspicious files with reasoning for each."
    )

class SuspiciousFileDeepReasoning(BaseModel):
    file: str = Field(..., description="The path to the suspicious file.")
    confidence: int = Field(..., description="Confidence out of 100 to say the file is suspicious.")
    reason: str = Field(..., description="The reasoning behind selecting this file as suspicious and giving such a confidence score out of 100.")

class SuspiciousFileDeepReasoningOutput(BaseModel):
    suspicious_files: List[SuspiciousFileDeepReasoning] = Field(
        ...,
        description="A list of suspicious files with a confidence score and deep reasoning for each."
    )
    
    
class DeleteOperation(BaseModel):
    """Represents a line deletion operation"""
    start: int = Field(..., description="Starting line number to delete (1-indexed)")
    end: int = Field(..., description="Ending line number to delete (1-indexed)")

class InsertOperation(BaseModel):
    """Represents a line insertion operation. Multi lines can be inserted at the start of line number"""
    line_number: int = Field(..., description="Start of Line number where to insert (1-indexed)")
    content: str = Field(..., description="Content to insert (can contain \n for multiple lines)")



###################Agent

class Deletion(BaseModel):
    start: int = Field(..., description="Start line (1-indexed) to start delete")
    end: int = Field(..., description="End line (1-indexed) to end delete")

class Insertion(BaseModel):
    line_num: int = Field(..., description="Line number to insert")
    content: str = Field(..., description="Code to insert (can contain \n for multiple lines)")

class FileOperations(BaseModel):
    """Complete set of file operations to perform"""
    deleted: List[Deletion] = Field(
        ..., 
        description="List of (start, end) tuples lines to delete lines of code to fix the issue"
    )
    inserted: List[Insertion] = Field(
        ..., 
        description="List of (line_number, content) tuples for lines to insert (can contain \n for multiple lines)"
    )
    reasoning: str = Field(
        ..., 
        description="Explanation of the changes made"
    )

class MainCode(BaseModel):
    
    main_code: str = Field(
        ..., 
        description= "A main code block to be appended at the end of the file, serving as a test to verify that the issue has been resolved"
    )

class CodeWindow(BaseModel):
    """Represents a specific window of code lines that need attention"""
    start_line: int = Field(
        ..., 
        description="Starting line number of the code window (1-indexed)"
    )
    end_line: int = Field(
        ..., 
        description="Ending line number of the code window (1-indexed)"
    )

from enum import Enum    
    
class NextStep(str, Enum):
    """Whether the workflow should end or continue."""
    END = "end"
    CONTINUE = "continue"


class ResolutionFeedback(BaseModel):
    """
    Schema passed to the tool that decides what to do next
    and records what was learned from the latest step.
    """
    learning_experience: str = Field(
        ...,
        description="learning experience got from the previous step."
    )
    
class NextStepFeedback(BaseModel):
    """
    Schema passed to the tool that decides what to do next
    and records what was learned from the latest step.
    """
    next_step: NextStep = Field(
        ...,
        description="Set to 'end' if it is confident that the issue is fully resolved, otherwise 'continue'.",
    )
    