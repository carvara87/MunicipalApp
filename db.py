import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@st.cache_resource # <--- ESTO ES VITAL
def get_engine():
    if "DATABASE_URL" not in st.secrets:
        raise RuntimeError("DATABASE_URL no encontrada en Streamlit Secrets")

    database_url = st.secrets["DATABASE_URL"]

    # Tip para Neon: Asegúrate de que la URL empiece con postgresql:// 
    # y no solo postgres:// si usas SQLAlchemy 2.0
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,       # Limita las conexiones para no saturar Neon
        max_overflow=10
    )
    return engine

def get_session():
    engine = get_engine()
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    return SessionLocal()
