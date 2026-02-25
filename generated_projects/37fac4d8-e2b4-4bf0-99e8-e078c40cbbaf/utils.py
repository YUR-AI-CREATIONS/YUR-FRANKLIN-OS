from typing import Dict, Any
import json
from datetime import datetime

def serialize_datetime(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def format_response(data: Any, message: str = "Success", status_code: int = 200) -> Dict[str, Any]:
    """Format API response consistently"""
    return {
        "status_code": status_code,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

def validate_uuid(uuid_string: str) -> bool:
    """Validate if string is a valid UUID"""
    try:
        import uuid
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def paginate_query(query, page: int = 1, per_page: int = 10):
    """Add pagination to SQLAlchemy query"""
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10
    if per_page > 100:  # Limit max per_page
        per_page = 100
    
    offset = (page - 1) * per_page
    return query.offset(offset).limit(per_page)