from fastapi import FastAPI

from app.api.routes.auth import auth_router
from app.core.config import settings

app = FastAPI(title="suspend-it")

# Settings are loaded at import so DATABASE_URL / JWT_SECRET are available to
# the DB engine and auth dependencies. Schema changes go through alembic.
_ = settings

app.include_router(auth_router)
# Other routers (exercises, workouts, ai_workouts, history) will be wired at integration time.
