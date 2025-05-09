"""
* Author: Lahiru Menikdiwela
* Email: lahirumenik@gmail.com
___________________________________________________________
* Date: Sat May 04 2025

"""


from pydantic import BaseModel, Field
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