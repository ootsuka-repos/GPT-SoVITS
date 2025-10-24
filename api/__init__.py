"""API package for GPT-SoVITS FastAPI application."""

from .main import app  # re-export for `uvicorn api:app`

__all__ = ["app"]
