import logging

from backend.utils.llm_factory import create_llm

class JuniorDeveloperAgent:
    def __init__(self):
        self.role = "Junior Developer"
        self.goal = "Implement code and follow guidelines from senior dev"
        self.backstory = "Entry-level dev learning by contributing to modules"

    async def implement_task(self, task):
        logging.info(f"JuniorDeveloper implementing task: {task}")
        # Dummy implementation logic
        result = f"Task '{task}' implemented successfully."
        return result

    async def report_progress(self, task):
        logging.info(f"JuniorDeveloper reporting progress for task: {task}")
        return f"Progress for task '{task}': Completed."
from crewai import Agent, Task
from langchain_ollama import OllamaLLM
from backend.config import settings
from typing import Dict, Any, List
import json

class JuniorDeveloperAgent:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.llm = create_llm("junior_developer")

        
        self.agent = Agent(
            role=f"Junior Developer {agent_id}",
            goal="Implement specific modules and helper functions",
            backstory=f"""You are junior developer #{agent_id} specializing in implementing 
            specific features and modules. You write clean, well-documented code following 
            best practices.""",
            llm=self.llm,
            verbose=True
        )
    
    def implement_module(self, subtask: Dict[str, Any]) -> Dict[str, str]:
        """Implement a specific module or feature"""
        
        task = Task(
            description=f"""
            Implement this specific module:
            
            File: {subtask.get('file', 'module.py')}
            Task: {subtask.get('description', 'Implement module')}
            
            Requirements:
            1. Write complete, working code
            2. Include proper error handling
            3. Add docstrings and comments
            4. Follow Python best practices
            
            Return the complete file content as a string.
            """,
            agent=self.agent,
            expected_output="Complete Python file content"
        )
        
        result = task.execute()
        
        # Clean up the result
        code = result.strip()
        if not code.startswith('"""') and not code.startswith('#'):
            # Add a basic module docstring if missing
            code = f'"""\nModule: {subtask.get("file", "module.py")}\nDescription: {subtask.get("description", "Module implementation")}\n"""\n\n' + code
        
        return {subtask.get('file', f'module_{self.agent_id}.py'): code}
    
    def implement_helper_functions(self, project_type: str) -> Dict[str, str]:
        """Implement helper functions based on project type"""
        
        helpers = {}
        
        if project_type == "ai_ml":
            task = Task(
                description="""
                Create helper functions for an AI/ML project:
                1. Data preprocessing functions
                2. Model evaluation metrics
                3. Visualization helpers
                4. Data loading utilities
                
                Return complete Python code with all functions.
                """,
                agent=self.agent,
                expected_output="Python code with helper functions"
            )
            
            result = task.execute()
            helpers["ml_helpers.py"] = result
            
        elif project_type == "web_app":
            task = Task(
                description="""
                Create helper functions for a web application:
                1. Input validation functions
                2. Database connection helpers
                3. Authentication utilities
                4. Response formatting functions
                
                Return complete Python code with all functions.
                """,
                agent=self.agent,
                expected_output="Python code with helper functions"
            )
            
            result = task.execute()
            helpers["web_helpers.py"] = result
        
        return helpers
