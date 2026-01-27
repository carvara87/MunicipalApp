import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Base para los modelos
Base = declarative_base()

@st.cache_resource
def get_engine():
    """Crea y cachea el motor de conexión a la base de datos."""
    if "DATABASE_URL" not in st.secrets:
        raise RuntimeError("DATABASE_URL no encontrada en Streamlit Secrets")

    database_url = st.secrets["DATABASE_URL"]

    # Corrección de protocolo para SQLAlchemy 2.0 (Neon usa postgres://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return create_engine(
        database_url,
        pool_pre_ping=True,  # Verifica si la conexión sigue viva antes de usarla
        pool_recycle=300,    # Reinicia conexiones cada 5 min para evitar cortes de Neon
        pool_size=5,         # Límite de conexiones para no saturar la capa gratuita
        max_overflow=10
    )

def init_db():
    """Crea las tablas si no existen."""
    engine = get_engine()
    # Importante: Aquí se crean las tablas basadas en tus modelos
    Base.metadata.create_all(bind=engine)

def get_session():
    """Crea una nueva sesión de base de datos."""
    engine = get_engine()
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    return SessionLocal()
