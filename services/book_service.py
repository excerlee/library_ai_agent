from sqlalchemy.orm import Session
from db import models
from schemas import schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_holds_by_user(db: Session, user_id: int):
    return db.query(models.Hold).filter(models.Hold.user_id == user_id).all()

def create_hold(db: Session, hold: schemas.HoldCreate):
    db_hold = models.Hold(**hold.model_dump())
    db.add(db_hold)
    db.commit()
    db.refresh(db_hold)
    return db_hold

def update_hold_status(db: Session, hold_id: int, status_update: dict):
    db_hold = db.query(models.Hold).filter(models.Hold.id == hold_id).first()
    if db_hold:
        for key, value in status_update.items():
            setattr(db_hold, key, value)
        db.commit()
        db.refresh(db_hold)
    return db_hold

