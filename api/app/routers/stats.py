from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date
from sqlalchemy import func
from ..schemas import AggregateRead
from ..db import get_db
from .. import models
from ..schemas import StatCreate, StatRead
from ..security import require_admin

router = APIRouter(prefix="/stats", tags=["stats"])

@router.post("", response_model=StatRead, status_code=201, dependencies=[Depends(require_admin)])
def upsert_stat(payload: StatCreate, db: Session = Depends(get_db)):
    # ensure player & game exist (helpful error)
    if not db.get(models.Player, payload.player_id):
        raise HTTPException(status_code=404, detail="Player not found")
    if not db.get(models.Game, payload.game_id):
        raise HTTPException(status_code=404, detail="Game not found")

    stat = db.query(models.PlayerGameStat).filter(
        and_(
            models.PlayerGameStat.player_id == payload.player_id,
            models.PlayerGameStat.game_id == payload.game_id,
        )
    ).one_or_none()

    if stat is None:
        stat = models.PlayerGameStat(
            player_id=payload.player_id,
            game_id=payload.game_id,
        )
        db.add(stat)

    # update fields
    for field in [
        "at_bats","hits","singles","doubles","triples","home_runs",
        "rbis","walks","strikeouts","sac_flies","hit_by_pitches","errors"
    ]:
        setattr(stat, field, getattr(payload, field))

    db.commit()
    db.refresh(stat)
    
    player = db.get(models.Player, stat.player_id)
    stat_dict = {
        **stat.__dict__,
        'player_first_name': player.first_name,
        'player_last_name': player.last_name
    }
    
    return StatRead(**stat_dict)

@router.get("", response_model=List[StatRead])
def list_stats(
    db: Session = Depends(get_db),
    player_id: Optional[int] = None,
    game_id: Optional[int] = None,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    query = db.query(
        models.PlayerGameStat,
        models.Player.first_name,
        models.Player.last_name
    ).join(models.Player, models.Player.id == models.PlayerGameStat.player_id)

    if player_id is not None:
        query = query.filter(models.PlayerGameStat.player_id == player_id)
    if game_id is not None:
        query = query.filter(models.PlayerGameStat.game_id == game_id)

    results = query.order_by(
        models.PlayerGameStat.game_id.desc(), 
        models.PlayerGameStat.player_id.asc()
    ).offset(offset).limit(limit).all()

    stats = []
    for stat, first_name, last_name in results:
        stat_dict = {
            **stat.__dict__,
            'player_first_name': first_name,
            'player_last_name': last_name
        }
        stats.append(StatRead(**stat_dict))

    return stats

def _safe_div(n: float, d: float) -> float:
    return float(n / d) if d else 0.0

@router.get("/aggregate", response_model=AggregateRead)
def aggregate_stats(
    db: Session = Depends(get_db),
    player_id: Optional[int] = None,
    game_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
):
    """
    Aggregate across stats with optional filters:
      - player_id: totals for a single player
      - game_id: totals for a single game
      - date range (by Game.date): team or player within span
      - combine filters as needed (e.g., player_id + date_from/to)
    """
    q = db.query(
        func.coalesce(func.sum(models.PlayerGameStat.at_bats), 0),
        func.coalesce(func.sum(models.PlayerGameStat.hits), 0),
        func.coalesce(func.sum(models.PlayerGameStat.singles), 0),
        func.coalesce(func.sum(models.PlayerGameStat.doubles), 0),
        func.coalesce(func.sum(models.PlayerGameStat.triples), 0),
        func.coalesce(func.sum(models.PlayerGameStat.home_runs), 0),
        func.coalesce(func.sum(models.PlayerGameStat.rbis), 0),
        func.coalesce(func.sum(models.PlayerGameStat.walks), 0),
        func.coalesce(func.sum(models.PlayerGameStat.strikeouts), 0),
        func.coalesce(func.sum(models.PlayerGameStat.sac_flies), 0),
        func.coalesce(func.sum(models.PlayerGameStat.hit_by_pitches), 0),
        func.coalesce(func.sum(models.PlayerGameStat.errors), 0),
    ).join(models.Game, models.Game.id == models.PlayerGameStat.game_id)

    if player_id is not None:
        q = q.filter(models.PlayerGameStat.player_id == player_id)
    if game_id is not None:
        q = q.filter(models.PlayerGameStat.game_id == game_id)
    if date_from is not None:
        q = q.filter(models.Game.date >= date_from)
    if date_to is not None:
        q = q.filter(models.Game.date <= date_to)

    (ab, h, s1, s2, s3, hr, rbi, bb, so, sf, hbp, errs) = q.one()

    total_bases = int(s1 + 2 * s2 + 3 * s3 + 4 * hr)
    avg = _safe_div(h, ab)
    slg = _safe_div(total_bases, ab)
    obp = _safe_div(h + bb + hbp, ab + bb + hbp + sf)
    ops = obp + slg

    return AggregateRead(
        at_bats=int(ab),
        hits=int(h),
        singles=int(s1),
        doubles=int(s2),
        triples=int(s3),
        home_runs=int(hr),
        rbis=int(rbi),
        walks=int(bb),
        strikeouts=int(so),
        sac_flies=int(sf),
        hit_by_pitches=int(hbp),
        errors=int(errs),
        total_bases=total_bases,
        average=round(avg, 3),
        slugging=round(slg, 3),
        on_base_percent=round(obp, 3),
        on_base_percent_plus_slugging=round(ops, 3),
    )