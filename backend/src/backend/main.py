from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.core.dependencies import get_db
from backend.api.v1.auth import router as auth_router
from backend.api.v1.projects import router as projects_router
app = FastAPI(
    title="AI Production Incident Investigator",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(projects_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "incident-investigator",
    }


@app.get("/health/db")
def database_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
    }