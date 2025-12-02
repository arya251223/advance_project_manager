import os
import json
from pathlib import Path
from typing import Any, Dict, List
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self):
        self.base_path = Path(settings.GENERATED_DIR)
        self.ensure_base_directory()
    
    def ensure_base_directory(self):
        """Ensure the base generated directory exists"""
        self.base_path.mkdir(exist_ok=True)
    
    def create_project_directory(self, project_id: str) -> Path:
        """Create a directory for a specific project"""
        project_path = self.base_path / project_id
        project_path.mkdir(exist_ok=True)
        return project_path
    
    def save_file(self, project_id: str, filename: str, content: str) -> Path:
        """Save a file to the project directory"""
        project_path = self.create_project_directory(project_id)
        
        # Handle nested paths
        file_path = project_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved file: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save file {filename}: {str(e)}")
            raise
    
    def save_json(self, project_id: str, filename: str, data: Dict[str, Any]) -> Path:
        """Save JSON data to a file"""
        content = json.dumps(data, indent=2)
        return self.save_file(project_id, filename, content)
    
    def read_file(self, project_id: str, filename: str) -> str:
        """Read a file from the project directory"""
        file_path = self.base_path / project_id / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def list_project_files(self, project_id: str) -> List[str]:
        """List all files in a project directory"""
        project_path = self.base_path / project_id
        
        if not project_path.exists():
            return []
        
        files = []
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(project_path)
                files.append(str(relative_path))
        
        return sorted(files)
    
    def get_project_structure(self, project_id: str) -> Dict[str, Any]:
        """Get the project directory structure as a nested dictionary"""
        project_path = self.base_path / project_id
        
        if not project_path.exists():
            return {}
        
        def build_tree(path: Path) -> Dict[str, Any]:
            tree = {}
            
            for item in sorted(path.iterdir()):
                if item.is_file():
                    tree[item.name] = "file"
                elif item.is_dir():
                    tree[item.name] = build_tree(item)
            
            return tree
        
        return build_tree(project_path)
    
    def delete_project(self, project_id: str):
        """Delete a project directory and all its contents"""
        project_path = self.base_path / project_id
        
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)
            logger.info(f"Deleted project: {project_id}")
    
    def get_file_stats(self, project_id: str) -> Dict[str, Any]:
        """Get statistics about project files"""
        project_path = self.base_path / project_id
        
        if not project_path.exists():
            return {"exists": False}
        
        total_size = 0
        file_count = 0
        file_types = {}
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                file_count += 1
                size = file_path.stat().st_size
                total_size += size
                
                # Count file types
                ext = file_path.suffix.lower()
                if ext:
                    file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            "exists": True,
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": file_types
        }
