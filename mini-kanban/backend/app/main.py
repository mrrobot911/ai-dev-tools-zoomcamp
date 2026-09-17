from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.routers import auth, boards, columns, cards, participants, invitations, search
from app.auth import auth_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed data
    from app.store import seed_data
    seed_data()
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

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(boards.router, prefix="/boards", tags=["Boards"])
app.include_router(columns.router, prefix="/boards", tags=["Columns"])
app.include_router(cards.router, prefix="/boards", tags=["Cards"])
app.include_router(participants.router, prefix="/boards", tags=["Participants"])
app.include_router(invitations.router, prefix="/boards", tags=["Invitations"])
app.include_router(search.router, prefix="/boards", tags=["Search"])

@app.get("/")
async def root():
    return {"message": "Mini Kanban Board API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}