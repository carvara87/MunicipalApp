import streamlit as st
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default='user')

@st.cache_resource
def get_engine():
    """Mantiene la conexión viva y compartida."""
    if "DATABASE_URL" not in st.secrets:
        st.error("DATABASE_URL no encontrada en Secrets.")
        st.stop()
    
    url = st.secrets["DATABASE_URL"]
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    return create_engine(
        url,
        pool_pre_ping=True,  # Verifica salud de conexión
        pool_recycle=300,    # Refresca cada 5 min
        pool_size=5
    )

def init_db():
    """Inicializa tablas y crea admin por defecto."""
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
    return sessionmaker(bind=get_engine())()
