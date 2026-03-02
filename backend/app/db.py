from pathlib import Path
from sqlmodel import SQLModel, create_engine

# Single SQLite DB file for everything (V1)
DB_PATH = Path(__file__).resolve().parents[2] / "paloma_v1.sqlite3"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},  # needed for FastAPI + SQLite
)

def init_db() -> None:
    """Create tables if they don't exist."""
    SQLModel.metadata.create_all(engine)