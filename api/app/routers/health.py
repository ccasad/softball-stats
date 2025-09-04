from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from sqlalchemy import text
from ..security import require_admin

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health(db: Session = Depends(get_db)):
    # Try a simple DB query
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {"ok": True, "db": db_ok}

@router.get("/admin")
def health_admin(_: bool = Depends(require_admin)):
    return {"ok": True, "admin": True}
    