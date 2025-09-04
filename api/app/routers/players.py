from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..db import get_db
from .. import models
from ..schemas import PlayerCreate, PlayerRead
from ..security import require_admin

def _safe_div(n: float, d: float) -> float:
    return float(n / d) if d else 0.0

router = APIRouter(prefix="/players", tags=["players"])

@router.post("", response_model=PlayerRead, status_code=201, dependencies=[Depends(require_admin)])
def create_player(payload: PlayerCreate, db: Session = Depends(get_db)):
    player = models.Player(
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        jersey_number=payload.jersey_number,
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

@router.get("", response_model=List[PlayerRead])
def list_players(
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="Search by name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    query = db.query(models.Player)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            (models.Player.first_name.ilike(term)) | (models.Player.last_name.ilike(term))
        )
    players = query.order_by(models.Player.last_name, models.Player.first_name)\
                   .offset(offset).limit(limit).all()

    # Calculate aggregated stats for each player
    result = []
    for player in players:
        # Get aggregated stats for this player
        stats_query = db.query(
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
            func.coalesce(func.sum(models.PlayerGameStat.sac_bunts), 0),
            func.coalesce(func.sum(models.PlayerGameStat.hit_by_pitches), 0),
            func.coalesce(func.sum(models.PlayerGameStat.errors), 0),
        ).filter(models.PlayerGameStat.player_id == player.id)
        
        (ab, h, s1, s2, s3, hr, rbi, bb, so, sf, sb, hbp, err) = stats_query.one()

        # Count games played separately
        games_count = db.query(func.count(models.PlayerGameStat.id)).filter(
            models.PlayerGameStat.player_id == player.id
        ).scalar() or 0

        # Calculate derived stats
        plate_appearances = int(ab + bb + hbp + sf)
        total_bases = int(s1 + 2 * s2 + 3 * s3 + 4 * hr)
        avg = _safe_div(h, ab)
        slg = _safe_div(total_bases, ab)
        obp = _safe_div(h + bb + hbp, plate_appearances)
        ops = obp + slg
        
        # Create player dict with stats
        player_dict = {
            **player.__dict__,
            'games_played': int(games_count),
            'plate_appearances': plate_appearances,
            'at_bats': int(ab),
            'hits': int(h),
            'singles': int(s1),
            'doubles': int(s2),
            'triples': int(s3),
            'home_runs': int(hr),
            'rbis': int(rbi),
            'walks': int(bb),
            'strikeouts': int(so),
            'sac_bunts': int(sb),
            'sac_flies': int(sf),
            'hit_by_pitches': int(hbp),
            'errors': int(err),
            'total_bases': total_bases,
            'average': round(avg, 3),
            'slugging': round(slg, 3),
            'on_base_percent': round(obp, 3),
            'on_base_percent_plus_slugging': round(ops, 3),
        }
        result.append(PlayerRead(**player_dict))

    return result
