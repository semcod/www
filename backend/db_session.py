"""SQLAlchemy session and engine configuration."""
from os import getenv

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from config import DATABASE_URL, DB_PATH, DB_TYPE

# Determine database URL
if DB_TYPE == "postgresql" and DATABASE_URL:
    # Convert postgres:// to postgresql:// for SQLAlchemy
    db_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    db_url = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(
    db_url,
    echo=False,
    # SQLite-specific settings
    connect_args={"check_same_thread": False} if DB_TYPE == "sqlite" else {},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with all tables."""
    from db_models import Base
    Base.metadata.create_all(bind=engine)
    _run_migrations()


def _run_migrations():
    """Apply additive schema migrations for existing databases."""
    migrations = [
        "ALTER TABLE audit_results ADD COLUMN audit_meta TEXT DEFAULT '{}'",
    ]
    with engine.connect() as conn:
        for sql in migrations:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception:
                pass  # column already exists or table doesn't exist yet
