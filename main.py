from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

from db.database import get_db, init_db
from schemas import schemas
from services import book_service, library_service, auth_service, admin_service
from services.nyt_picture_books_service import fetch_nyt_picture_books

app = FastAPI(
    title="Library Hold Tracker API",
    description="API for tracking library book holds and automating hold placement.",
    version="0.1.0",
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the database and create tables
init_db()

# Security
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Dependency to get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = auth_service.decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    user = auth_service.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

def get_admin_user(current_user = Depends(get_current_user)):
    """Dependency to verify user is an admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user

@app.get("/")
def read_root():
    return {"message": "Welcome to the Library Hold Tracker API"}

# --- Authentication Endpoints ---

@app.post("/auth/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists
    if auth_service.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # Check if email already exists
    if auth_service.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = auth_service.create_user(db, user_data)
    
    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.username}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "library_name": user.library_name,
            "has_library_card": bool(user.library_card_number),
            "created_at": user.created_at
        }
    }

@app.post("/auth/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = auth_service.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.username}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "library_name": user.library_name,
            "has_library_card": bool(user.library_card_number),
            "created_at": user.created_at
        }
    }

@app.get("/auth/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "library_name": current_user.library_name,
        "has_library_card": bool(current_user.library_card_number),
        "created_at": current_user.created_at
    }

@app.put("/auth/profile", response_model=schemas.UserResponse)
def update_profile(
    profile_data: schemas.UserProfileUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile (email, username)"""
    # Check if new email is already taken by another user
    if profile_data.email:
        existing_user = auth_service.get_user_by_email(db, profile_data.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = profile_data.email
    
    # Check if new username is already taken by another user
    if profile_data.username:
        existing_user = auth_service.get_user_by_username(db, profile_data.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = profile_data.username
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "library_name": current_user.library_name,
        "has_library_card": bool(current_user.library_card_number),
        "created_at": current_user.created_at
    }

# --- Library Card Management ---

@app.post("/library-cards/update", response_model=schemas.UserResponse)
def update_library_card(
    card_data: schemas.LibraryCardUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's library card credentials.
    Can provide either library_id (preferred) or library_name.
    """
    # Validate library_id if provided
    if card_data.library_id:
        library = admin_service.get_library_by_id(db, card_data.library_id)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Library not found"
            )
        if not library.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Library is not active"
            )
    
    user = auth_service.update_library_credentials(
        db, 
        current_user.id, 
        card_data.library_card_number,
        card_data.library_pin,
        card_data.library_name or "Contra Costa",
        card_data.library_id
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "library_name": user.library_name,
        "has_library_card": True,
        "created_at": user.created_at
    }

@app.get("/library-cards/info")
def get_library_card_info(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's library card info (without exposing full PIN)"""
    if not current_user.library_card_number:
        return {
            "has_card": False,
            "library_name": None
        }
    
    return {
        "has_card": True,
        "library_name": current_user.library_name,
        "card_number_masked": f"****{current_user.library_card_number[-4:]}" if current_user.library_card_number else None
    }

# --- User Endpoints (Legacy - keep for backward compatibility) ---

@app.post("/users/", response_model=schemas.User)
def create_user_legacy(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Legacy endpoint - use /auth/register instead"""
    return auth_service.create_user(db=db, user_data=user)

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(auth_service.User).filter(auth_service.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Book Search Endpoint ---

@app.post("/books/search", response_model=List[schemas.BookSearchResult])
async def search_book_endpoint(query: schemas.BookSearchQuery):
    """
    Search a library catalog for a book. This does not require a database connection.
    """
    results = await library_service.search_library_catalog(query)
    if not results:
        raise HTTPException(status_code=404, detail="No books found matching your query.")
    return results

# --- NYT Best Sellers Picture Books Endpoint ---

@app.get("/nyt/picture-books", response_model=List[dict])
def get_nyt_picture_books():
    """
    Fetch the current NYT Best Sellers Picture Books list.
    """
    try:
        return fetch_nyt_picture_books()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch NYT picture books: {e}")

# --- Hold Management Endpoints ---

class SimplePlaceHoldRequest(schemas.BaseModel):
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    library_item_id: str
    library_name: str = "Contra Costa"

@app.post("/holds/place", response_model=schemas.Hold)
async def place_hold_endpoint(
    hold_request: SimplePlaceHoldRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Place a hold using authenticated user's library credentials
    """
    # Check if user has library credentials
    if not current_user.library_card_number or not current_user.library_pin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Library card credentials not set. Please update your library card information first."
        )
    
    # Build full hold request with user's credentials
    full_hold_request = schemas.PlaceHoldRequest(
        user_id=current_user.id,
        title=hold_request.title,
        author=hold_request.author,
        isbn=hold_request.isbn,
        library_name=hold_request.library_name,
        library_item_id=hold_request.library_item_id,
        library_card_number=current_user.library_card_number,
        library_pin=current_user.library_pin
    )
    
    # 1. Attempt to place the hold on the external library website
    try:
        hold_data = await library_service.place_hold(full_hold_request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place hold on library website: {e}"
        )

    # 2. Save the successful hold record to the database
    hold_create = schemas.HoldCreate(
        user_id=current_user.id,
        title=hold_data["title"],
        author=hold_data.get("author"),
        isbn=hold_data.get("isbn"),
        library_name=hold_data["library_name"],
        library_item_id=hold_data["library_item_id"]
    )
    db_hold = book_service.create_hold(db=db, hold=hold_create)
    
    # 3. Update the database record with the status information from the library
    # Extract only the status fields for the update
    status_fields = {k: v for k, v in hold_data.items() 
                    if k in ["status", "queue_position", "estimated_wait_days", "last_checked"]}
    book_service.update_hold_status(db, db_hold.id, status_fields)
    
    return book_service.update_hold_status(db, db_hold.id, status_fields)

@app.get("/holds/my-holds", response_model=List[schemas.Hold])
def get_my_holds(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all holds for the authenticated user
    """
    return book_service.get_holds_by_user(db, user_id=current_user.id)

@app.get("/holds/{user_id}", response_model=List[schemas.Hold])
def get_user_holds_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all tracked holds for a specific user (legacy endpoint).
    """
    return book_service.get_holds_by_user(db, user_id=user_id)

@app.post("/holds/update_all_status")
async def update_all_holds_status_endpoint(db: Session = Depends(get_db)):
    """
    Periodically check the status of all tracked holds and update the database.
    This would typically be run as a scheduled background task.
    """
    all_holds = db.query(models.Hold).all()
    updated_count = 0
    
    for hold in all_holds:
        # For a real implementation, you'd need the user's credentials to log in,
        # which would be retrieved securely (e.g., from an encrypted vault) using hold.user_id.
        # For this example, we'll use the placeholder service which doesn't need credentials.
        
        # 1. Check status on the library website
        status_update = await library_service.check_hold_status(hold)
        
        # 2. Update the database record
        book_service.update_hold_status(db, hold.id, status_update)
        updated_count += 1
        
    return {"message": f"Successfully checked and updated status for {updated_count} holds."}

# --- Admin Endpoints ---

@app.get("/admin/users", response_model=List[schemas.AdminUserResponse])
def admin_get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only)
    """
    users = admin_service.get_all_users(db, skip=skip, limit=limit)
    return users

@app.get("/admin/users/{user_id}", response_model=schemas.AdminUserResponse)
def admin_get_user(
    user_id: int,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (admin only)
    """
    user = admin_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.put("/admin/users/{user_id}", response_model=schemas.AdminUserResponse)
def admin_update_user(
    user_id: int,
    user_update: schemas.AdminUserUpdate,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update user information (admin only)
    """
    user = admin_service.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.delete("/admin/users/{user_id}")
def admin_delete_user(
    user_id: int,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete user (admin only)
    """
    # Prevent admin from deleting themselves
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = admin_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}

@app.post("/admin/users/{user_id}/promote", response_model=schemas.AdminUserResponse)
def admin_promote_user(
    user_id: int,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Promote user to admin (admin only)
    """
    user = admin_service.promote_to_admin(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@app.post("/admin/users/{user_id}/demote", response_model=schemas.AdminUserResponse)
def admin_demote_user(
    user_id: int,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Remove admin privileges (admin only)
    """
    # Prevent admin from demoting themselves
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote yourself"
        )
    
    user = admin_service.demote_from_admin(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# --- Library Management Endpoints (Admin) ---

@app.get("/admin/libraries", response_model=List[schemas.Library])
def admin_get_libraries(
    include_inactive: bool = False,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all libraries (admin only)
    """
    return admin_service.get_all_libraries(db, include_inactive=include_inactive)

@app.get("/libraries", response_model=List[schemas.Library])
def get_active_libraries(db: Session = Depends(get_db)):
    """
    Get all active libraries (public endpoint)
    """
    return admin_service.get_all_libraries(db, include_inactive=False)

@app.get("/admin/libraries/{library_id}", response_model=schemas.Library)
def admin_get_library(
    library_id: int,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get library by ID (admin only)
    """
    library = admin_service.get_library_by_id(db, library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return library

@app.post("/admin/libraries", response_model=schemas.Library, status_code=status.HTTP_201_CREATED)
def admin_create_library(
    library: schemas.LibraryCreate,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new library (admin only)
    """
    # Check if library with same name already exists
    existing = admin_service.get_library_by_name(db, library.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Library with this name already exists"
        )
    
    return admin_service.create_library(db, library)

@app.put("/admin/libraries/{library_id}", response_model=schemas.Library)
def admin_update_library(
    library_id: int,
    library_update: schemas.LibraryUpdate,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update library information (admin only)
    """
    library = admin_service.update_library(db, library_id, library_update)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return library

@app.delete("/admin/libraries/{library_id}")
def admin_delete_library(
    library_id: int,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete library (admin only)
    """
    success = admin_service.delete_library(db, library_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return {"message": "Library deleted successfully"}

@app.post("/admin/libraries/{library_id}/deactivate", response_model=schemas.Library)
def admin_deactivate_library(
    library_id: int,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate library (admin only)
    """
    library = admin_service.deactivate_library(db, library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return library

@app.post("/admin/libraries/{library_id}/activate", response_model=schemas.Library)
def admin_activate_library(
    library_id: int,
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Activate library (admin only)
    """
    library = admin_service.activate_library(db, library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library not found"
        )
    return library

