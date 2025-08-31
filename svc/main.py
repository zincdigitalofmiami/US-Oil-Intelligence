from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.logging import setup_logging
from .api.routes import router

setup_logging()
app = FastAPI(title=settings.app_name)
app.add_middleware(CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_allow_origins.split(',') if o.strip()],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_prefix)

@app.get("/")
def root(): return {"name": settings.app_name, "env": settings.env}

def start():
    import uvicorn
    uvicorn.run("svc.main:app", host="0.0.0.0", port=settings.port, reload=False)

if __name__ == "__main__": start()
