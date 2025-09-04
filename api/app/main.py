from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .routers import health
from .routers import players, games, stats

from .db import engine
from . import models  # <-- import models so metadata is registered

app = FastAPI(title="Softball Stats API")

origins = [o.strip() for o in os.getenv("API_CORS_ORIGINS", "").split(",") if o.strip()]
if not origins:
    origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- AUTO-CREATE TABLES ON STARTUP ---
@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)
# --------------------------------------

app.include_router(health.router)
app.include_router(players.router)
app.include_router(games.router)
app.include_router(stats.router)

@app.get("/")
def root():
    return {"message": "Softball Stats API is running"}
