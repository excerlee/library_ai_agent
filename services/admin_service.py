"""
Admin service for managing users and libraries
"""
from sqlalchemy.orm import Session
from db.models import User, Library
from schemas.schemas import AdminUserUpdate, LibraryCreate, LibraryUpdate
from typing import List, Optional

# --- User Management Functions ---

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users (admin only)"""
    return db.query(User).offset(skip).limit(limit).all()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID (admin only)"""
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, user_update: AdminUserUpdate) -> Optional[User]:
    """Update user information (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    return True

def promote_to_admin(db: Session, user_id: int) -> Optional[User]:
    """Promote user to admin (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    user.is_admin = True
    db.commit()
    db.refresh(user)
    return user

def demote_from_admin(db: Session, user_id: int) -> Optional[User]:
    """Remove admin privileges (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    user.is_admin = False
    db.commit()
    db.refresh(user)
    return user

# --- Library Management Functions ---

def get_all_libraries(db: Session, include_inactive: bool = False) -> List[Library]:
    """Get all libraries"""
    query = db.query(Library)
    if not include_inactive:
        query = query.filter(Library.is_active == True)
    return query.all()

def get_library_by_id(db: Session, library_id: int) -> Optional[Library]:
    """Get library by ID"""
    return db.query(Library).filter(Library.id == library_id).first()

def get_library_by_name(db: Session, name: str) -> Optional[Library]:
    """Get library by name"""
    return db.query(Library).filter(Library.name == name).first()

def create_library(db: Session, library: LibraryCreate) -> Library:
    """Create new library (admin only)"""
    db_library = Library(**library.dict())
    db.add(db_library)
    db.commit()
    db.refresh(db_library)
    return db_library

def update_library(db: Session, library_id: int, library_update: LibraryUpdate) -> Optional[Library]:
    """Update library information (admin only)"""
    library = db.query(Library).filter(Library.id == library_id).first()
    if not library:
        return None
    
    update_data = library_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(library, field, value)
    
    db.commit()
    db.refresh(library)
    return library

def delete_library(db: Session, library_id: int) -> bool:
    """Delete library (admin only)"""
    library = db.query(Library).filter(Library.id == library_id).first()
    if not library:
        return False
    
    db.delete(library)
    db.commit()
    return True

def deactivate_library(db: Session, library_id: int) -> Optional[Library]:
    """Deactivate library instead of deleting (admin only)"""
    library = db.query(Library).filter(Library.id == library_id).first()
    if not library:
        return None
    
    library.is_active = False
    db.commit()
    db.refresh(library)
    return library

def activate_library(db: Session, library_id: int) -> Optional[Library]:
    """Activate library (admin only)"""
    library = db.query(Library).filter(Library.id == library_id).first()
    if not library:
        return None
    
    library.is_active = True
    db.commit()
    db.refresh(library)
    return library
