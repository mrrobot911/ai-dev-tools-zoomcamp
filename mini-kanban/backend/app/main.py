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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
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

# Serve static files
from fastapi.staticfiles import StaticFiles
app.mount("/assets", StaticFiles(directory="/app/static/assets"), name="assets")

# Catch-all for SPA routing
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    frontend_dir = "/app/static"
    
    if not full_path:
        return FileResponse(os.path.join(frontend_dir, "index.html"))
    
    file_path = os.path.join(frontend_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    return FileResponse(os.path.join(frontend_dir, "index.html"))