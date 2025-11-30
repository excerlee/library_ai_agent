"""
Authentication service for user registration, login, and JWT token management
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from db.models import User
from schemas.schemas import UserCreate, UserLogin
import bcrypt as bcrypt_lib

# Password hashing - use bcrypt directly to avoid passlib initialization issues
pwd_context = None  # Will use bcrypt directly

# JWT settings
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt_lib.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Truncate password to 72 bytes for bcrypt (bcrypt limitation)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt_lib.gensalt(rounds=12)
    hashed = bcrypt_lib.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user with hashed password"""
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def update_library_credentials(db: Session, user_id: int, card_number: str, pin: str, library_name: str = "Contra Costa", library_id: int = None) -> User:
    """Update user's library card credentials"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # If library_id is provided, fetch library name from libraries table
    if library_id:
        from db.models import Library
        library = db.query(Library).filter(Library.id == library_id).first()
        if library:
            library_name = library.name
    
    user.library_card_number = card_number
    user.library_pin = pin
    user.library_name = library_name
    db.commit()
    db.refresh(user)
    return user

def get_user_library_credentials(db: Session, user_id: int) -> dict:
    """Get user's library credentials"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    return {
        "library_card_number": user.library_card_number,
        "library_pin": user.library_pin,
        "library_name": user.library_name or "Contra Costa"
    }
