from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Library credentials (in production, these should be encrypted)
    library_card_number = Column(String, nullable=True)
    library_pin = Column(String, nullable=True)
    library_name = Column(String, nullable=True, default="Contra Costa")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    holds = relationship("Hold", back_populates="user")

class Library(Base):
    __tablename__ = "libraries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    base_url = Column(String, nullable=False)
    search_url = Column(String, nullable=True)
    login_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Hold(Base):
    __tablename__ = "holds"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Book Information
    title = Column(String, nullable=False)
    author = Column(String)
    isbn = Column(String, index=True)
    
    # Library Information
    library_name = Column(String, nullable=False) # e.g., "Contra Costa", "Alameda"
    library_item_id = Column(String, index=True) # The ID used by the library's catalog
    
    # Hold Status
    status = Column(String, default="Pending") # e.g., "Pending", "In Transit", "Ready for Pickup", "Fulfilled"
    queue_position = Column(Integer)
    estimated_wait_days = Column(Integer)
    last_checked = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="holds")

