from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    # In a real application, we would store a hashed password, but for this
    # example, we'll store library card credentials securely (e.g., encrypted or in a secure vault).
    # For now, we'll use a simple string field as a placeholder for a unique user identifier.
    # The actual library credentials will be stored separately or passed at runtime.
    # For simplicity in this example, we'll assume a user is defined by a username.
    
    holds = relationship("Hold", back_populates="user")

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

