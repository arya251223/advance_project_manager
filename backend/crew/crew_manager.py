### 11. Crew Manager (`backend/crew/crew_manager.py`)


from crewai import Crew, Process
from backend.agents.senior_manager_agent import SeniorManagerAgent
from backend.agents.project_manager_agent import ProjectManagerAgent
from backend.agents.senior_developer_agent import SeniorDeveloperAgent
from backend.agents.junior_developer_agent import JuniorDeveloperAgent
from backend.agents.integrator_agent import IntegratorAgent
from backend.agents.integrator_tester_agent import IntegratorTesterAgent
from backend.agents.tester_agent import FinalTesterAgent 
from backend.agents.delivery_agent import DeliveryAgent
from backend.models import ProjectRequest, ProjectResponse
from backend.utils.file_manager import FileManager
from backend.utils.project_packager import ProjectPackager
from typing import Dict, Any
import uuid
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CrewManager:
    def __init__(self):
        self.file_manager = FileManager()
        self.project_packager = ProjectPackager()
        
        # Initialize all agents
        self.senior_manager = SeniorManagerAgent()
        self.project_manager = ProjectManagerAgent()
        self.senior_developer = SeniorDeveloperAgent()
        self.junior_developers = [JuniorDeveloperAgent(i) for i in range(1, 6)]
        self.integrators = [IntegratorAgent(i) for i in range(1, 3)]
        self.integrator_tester = IntegratorTesterAgent()
        self.final_tester = FinalTesterAgent()
        self.delivery_agent = DeliveryAgent()
    
    async def execute_project(self, project_request: ProjectRequest) -> ProjectResponse:
        """Execute the entire project workflow"""
        
        project_id = str(uuid.uuid4())
        logger.info(f"Starting project execution: {project_id}")
        
        try:
            # Phase 1: Strategy and Planning
            logger.info("Phase 1: Strategy and Planning")
            strategy = await self._run_with_timeout(
                self.senior_manager.analyze_project(project_request),
                timeout=300
            )
            
            project_plan = await self._run_with_timeout(
                self.project_manager.create_project_plan(strategy, project_id),
                timeout=300
            )
            
            # Phase 2: Core Development
            logger.info("Phase 2: Core Development")
            core_files = await self._run_with_timeout(
                self.senior_developer.implement_core_architecture(project_plan.dict()),
                timeout=600
            )
            
            # Save core files
            for filename, content in core_files.items():
                self.file_manager.save_file(project_id, filename, content)
            
            # Phase 3: Module Development (Junior Developers)
            logger.info("Phase 3: Module Development")
            subtasks = self.senior_developer.delegate_subtasks(project_plan.tasks)
            
            # Distribute subtasks among junior developers
            all_module_files = {}
            for i, subtask in enumerate(subtasks):
                junior_dev = self.junior_developers[i % len(self.junior_developers)]
                module_files = await self._run_with_timeout(
                    junior_dev.implement_module(subtask),
                    timeout=400
                )
                all_module_files.update(module_files)
            
            # Save module files
            for filename, content in all_module_files.items():
                self.file_manager.save_file(project_id, filename, content)
            
            # Phase 4: Integration
            logger.info("Phase 4: Integration")
            all_files = {**core_files, **all_module_files}
            
            # Run both integrators in parallel
            integration_tasks = []
            for integrator in self.integrators:
                task = self._run_with_timeout(
                    integrator.integrate_components(all_files, project_request.project_type),
                    timeout=400
                )
                integration_tasks.append(task)
            
            integration_results = await asyncio.gather(*integration_tasks)
            
            # Merge integration files
            for result in integration_results:
                for filename, content in result.items():
                    self.file_manager.save_file(project_id, filename, content)
                    all_files[filename] = content
            
            # Phase 5: Integration Testing
            logger.info("Phase 5: Integration Testing")
            test_results = await self._run_with_timeout(
                self.integrator_tester.test_integration(all_files),
                timeout=600
            )
            
            # Save test files and apply fixes
            for filename, content in test_results.get('test_files', {}).items():
                for filename, content in test_results.get('test_files', {}).items():
                     self.file_manager.save_file(project_id, filename, content)
            
            for filename, content in test_results.get('fixes', {}).items():
                self.file_manager.save_file(project_id, filename, content)
                all_files[filename] = content
            
            # Phase 6: Final Testing
            logger.info("Phase 6: Final Testing")
            validation_results = await self._run_with_timeout(
                self.final_tester.final_validation(all_files, project_request.project_type),
                timeout=600
            )
            
            # Save additional test files
            for filename, content in validation_results.get('additional_tests', {}).items():
                self.file_manager.save_file(project_id, filename, content)
            
            # Phase 7: Delivery
            logger.info("Phase 7: Delivery")
            delivery_files = await self._run_with_timeout(
                self.delivery_agent.prepare_delivery(project_id, all_files, validation_results),
                timeout=300
            )
            
            # Save delivery files
            for filename, content in delivery_files.items():
                self.file_manager.save_file(project_id, filename, content)
            
            # Create final package
            logger.info("Creating final package")
            zip_path = self.project_packager.create_package(project_id)
            
            return ProjectResponse(
                project_id=project_id,
                status="completed",
                message="Project successfully generated and delivered",
                download_url=f"/download/{project_id}",
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Project execution failed: {str(e)}")
            return ProjectResponse(
                project_id=project_id,
                status="failed",
                message=f"Project generation failed: {str(e)}",
                created_at=datetime.now()
            )
    
    async def _run_with_timeout(self, coro, timeout: int):
        """Run a coroutine with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise Exception(f"Operation timed out after {timeout} seconds")
