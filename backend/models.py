from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ProjectType(str, Enum):
    WEB_APP = "web_app"
    AI_ML = "ai_ml"
    FULL_STACK = "full_stack"
    DATA_ANALYSIS = "data_analysis"

class ProjectRequest(BaseModel):
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Detailed project description")
    project_type: ProjectType = Field(..., description="Type of project")
    requirements: Optional[List[str]] = Field(default=[], description="Specific requirements")
    
class Task(BaseModel):
    id: str
    title: str
    description: str
    assigned_to: str
    status: str = "pending"
    dependencies: List[str] = []
    output: Optional[Dict[str, Any]] = None
    
class ProjectPlan(BaseModel):
    project_id: str
    title: str
    description: str
    tasks: List[Task]
    architecture: Dict[str, Any]
    tech_stack: List[str]
    
class ProjectResponse(BaseModel):
    project_id: str
    status: str
    message: str
    download_url: Optional[str] = None
    created_at: datetime