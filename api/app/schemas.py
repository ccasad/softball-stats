from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator
from typing import Optional

# ---------- Players ----------
class PlayerCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    jersey_number: Optional[int] = Field(None, ge=0, le=999)

class PlayerRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    jersey_number: Optional[int]
    created_at: datetime
    # Aggregated stats
    games_played: int = 0
    plate_appearances: int = 0
    at_bats: int = 0
    hits: int = 0
    singles: int = 0
    doubles: int = 0
    triples: int = 0
    home_runs: int = 0
    rbis: int = 0
    walks: int = 0
    strikeouts: int = 0
    sac_bunts: int = 0
    sac_flies: int = 0
    total_bases: int = 0
    average: float = 0.0
    slugging: float = 0.0
    on_base_percent: float = 0.0
    on_base_percent_plus_slugging: float = 0.0
    errors: int = 0
    hit_by_pitches: int = 0
    class Config:
        from_attributes = True

# ---------- Games ----------
class GameCreate(BaseModel):
    opponent: str = Field(..., min_length=1, max_length=150)
    date: date
    time: Optional[str] = Field(None, max_length=10)
    location: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

class GameRead(BaseModel):
    id: int
    opponent: str
    date: date
    time: Optional[str]
    location: Optional[str]
    notes: Optional[str]
    score_ours: Optional[int]
    score_opponent: Optional[int]
    created_at: datetime
    class Config:
        from_attributes = True

# ---------- Player Game Stats ----------
class StatBase(BaseModel):
    at_bats: int = 0
    hits: int = 0
    singles: int = 0
    doubles: int = 0
    triples: int = 0
    home_runs: int = 0
    rbis: int = 0
    walks: int = 0
    strikeouts: int = 0
    sac_flies: int = 0
    hit_by_pitches: int = 0
    errors: int = 0

    @model_validator(mode="after")
    def check_consistency(self):
        # non-negative (pydantic ints already enforce numeric; add logic guard)
        nums = [
            self.at_bats, self.hits, self.singles, self.doubles, self.triples, self.home_runs,
            self.rbis, self.walks, self.strikeouts, self.sac_flies, self.hit_by_pitches, self.errors
        ]
        if any(n < 0 for n in nums):
            raise ValueError("All stat fields must be >= 0")
        # hits must equal singles+doubles+triples+home_runs if provided explicitly
        if self.hits != (self.singles + self.doubles + self.triples + self.home_runs):
            raise ValueError("hits must equal singles + doubles + triples + home_runs")
        # Hits cannot exceed AB + HBP + walks + sac flies (very loose sanity)
        if self.hits > (self.at_bats + self.hit_by_pitches + self.walks + self.sac_flies):
            raise ValueError("hits cannot exceed plate appearances")
        return self

class StatCreate(StatBase):
    player_id: int
    game_id: int

class StatRead(StatBase):
    id: int
    player_id: int
    game_id: int
    player_first_name: str
    player_last_name: str
    created_at: datetime
    class Config:
        from_attributes = True

# ---------- Aggregates ----------
class AggregateFilters(BaseModel):
    player_id: Optional[int] = None
    game_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None

class AggregateRead(BaseModel):
    # raw totals
    at_bats: int
    hits: int
    singles: int
    doubles: int
    triples: int
    home_runs: int
    rbis: int
    walks: int
    strikeouts: int
    sac_flies: int
    hit_by_pitches: int
    errors: int
    # derived
    total_bases: int
    average: float
    slugging: float
    on_base_percent: float
    on_base_percent_plus_slugging: float

