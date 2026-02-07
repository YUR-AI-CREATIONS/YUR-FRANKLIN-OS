from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/products")
async def get_products():
    return {"message": "GET /products endpoint"}

@router.post("/products")
async def post_products():
    return {"message": "POST /products endpoint"}

@router.get("/cart")
async def get_cart():
    return {"message": "GET /cart endpoint"}

@router.post("/cart/add")
async def post_cart_add():
    return {"message": "POST /cart/add endpoint"}

@router.post("/checkout")
async def post_checkout():
    return {"message": "POST /checkout endpoint"}

