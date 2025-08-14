"""FastAPI application entrypoint.

Initializes settings, logging, mounts routes, and exposes a health endpoint.
"""
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes.predict import router as predict_router
from app.config.settings import get_settings


settings = get_settings()
logging.basicConfig(level=getattr(logging, 
                                   settings.log_level.upper(), 
                                   logging.INFO))

logging.info("Initializing FastAPI application: %s v%s", 
             settings.api_project_name, 
             settings.api_version)

app = FastAPI(title=settings.api_project_name,
               version=settings.api_version)

@app.get("/health")
def health() -> JSONResponse:
    """Simple liveness probe endpoint."""
    return JSONResponse({"status": "ok"})

app.include_router(
    predict_router,
    prefix=settings.api_major_version,
    tags=["inference"],
)


