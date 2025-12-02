from crewai import Agent, Task, Crew
from langchain_ollama import OllamaLLM
from backend.config import settings
from backend.models import ProjectRequest
import json

from backend.utils.llm_factory import create_llm

class SeniorManagerAgent:
    def __init__(self):
        self.llm = create_llm("senior_manager")

        self.agent = Agent(
            role="Senior Project Manager",
            goal="Define project vision, strategy, and high-level architecture",
            backstory="""You are an experienced senior manager with 15+ years in software 
            development. You excel at understanding client needs and translating them into 
            clear technical requirements and architectural decisions.""",
            llm=self.llm,
            verbose=True
        )

    async def analyze_project(self, project_request: ProjectRequest):
        task = Task(
            description=f"""
            Analyze this project request and create a comprehensive strategy:
            Title: {project_request.title}
            Description: {project_request.description}
            Type: {project_request.project_type}
            Requirements: {', '.join(project_request.requirements)}
            Provide a JSON response with keys: vision, goals, architecture, tech_stack, modules, risks.
            """,
            agent=self.agent,
            expected_output="JSON formatted project strategy"
        )

        # Create a Crew and run the task (without await - kickoff is synchronous)
        crew = Crew(
            agents=[self.agent],
            tasks=[task]
        )
        result = crew.kickoff()  # Remove await - kickoff() is synchronous

        # Extract the raw output from CrewOutput object
        output_text = str(result.raw) if hasattr(result, 'raw') else str(result)

        try:
            strategy = json.loads(output_text)
        except Exception:
            strategy = {
                "vision": output_text,
                "goals": ["Build a functional " + project_request.project_type],
                "architecture": {"pattern": "MVC", "components": ["Frontend", "Backend", "Database"]},
                "tech_stack": ["Python", "FastAPI", "HTML", "CSS", "JavaScript"],
                "modules": [{"name": "Core", "purpose": "Main logic"}],
                "risks": ["Timeline", "Integration", "Complexity"]
            }

        return strategy