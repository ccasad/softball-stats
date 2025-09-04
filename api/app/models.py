from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Date, Text, ForeignKey,
    DateTime, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .db import Base

class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    jersey_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    stats: Mapped[list["PlayerGameStat"]] = relationship(
        "PlayerGameStat", back_populates="player", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Player {self.id} {self.first_name} {self.last_name}>"

class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opponent: Mapped[str] = mapped_column(String(150), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    time: Mapped[str | None] = mapped_column(String(10), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    score_ours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_opponent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    stats: Mapped[list["PlayerGameStat"]] = relationship(
        "PlayerGameStat", back_populates="game", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Game {self.id} vs {self.opponent} on {self.date}>"

class PlayerGameStat(Base):
    __tablename__ = "player_game_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False)

    # Box score (non-negative)
    at_bats: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    singles: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    doubles: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    triples: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    home_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rbis: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    walks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    strikeouts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sac_flies: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sac_bunts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hit_by_pitches: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Ensure one stats row per (player, game)
    __table_args__ = (
        UniqueConstraint("player_id", "game_id", name="uq_player_game"),
        # Basic non-negative guards (MySQL 8.0+ enforces CHECK)
        CheckConstraint("at_bats >= 0 AND hits >= 0 AND singles >= 0 AND doubles >= 0 AND triples >= 0 AND home_runs >= 0", name="ck_nonneg_hits"),
        CheckConstraint("rbis >= 0 AND walks >= 0 AND strikeouts >= 0 AND sac_flies >= 0 AND sac_bunts >= 0 AND hit_by_pitches >= 0 AND errors >= 0", name="ck_nonneg_other"),
    )

    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="stats")
    game: Mapped["Game"] = relationship("Game", back_populates="stats")

    def __repr__(self) -> str:
        return f"<Stat p={self.player_id} g={self.game_id}>"
