from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/tasks")
async def tasks():
    return {"message": "endpoint generated"}

@router.post("/tasks")
async def tasks():
    return {"message": "endpoint generated"}

