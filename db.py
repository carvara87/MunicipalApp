import streamlit as st
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

# Base para los modelos
Base = declarative_base()

# Modelo de Usuario para el Login
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default='user')

@st.cache_resource
def get_engine():
    """Crea y cachea el motor de conexión a la base de datos."""
    if "DATABASE_URL" not in st.secrets:
        raise RuntimeError("DATABASE_URL no encontrada en Streamlit Secrets")

    database_url = st.secrets["DATABASE_URL"]

    # Corrección de protocolo para SQLAlchemy 2.0
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return create_engine(
        database_url,
        pool_pre_ping=True,  # Verifica si la conexión está viva
        pool_recycle=300,    # Evita que Neon cierre la conexión por inactividad
        pool_size=5,
        max_overflow=10
    )

def init_db():
    """Crea las tablas y el usuario administrador inicial."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    
    # Crear usuario administrador inicial (admin/admin123)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        if not session.query(User).filter_by(username='admin').first():
            admin_user = User(username='admin', password='admin123', role='admin')
            session.add(admin_user)
            session.commit()
    finally:
        session.close()

def get_session():
    """Crea una nueva sesión de base de datos."""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
