from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select
from .db import SessionLocal, engine
from . import models

def ensure_tables():
    models.Base.metadata.create_all(bind=engine)

def upsert_player(db: Session, first, last, num=None):
    existing = db.execute(
        select(models.Player).where(
            models.Player.first_name==first, models.Player.last_name==last
        )
    ).scalar_one_or_none()
    if existing:
        return existing
    p = models.Player(first_name=first, last_name=last, jersey_number=num)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def upsert_game(db: Session, opponent, when, location=None, notes=None):
    existing = db.execute(
        select(models.Game).where(
            models.Game.opponent==opponent, models.Game.date==when
        )
    ).scalar_one_or_none()
    if existing:
        return existing
    g = models.Game(opponent=opponent, date=when, location=location, notes=notes)
    db.add(g)
    db.commit()
    db.refresh(g)
    return g

def upsert_stat(db: Session, player_id, game_id, **kws):
    existing = db.execute(
        select(models.PlayerGameStat).where(
            models.PlayerGameStat.player_id==player_id,
            models.PlayerGameStat.game_id==game_id
        )
    ).scalar_one_or_none()
    if existing:
        for k,v in kws.items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    stat = models.PlayerGameStat(player_id=player_id, game_id=game_id, **kws)
    db.add(stat)
    db.commit()
    db.refresh(stat)
    return stat

def main():
    ensure_tables()
    db = SessionLocal()
    try:
        # Players
        alex   = upsert_player(db, "Alex", "Morgan", 10)
        riley  = upsert_player(db, "Riley", "Parker", 7)
        taylor = upsert_player(db, "Taylor", "Kim", 22)

        # Games
        g1 = upsert_game(db, "Blue Jays", date(2025, 4, 12), "Field 1")
        g2 = upsert_game(db, "Cardinals", date(2025, 4, 19), "Field 2")

        # Stats (keep hits = 1B+2B+3B+HR)
        upsert_stat(db, alex.id, g1.id,
            at_bats=4, hits=2, singles=1, doubles=1, triples=0, home_runs=0,
            rbis=2, walks=1, strikeouts=1, sac_flies=0, hit_by_pitches=0, errors=0
        )
        upsert_stat(db, riley.id, g1.id,
            at_bats=3, hits=1, singles=1, doubles=0, triples=0, home_runs=0,
            rbis=1, walks=0, strikeouts=1, sac_flies=0, hit_by_pitches=0, errors=1
        )
        upsert_stat(db, taylor.id, g2.id,
            at_bats=4, hits=3, singles=1, doubles=1, triples=0, home_runs=1,
            rbis=3, walks=0, strikeouts=0, sac_flies=0, hit_by_pitches=0, errors=0
        )
        print("Seed complete.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
