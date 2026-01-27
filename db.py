import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_engine():
    if "DATABASE_URL" not in st.secrets:
        raise RuntimeError("DATABASE_URL no encontrada en Streamlit Secrets")

    database_url = st.secrets["DATABASE_URL"]

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300
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
