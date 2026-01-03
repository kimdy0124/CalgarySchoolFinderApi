from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db import get_db

router = APIRouter(prefix="/districts", tags=["districts"])

@router.get("")
def list_districts(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT district_id, name, type, website_url FROM districts ORDER BY name ASC")
    ).mappings().all()
    return list(rows)
