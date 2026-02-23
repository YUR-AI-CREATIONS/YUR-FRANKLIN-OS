from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/tasks")
async def get_tasks():
    return {"message": "GET /tasks endpoint"}

