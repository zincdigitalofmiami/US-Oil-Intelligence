
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .core.config import settings
from .core.logging import setup_logging
import os

# Import all the routers
from .api.routes import router as public_router
from .api.routes_write import router as write_router
from .api.routes_admin import router as admin_router

setup_logging()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the routers with appropriate prefixes
app.include_router(public_router, prefix=settings.api_prefix)
app.include_router(write_router, prefix=settings.api_prefix)
app.include_router(admin_router, prefix=settings.api_prefix)


def start():
    """Starts the Uvicorn server."""
    import uvicorn
    uvicorn.run("svc.main:app", host="0.0.0.0", port=settings.port, reload=False)

if __name__ == "__main__":
    start()
