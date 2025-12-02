from crewai import Agent, Task
from langchain_ollama import OllamaLLM
from backend.config import settings
from typing import Dict, Any, List
import json

from backend.utils.llm_factory import create_llm

class IntegratorAgent:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.llm = create_llm("integrator")
        
        self.agent = Agent(
            role=f"Integration Engineer {agent_id}",
            goal="Integrate components and ensure smooth communication between modules",
            backstory=f"""You are integration engineer #{agent_id} responsible for connecting 
            different parts of the system. You ensure APIs work correctly, frontend communicates 
            with backend, and all components integrate seamlessly.""",
            llm=self.llm,
            verbose=True
        )
    
    def integrate_components(self, files: Dict[str, str], project_type: str) -> Dict[str, str]:
        """Integrate all components together"""
        
        task = Task(
            description=f"""
            Review these files and create integration code:
            
            Files: {list(files.keys())}
            Project Type: {project_type}
            
            Create or modify files to ensure:
            1. Frontend properly calls backend APIs
            2. All imports are correct
            3. Configuration is properly set up
            4. Error handling is consistent
            5. Data flows correctly between components
            
            Return any new or modified files as JSON with filename as key and code as value.
            """,
            agent=self.agent,
            expected_output="JSON with integration files"
        )
        
        result = task.execute()
        
        try:
            integration_files = json.loads(result)
        except:
            # Fallback integration
            integration_files = self._create_default_integration(project_type)
        
        return integration_files
    
    def _create_default_integration(self, project_type: str) -> Dict[str, str]:
        """Create default integration files"""
        
        files = {}
        
        # API client for frontend
        files["api_client.js"] = """class APIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'API request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }
    
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// Export for use in other files
const apiClient = new APIClient();
"""

        # Configuration manager
        files["config_manager.py"] = """import os
import json
from typing import Any, Dict

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        \"\"\"Load configuration from file or environment\"\"\"
        config = {
            "api_host": os.getenv("API_HOST", "0.0.0.0"),
            "api_port": int(os.getenv("API_PORT", 8000)),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "database_url": os.getenv("DATABASE_URL", "sqlite:///./app.db"),
        }
        
        # Load from file if exists
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        \"\"\"Get configuration value\"\"\"
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        \"\"\"Set configuration value\"\"\"
        self.config[key] = value
        self.save_config()
    
    def save_config(self) -> None:
        \"\"\"Save configuration to file\"\"\"
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

# Global config instance
config = ConfigManager()
"""

        return files
