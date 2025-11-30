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
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_admin: bool = False
    library_name: Optional[str] = None
    has_library_card: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    library_card_number: Optional[str] = None
    library_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class LibraryCardUpdate(BaseModel):
    library_card_number: str
    library_pin: str
    library_id: Optional[int] = None  # Library ID from libraries table
    library_name: Optional[str] = None  # For backward compatibility

class UserProfileUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

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

# --- Library Management Schemas ---

class LibraryBase(BaseModel):
    name: str
    base_url: str
    search_url: Optional[str] = None
    login_url: Optional[str] = None
    description: Optional[str] = None

class LibraryCreate(LibraryBase):
    pass

class LibraryUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    search_url: Optional[str] = None
    login_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class Library(LibraryBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- Admin User Management Schemas ---

class AdminUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = None
    library_card_number: Optional[str] = None
    library_pin: Optional[str] = None
    library_name: Optional[str] = None

class AdminUserResponse(UserBase):
    id: int
    is_admin: bool
    library_card_number: Optional[str] = None
    library_pin: Optional[str] = None
    library_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

