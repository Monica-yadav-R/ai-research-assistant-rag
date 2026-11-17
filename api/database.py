
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from .model import Base


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Local SQLite database path
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

LOCAL_DATABASE_URL = f"sqlite:///{DATA_DIR / 'research_assistant.db'}"

# Select database explicitly
DATABASE_BACKEND = os.getenv(
    "DATABASE_BACKEND", "sqlite"
).lower()

if DATABASE_BACKEND == "sqlite":
    DATABASE_URL = LOCAL_DATABASE_URL
    connect_args = {"check_same_thread": False}

elif DATABASE_BACKEND == "postgresql":
    DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

    if not DATABASE_URL:
        raise RuntimeError(
            "SUPABASE_DATABASE_URL is missing from .env"
        )

    # Use Psycopg 3 with SQLAlchemy
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    connect_args = {}

else:
    raise ValueError(
        f"Unsupported DATABASE_BACKEND: {DATABASE_BACKEND}"
    )


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)


# Enable SQLite foreign keys
if DATABASE_BACKEND == "sqlite":

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Create database tables
def init_db():
    # Create users and documents tables
    Base.metadata.create_all(bind=engine)

    # Create pgvector table when using PostgreSQL
    if DATABASE_BACKEND == "postgresql":
        from api.pgvector_store import PgVectorBase

        PgVectorBase.metadata.create_all(bind=engine)


# FastAPI database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
