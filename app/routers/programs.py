from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db import get_db

router = APIRouter(prefix="/programs", tags=["programs"])

@router.get("")
def list_programs(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT program_id, name, category FROM programs ORDER BY name ASC")
    ).mappings().all()
    return list(rows)
