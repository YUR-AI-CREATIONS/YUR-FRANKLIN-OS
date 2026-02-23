from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    email: str
    name: str

class Task(BaseModel):
    title: str
    completed: bool

