"""CORS middleware configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import parse_cors_origins, settings


def setup_cors(app: FastAPI) -> None:
    """Configure CORS for the application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=parse_cors_origins(settings.CORS_ORIGINS),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
