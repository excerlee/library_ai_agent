from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Book Search Schemas ---

class BookSearchQuery(BaseModel):
    query: str
    search_type: str # e.g., "title", "author", "isbn"
    library: str # e.g., "Contra Costa", "Alameda"

class BookSearchResult(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    library_item_id: str # The ID needed to place a hold
    library_name: str
    availability: str # e.g., "Available", "On Order", "1 copy, 5 holds"

# --- User Schemas ---

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass # For simplicity, we only require a username for creation

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Hold Schemas ---

class HoldBase(BaseModel):
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    library_name: str
    library_item_id: str

class PlaceHoldRequest(HoldBase):
    user_id: int
    library_card_number: str
    library_pin: str

class HoldCreate(HoldBase):
    user_id: int

class Hold(HoldBase):
    id: int
    user_id: int
    status: str
    queue_position: Optional[int] = None
    estimated_wait_days: Optional[int] = None
    last_checked: datetime

    class Config:
        from_attributes = True

