from fastapi import FastAPI

from app.router import router

app = FastAPI(
    title="Test task",
)

app.include_router(router)
