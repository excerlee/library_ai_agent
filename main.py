from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db, init_db
from schemas import schemas
from services import book_service, library_service

app = FastAPI(
    title="Library Hold Tracker API",
    description="API for tracking library book holds and automating hold placement.",
    version="0.1.0",
)

# Initialize the database and create tables
init_db()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Library Hold Tracker API"}

# --- User Endpoints (for simplicity, just create and get) ---

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return book_service.create_user(db=db, user=user)

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = book_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

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

# --- Hold Management Endpoints ---

@app.post("/holds/place", response_model=schemas.Hold)
async def place_hold_endpoint(hold_request: schemas.PlaceHoldRequest, db: Session = Depends(get_db)):
    """
    Logs into the specified library, places the hold, and saves the hold record to the database.
    """
    # 1. Attempt to place the hold on the external library website
    try:
        hold_data = await library_service.place_hold(hold_request)
    except Exception as e:
        # In a real app, you'd handle specific login/hold errors
        raise HTTPException(status_code=500, detail=f"Failed to place hold on library website: {e}")

    # 2. Save the successful hold record to the database
    hold_create = schemas.HoldCreate(
        user_id=hold_request.user_id,
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

@app.get("/holds/{user_id}", response_model=List[schemas.Hold])
def get_user_holds_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all tracked holds for a specific user.
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

