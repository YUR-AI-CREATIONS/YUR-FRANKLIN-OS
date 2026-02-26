"""
API Routes
TODO: Add input validation
TODO: Implement caching
"""
from fastapi import APIRouter

user_router = APIRouter(prefix="/users")

@user_router.get("/")
def get_users():
    # TODO: Add pagination
    return []

@user_router.post("/")
def create_user(data: dict):
    # TODO: Validate email format
    # TODO: Hash password
    return {"id": 1, **data}
