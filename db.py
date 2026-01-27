import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_engine():
    """
    Crea el engine SOLO cuando se llama.
    Evita crashes al iniciar Streamlit.
    """
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("❌ DATABASE_URL no está definida en Streamlit Secrets")

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300
    )

    return engine


def get_session():
    """
    Retorna una sesión lista para usar
    """
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
