from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from backend.models import ProjectRequest, ProjectResponse
from backend.crew.crew_manager import CrewManager
from backend.config import settings
from pathlib import Path
import logging
import uvicorn

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Project Manager API",
    description="Automatically generate full-stack projects using AI agents",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Paths ===
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "backend" / "frontend"

# ✅ Mount static files properly
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ✅ Serve index.html manually
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")


# === Crew Manager setup ===
crew_manager = CrewManager()
active_projects = {}

@app.get("/info")
async def root():
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
    return {"status": "healthy"}

@app.post("/assign_project", response_model=ProjectResponse)
async def assign_project(project_request: ProjectRequest, background_tasks: BackgroundTasks):
    if not project_request.title or not project_request.description:
        raise HTTPException(status_code=400, detail="Project title and description are required")
    try:
        response = await crew_manager.execute_project(project_request)
        active_projects[response.project_id] = response
        return response
    except Exception as e:
        logger.error(f"Failed to assign project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to assign project: {str(e)}")

@app.get("/project/{project_id}/status")
async def get_project_status(project_id: str):
    if project_id not in active_projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return active_projects[project_id]

@app.get("/download/{project_id}")
async def download_project(project_id: str):
    zip_path = Path(settings.GENERATED_DIR) / f"{project_id}.zip"
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Project package not found")
    return FileResponse(path=zip_path, filename=f"project_{project_id}.zip", media_type="application/zip")

@app.get("/projects")
async def list_projects():
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

# === Error Handlers ===
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
