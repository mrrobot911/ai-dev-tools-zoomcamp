from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from .routers import sessions, diagrams, notes, events


app = FastAPI(
    title="Interview Canvas Share API",
    description="Backend API for Interview Canvas Share application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(sessions.router)
app.include_router(diagrams.router)
app.include_router(notes.router)
app.include_router(events.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Interview Canvas Share API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)