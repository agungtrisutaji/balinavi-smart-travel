from fastapi import FastAPI

from app.backend.api.routes import router
from app.backend.core.config import APP_NAME, APP_VERSION


app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.include_router(router)
