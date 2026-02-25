from sqlalchemy.orm import Session
from database import ItemModel
from typing import List, Optional
import uuid
from datetime import datetime

def create_item(db: Session, item_data: dict) -> ItemModel:
    db_item = ItemModel(
        id=str(uuid.uuid4()),
        **item_data
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_item(db: Session, item_id: str) -> Optional[ItemModel]:
    return db.query(ItemModel).filter(ItemModel.id == item_id).first()

def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None
) -> List[ItemModel]:
    query = db.query(ItemModel)
    
    if category:
        query = query.filter(ItemModel.category.ilike(f"%{category}%"))
    
    return query.offset(skip).limit(limit).all()

def update_item(db: Session, item_id: str, item_data: dict) -> Optional[ItemModel]:
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    
    if db_item:
        for key, value in item_data.items():
            if hasattr(db_item, key) and value is not None:
                setattr(db_item, key, value)
        
        db_item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_item)
    
    return db_item

def delete_item(db: Session, item_id: str) -> bool:
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    
    return False

def get_categories(db: Session) -> List[str]:
    result = db.query(ItemModel.category).distinct().all()
    return [category[0] for category in result]