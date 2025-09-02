
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.logging import setup_logging
import os

# Import the Forecaster
from .services.forecasting import Forecaster

# Import all the routers
from .api.routes import router as public_router
from .api.routes_write import router as write_router
from .api.routes_admin import router as admin_router
from .routers.secrets_management import router as secrets_router # Import the new router

setup_logging()
app = FastAPI(title=settings.app_name)

# --- Application State ---
# Create a single, shared instance of the Forecaster. 
# This will load the model from the path specified in the settings.
app.state.forecaster = Forecaster(model_path=settings.model_path)
# -------------------------

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
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

# Include the new secrets management router
app.include_router(secrets_router, prefix="/admin", tags=["Secrets Management"])

def start():
    """Starts the Uvicorn server."""
    import uvicorn
    uvicorn.run("svc.main:app", host="0.0.0.0", port=settings.port, reload=False)

if __name__ == "__main__":
    start()
