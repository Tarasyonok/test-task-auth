from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user

from app.models import User

mock_router = APIRouter(prefix="/mock", tags=["Mock"])

mock_posts = [
    {"id": 1, "title": "First Post", "author_id": 1},
    {"id": 2, "title": "Second Post", "author_id": 2},
    {"id": 3, "title": "More Posts", "author_id": 1},
    {"id": 4, "title": "More Posts", "author_id": 2},
]


@mock_router.get("/posts")
async def list_posts(user: User = Depends(get_current_user)):
    return mock_posts


@mock_router.get("/posts/{post_id}")
async def get_post(post_id: int, user: User = Depends(get_current_user)):
    post = next((p for p in mock_posts if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post["author_id"] != user.id and not user.role.name == "admin":
        raise HTTPException(status_code=403, detail="Not your post")
    return post
