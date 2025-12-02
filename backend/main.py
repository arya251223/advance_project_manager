from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.models import ProjectRequest, ProjectResponse
from backend.crew.crew_manager import CrewManager
from backend.config import settings
from pathlib import Path
import logging
import uvicorn
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Project Manager API",
    description="Automatically generate full-stack projects using AI agents",
    version="1.0.0",
    root_path="/api"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize crew manager
crew_manager = CrewManager()

frontend_path = Path("backend/frontend")

# Serve static files (css/js) under /static
# Serve static assets directly from frontend folder
app.mount("/", StaticFiles(directory=frontend_path), name="frontend")


# Serve index.html at root
@app.get("/")
async def serve_index():
    return FileResponse(frontend_path / "index.html")



# Store active projects
active_projects = {}

@app.get("/info")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Project Manager API is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "assign_project": "/assign_project",
            "project_status": "/project/{project_id}/status",
            "download": "/download/{project_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/assign_project", response_model=ProjectResponse)
async def assign_project(
    project_request: ProjectRequest,
    background_tasks: BackgroundTasks
):
    """Assign a new project to the AI crew"""
    try:
        # Validate request
        if not project_request.title or not project_request.description:
            raise HTTPException(
                status_code=400,
                detail="Project title and description are required"
            )
        
        # Execute project asynchronously
        response = await crew_manager.execute_project(project_request)
        
        # Store project status
        active_projects[response.project_id] = response
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to assign project: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assign project: {str(e)}"
        )

@app.get("/project/{project_id}/status")
async def get_project_status(project_id: str):
    """Get the status of a project"""
    if project_id not in active_projects:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    
    return active_projects[project_id]

@app.get("/download/{project_id}")
async def download_project(project_id: str):
    """Download the generated project as a ZIP file"""
    zip_path = Path(settings.GENERATED_DIR) / f"{project_id}.zip"
    
    if not zip_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Project package not found"
        )
    
    return FileResponse(
        path=zip_path,
        filename=f"project_{project_id}.zip",
        media_type="application/zip"
    )

@app.get("/projects")
async def list_projects():
    """List all active projects"""
    return {
        "projects": [
            {
                "project_id": pid,
                "status": proj.status,
                "created_at": proj.created_at.isoformat()
            }
            for pid, proj in active_projects.items()
        ]
    }

# Mount static files for frontend
# Serve frontend (index.html at /)



# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )