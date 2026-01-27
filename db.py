import streamlit as st
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

# Modelo de Usuario para el acceso
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default='user')

@st.cache_resource
def get_engine():
    """Crea el motor de base de datos con caché para evitar reconexiones constantes."""
    if "DATABASE_URL" not in st.secrets:
        raise RuntimeError("No se encontró DATABASE_URL en Secrets")
    
    url = st.secrets["DATABASE_URL"]
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10
    )

def init_db():
    """Inicializa tablas y crea el admin inicial."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        if not session.query(User).filter_by(username='admin').first():
            admin = User(username='admin', password='admin123', role='admin')
            session.add(admin)
            session.commit()
    finally:
        session.close()

def get_session():
    """Genera una sesión para consultas."""
    engine = get_engine()
    return sessionmaker(bind=engine)()
