from fastapi import FastAPI

from app.api.routes.ai_workouts import ai_workouts_router
from app.api.routes.auth import auth_router
from app.api.routes.exercises import exercises_router
from app.api.routes.history import history_router
from app.api.routes.workouts import workouts_router
from app.core.config import settings

app = FastAPI(title="suspend-it")

# Settings are loaded at import so DATABASE_URL / JWT_SECRET are available to
# the DB engine and auth dependencies. Schema changes go through alembic.
_ = settings

app.include_router(auth_router)
app.include_router(exercises_router)
app.include_router(workouts_router)
app.include_router(ai_workouts_router)
app.include_router(history_router)
