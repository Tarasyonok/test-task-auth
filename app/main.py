from fastapi import FastAPI

from app.router import router
from app.mock_views import mock_router

app = FastAPI(
    title="Test task",
)

app.include_router(router)
app.include_router(mock_router)
