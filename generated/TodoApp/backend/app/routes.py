from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/tasks")
async def get_tasks():
    return {"message": "GET /tasks endpoint"}

@router.post("/tasks")
async def post_tasks():
    return {"message": "POST /tasks endpoint"}

@router.post("/auth/login")
async def post_auth_login():
    return {"message": "POST /auth/login endpoint"}

