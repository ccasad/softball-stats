from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

def _build_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return url
    host = os.getenv("MYSQL_HOST", "").strip()
    port = os.getenv("MYSQL_PORT", "3306").strip()
    db   = os.getenv("MYSQL_DATABASE", "").strip()
    user = os.getenv("MYSQL_USER", "").strip()
    pw   = os.getenv("MYSQL_PASSWORD", "").strip()
    if not all([host, port, db, user, pw]):
        # Helpful error for logs
        missing = [k for k,v in [("MYSQL_HOST",host),("MYSQL_PORT",port),
                                 ("MYSQL_DATABASE",db),("MYSQL_USER",user),
                                 ("MYSQL_PASSWORD",pw)] if not v]
        raise RuntimeError(f"DB config missing: {', '.join(missing)}")
    return f"mysql+pymysql://{user}:{pw}@{host}:{port}/{db}"

DATABASE_URL = _build_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
