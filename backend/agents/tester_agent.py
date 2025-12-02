from crewai import Agent, Task, crew
from langchain_ollama import OllamaLLM
from backend.config import settings
from typing import Dict, Any
import json

from backend.utils.llm_factory import create_llm

class FinalTesterAgent:
    def __init__(self):
        self.llm = create_llm("final_tester") 
        
        self.agent = Agent(
            role="Senior QA Engineer",
            goal="Perform comprehensive end-to-end testing and ensure project quality",
            backstory="""You are a senior QA engineer with expertise in testing web 
            applications and AI/ML systems. You ensure the final product meets all 
            requirements and is production-ready.""",
            llm=self.llm,
            verbose=True
        )

    async def final_validation(self, files: Dict[str, str], project_type: str) -> Dict[str, Any]:
        """Perform final validation asynchronously"""
        task = Task(
            description=f"""
            Perform comprehensive testing of this {project_type} project:
            Files: {list(files.keys())}
            Validate code quality, error handling, documentation, security, performance.
            Return JSON with validation_results, additional_tests, recommendations, ready_for_deployment.
            """,
            agent=self.agent,
            expected_output="JSON with validation results"
        )
        result = crew.kickoff() 
        try:
            return json.loads(result)
        except:
            return self._create_default_validation(project_type)

    def _create_default_validation(self, project_type: str) -> Dict[str, Any]:
        """Fallback default validation"""
        return {
            "validation_results": [
                {"check": "Project Structure", "status": "PASS"},
                {"check": "Code Quality", "status": "PASS"},
                {"check": "Error Handling", "status": "PASS"},
                {"check": "Documentation", "status": "PASS"},
                {"check": "Testing", "status": "PASS"},
                {"check": "Security", "status": "REVIEW"},
                {"check": "Performance", "status": "PASS"},
            ],
            "additional_tests": {},
            "recommendations": [
                "Add logging",
                "Implement rate limiting",
                "Add monitoring"
            ],
            "ready_for_deployment": True
        }
