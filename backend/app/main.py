"""XP Architect API - FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_all_tables
from app.routers import auth, projects, sessions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    create_all_tables()
    yield


app = FastAPI(
    title="XP Architect API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(sessions.router)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}
