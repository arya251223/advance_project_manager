from crewai import Agent, Task, Crew
from langchain_ollama import OllamaLLM
from backend.config import settings
from backend.models import ProjectPlan, Task as ProjectTask
from typing import Dict, Any, List
import json

from backend.utils.llm_factory import create_llm

class SeniorDeveloperAgent:
    def __init__(self):
        self.llm = create_llm("senior_developer")
    
        
        self.agent = Agent(
            role="Senior Full-Stack Developer",
            goal="Architect and implement core system components",
            backstory="""You are a senior developer with expertise in Python, FastAPI, 
            JavaScript, and AI/ML. You design scalable systems and write clean, 
            production-ready code.""",
            llm=self.llm,
            verbose=True
        )
    
    async def implement_core_architecture(self, project_plan: Dict[str, Any]) -> Dict[str, str]:
        """Implement core architecture and main components"""
        
        task = Task(
            description=f"""
            Implement the core architecture for this project:
            
            Tech Stack: {', '.join(project_plan['tech_stack'])}
            Architecture: {json.dumps(project_plan['architecture'])}
            
            Create:
            1. Main application entry point
            2. Core configuration
            3. Base models/schemas
            4. Main API structure (if web app)
            5. Project structure setup
            
            Return complete, production-ready code for each file.
            Format as JSON with filename as key and code as value.
            """,
            agent=self.agent,
            expected_output="JSON with filenames and code"
        )
        
        # Use Crew to execute the task
        crew = Crew(
            agents=[self.agent],
            tasks=[task]
        )
        result = crew.kickoff()  # Synchronous call
        
        # Extract the raw output
        output_text = str(result.raw) if hasattr(result, 'raw') else str(result)
        
        try:
            files = json.loads(output_text)
        except:
            # Fallback implementation
            files = self._generate_default_structure(project_plan)
        
        return files
    
    def delegate_subtasks(self, tasks: List[ProjectTask]) -> List[Dict[str, Any]]:
        """Break down tasks for junior developers"""
        
        subtasks = []
        for task in tasks:
            if task.assigned_to.startswith("junior_dev"):
                subtask = Task(
                    description=f"""
                    Create a detailed implementation plan for:
                    Task: {task.title}
                    Description: {task.description}
                    
                    Break this into 2-3 specific coding tasks with:
                    - File to create/modify
                    - Functions/classes to implement
                    - Clear specifications
                    
                    Format as JSON array of subtasks.
                    """,
                    agent=self.agent,
                    expected_output="JSON array of subtasks"
                )
                
                # Use Crew to execute
                crew = Crew(
                    agents=[self.agent],
                    tasks=[subtask]
                )
                result = crew.kickoff()  # Synchronous call
                
                output_text = str(result.raw) if hasattr(result, 'raw') else str(result)
                
                try:
                    task_breakdown = json.loads(output_text)
                    subtasks.extend(task_breakdown)
                except:
                    subtasks.append({
                        "file": f"{task.title.lower().replace(' ', '_')}.py",
                        "description": task.description,
                        "assigned_to": task.assigned_to
                    })
        
        return subtasks
    
    def _generate_default_structure(self, project_plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate default project structure"""
        # Keep the existing implementation as is
        files = {}
        
        # Main FastAPI app
        files["main.py"] = """from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

app = FastAPI(title="Generated Project")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestModel(BaseModel):
    data: str
    options: Optional[dict] = {}

class ResponseModel(BaseModel):
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/process", response_model=ResponseModel)
async def process_data(request: RequestModel):
    try:
        # Process the request
        result = {"processed": request.data}
        return ResponseModel(status="success", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        
        # Keep rest of the default structure generation as is...
        # (Include all the other files like requirements.txt, index.html, etc.)
        
        return files