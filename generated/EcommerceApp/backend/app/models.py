from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Product(BaseModel):
    name: str
    price: float
    description: str

class Cart(BaseModel):
    user_id: str
    items: str

class Order(BaseModel):
    total: float
    status: str

