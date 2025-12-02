import zipfile
import os
from pathlib import Path
from typing import Optional
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class ProjectPackager:
    def __init__(self):
        self.base_path = Path(settings.GENERATED_DIR)
    
    def create_package(self, project_id: str, output_name: Optional[str] = None) -> Path:
        """Create a ZIP package of the project"""
        project_path = self.base_path / project_id
        
        if not project_path.exists():
            raise FileNotFoundError(f"Project not found: {project_id}")
        
        # Determine output filename
        if output_name is None:
            output_name = f"{project_id}.zip"
        
        output_path = self.base_path / output_name
        
        # Create ZIP file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through all files in the project directory
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    # Get relative path for the archive
                    arcname = file_path.relative_to(project_path)
                    zipf.write(file_path, arcname)
                    logger.debug(f"Added to archive: {arcname}")
        
        logger.info(f"Created package: {output_path}")
        return output_path
    
    def extract_package(self, zip_path: Path, extract_to: Optional[Path] = None) -> Path:
        """Extract a ZIP package"""
        if not zip_path.exists():
            raise FileNotFoundError(f"ZIP file not found: {zip_path}")
        
        # Determine extraction path
        if extract_to is None:
            extract_to = self.base_path / zip_path.stem
        
        # Create extraction directory
        extract_to.mkdir(parents=True, exist_ok=True)
        
        # Extract ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_to)
        
        logger.info(f"Extracted package to: {extract_to}")
        return extract_to
    
    def get_package_info(self, zip_path: Path) -> dict:
        """Get information about a ZIP package"""
        if not zip_path.exists():
            raise FileNotFoundError(f"ZIP file not found: {zip_path}")
        
        info = {
            "filename": zip_path.name,
            "size_bytes": zip_path.stat().st_size,
            "size_mb": round(zip_path.stat().st_size / (1024 * 1024), 2),
            "files": []
        }
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for file_info in zipf.filelist:
                info["files"].append({
                    "filename": file_info.filename,
                    "size": file_info.file_size,
                    "compressed_size": file_info.compress_size
                })
        
        return info
    
    def validate_package(self, zip_path: Path) -> bool:
        """Validate that a ZIP package is not corrupted"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Test the ZIP file
                result = zipf.testzip()
                return result is None
        except Exception as e:
            logger.error(f"Package validation failed: {str(e)}")
            return False
