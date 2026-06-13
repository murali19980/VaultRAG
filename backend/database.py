import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import DATABASE_URL

logger = logging.getLogger(__name__)

def _get_engine():
    # If using SQLite or testing, use SQLite
    if "sqlite" in DATABASE_URL:
        return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    try:
        # Try to connect to PostgreSQL
        eng = create_engine(DATABASE_URL)
        # Verify the connection works
        with eng.connect() as conn:
            pass
        logger.info("Connected to database successfully using configured URL")
        return eng
    except Exception as e:
        sqlite_url = "sqlite:///./vaultrag.db"
        logger.warning(
            "Could not connect to database at '%s' (Error: %s). Falling back to local SQLite at '%s'",
            DATABASE_URL,
            str(e),
            sqlite_url
        )
        return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
