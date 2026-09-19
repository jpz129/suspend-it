from fastapi import FastAPI

from app.api.routes.auth import auth_router

# Other component routers are wired at integration time (AGENTS.md §7):
# app.include_router(exercises_router)
# app.include_router(workouts_router)
# app.include_router(ai_workouts_router)
# app.include_router(history_router)

app = FastAPI(title="suspend-it")
app.include_router(auth_router)
