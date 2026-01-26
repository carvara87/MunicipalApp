from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import os

Base = declarative_base()

# ===============================
# CONEXIÓN A BASE DE DATOS
# ===============================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    ENGINE = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"connect_timeout": 5}
    )
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "municipal_pa.db")
    ENGINE = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(bind=ENGINE)

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
