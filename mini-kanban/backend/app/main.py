from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from contextlib import asynccontextmanager
import os

from app.routers import auth, boards, columns, cards, participants, invitations, search, updates
from app.auth import auth_middleware
from app.database import get_db
from app.dependencies import get_db_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only seed data if using in-memory SQLite (for development)
    if os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/minikanban").startswith("sqlite://"):
        from app.database import get_session
        db = get_session()
        try:
            from app.database_service import DatabaseService
            service = DatabaseService(db)
            service.seed_data()
        finally:
            db.close()
    
    yield
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title="Mini Kanban Board API",
    description="REST API for the Mini Kanban Board application",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware (single-origin by default; override via CORS_ORIGINS for split deploy)
_cors_origins_env = os.getenv("CORS_ORIGINS", "*")
_cors_origins = [o.strip() for o in _cors_origins_env.split(",") if o.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )

# Database dependency is imported from app.dependencies

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(boards.router, prefix="/boards", tags=["Boards"])
app.include_router(columns.router, prefix="/boards", tags=["Columns"])
app.include_router(cards.router, prefix="/boards", tags=["Cards"])
app.include_router(participants.router, prefix="/boards", tags=["Participants"])
app.include_router(invitations.router, prefix="/boards", tags=["Invitations"])
app.include_router(search.router, prefix="/boards", tags=["Search"])
app.include_router(updates.router, prefix="", tags=["Real-time"])

# Serve static files (FRONTEND_DIR/STATIC_DIR overridable; skip if not built, e.g. local API-only run)
from fastapi.staticfiles import StaticFiles
FRONTEND_DIR = os.getenv("STATIC_DIR", os.getenv("FRONTEND_DIR", "/app/static"))
if os.path.isdir(os.path.join(FRONTEND_DIR, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")

# Catch-all for SPA routing
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    frontend_dir = FRONTEND_DIR
    
    # If it looks like an API route, raise 404 so FastAPI handles it normally
    if full_path.startswith(("auth/", "boards/", "health")):
        raise HTTPException(status_code=404, detail="Not found")
    
    file_path = os.path.join(frontend_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Not found")