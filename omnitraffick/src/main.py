"""Main FastAPI application for OmniTraffick."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.v1 import markets, brands, channels, campaigns, tickets

# Initialize FastAPI app
app = FastAPI(
    title="OmniTraffick",
    description="Enterprise AdOps Orchestration Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(markets.router, prefix=settings.api_v1_prefix)
app.include_router(brands.router, prefix=settings.api_v1_prefix)
app.include_router(channels.router, prefix=settings.api_v1_prefix)
app.include_router(campaigns.router, prefix=settings.api_v1_prefix)
app.include_router(tickets.router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "OmniTraffick API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
