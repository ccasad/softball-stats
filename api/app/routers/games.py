from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..db import get_db
from .. import models
from ..schemas import GameCreate, GameRead
from ..security import require_admin

router = APIRouter(prefix="/games", tags=["games"])

@router.post("", response_model=GameRead, status_code=201, dependencies=[Depends(require_admin)])
def create_game(payload: GameCreate, db: Session = Depends(get_db)):
    game = models.Game(
        opponent=payload.opponent.strip(),
        date=payload.date,
        location=payload.location.strip() if payload.location else None,
        notes=payload.notes,
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

@router.get("", response_model=List[GameRead])
def list_games(
    db: Session = Depends(get_db),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    opponent: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    query = db.query(models.Game)
    if opponent:
        query = query.filter(models.Game.opponent.ilike(f"%{opponent.strip()}%"))
    if date_from:
        query = query.filter(models.Game.date >= date_from)
    if date_to:
        query = query.filter(models.Game.date <= date_to)
    games = query.order_by(models.Game.date.desc())\
                 .offset(offset).limit(limit).all()
    return games
