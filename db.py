# db.py
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import os

Base = declarative_base()

# ===============================
# CONEXIÓN A BASE DE DATOS
# ===============================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL no está definida en Secrets")

ENGINE = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False)

# ===============================
# MODELOS
# ===============================

class Jugador(Base):
    __tablename__ = "jugadores"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    rut = Column(String, unique=True)
    serie = Column(String)
    fecha_nacimiento = Column(Date)
    edad = Column(Integer)
    telefono = Column(String)
    nacionalidad = Column(String)
    email = Column(String)

class Evento(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True)
    fecha = Column(String)
    rival = Column(String)
    cuota_default = Column(Integer)

class Pago(Base):
    __tablename__ = "pagos"
    id = Column(Integer, primary_key=True)
    fecha = Column(String)
    rival = Column(String)
    nombre = Column(String)
    serie = Column(String)
    n_camiseta = Column(Integer)
    cuota = Column(Integer)
    pagado = Column(Integer)
    estado = Column(String)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    tipo = Column(String)
    precio = Column(Float)

class Venta(Base):
    __tablename__ = "ventas"
    id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    producto_id = Column(Integer)
    cantidad = Column(Integer)
    total = Column(Float)
    jugador_id = Column(Integer, ForeignKey("jugadores.id"))

# ===============================
# HELPERS
# ===============================

def get_session():
    return SessionLocal()

def init_db():
    Base.metadata.create_all(bind=ENGINE)

    session = get_session()
    try:
        admin = session.query(User).filter_by(username="admin").first()
        if not admin:
            session.add(User(username="admin", password="admin123", role="admin"))
            session.commit()
    finally:
        session.close()
