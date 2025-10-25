from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

# Use a SQLite database for simplicity in this example
SQLALCHEMY_DATABASE_URL = "sqlite:///./library_holds.db"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to create all tables in the engine
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

