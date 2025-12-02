from crewai import Agent, Task, Crew
from langchain_ollama import OllamaLLM
from backend.config import settings
from backend.models import ProjectPlan, Task as ProjectTask
import uuid
import json

from backend.utils.llm_factory import create_llm

class ProjectManagerAgent:
    def __init__(self):
        self.llm = create_llm("project_manager") 
        

        self.agent = Agent(
            role="Project Manager",
            goal="Break down project into actionable tasks and manage execution",
            backstory="""You are a detail-oriented project manager who excels at breaking 
            down complex projects into manageable tasks. You understand dependencies and 
            can create realistic project plans.""",
            llm=self.llm,
            verbose=True
        )

    async def create_project_plan(self, strategy: dict, project_id: str):
        task = Task(
            description=f"""
            Create a detailed project plan based on this strategy:
            Vision: {strategy['vision']}
            Architecture: {json.dumps(strategy['architecture'])}
            Modules: {json.dumps(strategy['modules'])}
            Format as JSON with keys: tasks (list of title, description, assigned_to, dependencies, estimated_hours)
            """,
            agent=self.agent,
            expected_output="JSON formatted project plan"
        )

        # Run using Crew (without await)
        crew = Crew(
            agents=[self.agent],
            tasks=[task]
        )
        result = crew.kickoff()  # Remove await

        # Extract the raw output from CrewOutput object
        output_text = str(result.raw) if hasattr(result, 'raw') else str(result)

        try:
            data = json.loads(output_text)
            tasks = data.get("tasks", [])
        except Exception:
            tasks = [
                {"title": "Setup Project", "description": "Initialize repo", "assigned_to": "senior_dev", "dependencies": [], "estimated_hours": 2}
            ]

        project_tasks = [
            ProjectTask(
                id=str(uuid.uuid4()),
                title=t["title"],
                description=t["description"],
                assigned_to=t["assigned_to"],
                dependencies=t.get("dependencies", [])
            )
            for t in tasks
        ]

        return ProjectPlan(
            project_id=project_id,
            title=strategy.get("vision", "Project"),
            description=json.dumps(strategy),
            tasks=project_tasks,
            architecture=strategy["architecture"],
            tech_stack=strategy["tech_stack"]
        )