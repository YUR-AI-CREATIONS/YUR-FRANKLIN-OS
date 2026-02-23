from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Task(BaseModel):
    title: str

