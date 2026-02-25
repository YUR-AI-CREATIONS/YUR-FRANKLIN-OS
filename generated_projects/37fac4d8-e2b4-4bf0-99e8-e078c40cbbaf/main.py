from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import uuid

app = FastAPI(
    title="Sample API",
    description="A complete REST API with CRUD operations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database (replace with real database in production)
items_db = {}

# Pydantic models
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None

class Item(ItemBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ItemResponse(BaseModel):
    data: Item
    message: str

class ItemsResponse(BaseModel):
    data: List[Item]
    total: int
    message: str

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Sample API", "version": "1.0.0"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Create item
@app.post("/items", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    item_id = str(uuid.uuid4())
    now = datetime.now()
    
    new_item = Item(
        id=item_id,
        name=item.name,
        description=item.description,
        price=item.price,
        category=item.category,
        created_at=now,
        updated_at=now
    )
    
    items_db[item_id] = new_item
    
    return ItemResponse(
        data=new_item,
        message="Item created successfully"
    )

# Get all items
@app.get("/items", response_model=ItemsResponse)
async def get_items(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None
):
    items = list(items_db.values())
    
    # Filter by category if provided
    if category:
        items = [item for item in items if item.category.lower() == category.lower()]
    
    # Apply pagination
    total = len(items)
    items = items[skip:skip + limit]
    
    return ItemsResponse(
        data=items,
        total=total,
        message="Items retrieved successfully"
    )

# Get item by ID
@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return ItemResponse(
        data=items_db[item_id],
        message="Item retrieved successfully"
    )

# Update item
@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item_update: ItemUpdate):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    existing_item = items_db[item_id]
    
    # Update only provided fields
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_item, field, value)
    
    existing_item.updated_at = datetime.now()
    
    return ItemResponse(
        data=existing_item,
        message="Item updated successfully"
    )

# Delete item
@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    deleted_item = items_db.pop(item_id)
    
    return {
        "message": "Item deleted successfully",
        "deleted_item_id": item_id
    }

# Get items by category
@app.get("/categories/{category}/items", response_model=ItemsResponse)
async def get_items_by_category(category: str, skip: int = 0, limit: int = 10):
    items = [item for item in items_db.values() if item.category.lower() == category.lower()]
    
    total = len(items)
    items = items[skip:skip + limit]
    
    return ItemsResponse(
        data=items,
        total=total,
        message=f"Items in category '{category}' retrieved successfully"
    )

# Get all categories
@app.get("/categories")
async def get_categories():
    categories = list(set(item.category for item in items_db.values()))
    return {
        "data": categories,
        "total": len(categories),
        "message": "Categories retrieved successfully"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)