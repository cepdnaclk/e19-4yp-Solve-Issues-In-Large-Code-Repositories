"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat May 04 2025

"""


from pydantic import BaseModel, Field
from typing import List
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