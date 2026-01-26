# db.py
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# --- LÓGICA DE CONEXIÓN INTELIGENTE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'municipal_pa.db')

# 1. Intentamos obtener la URL desde los Secrets de Streamlit (Nube)
# 2. Si no existe, usamos SQLite (Local)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Corregimos el protocolo para SQLAlchemy
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Eliminamos el parámetro channel_binding si causa problemas en la nube
    if "channel_binding=" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.split("&channel_binding=")[0]
        
    ENGINE = create_engine(DATABASE_URL)
else:
    # Conexión local para desarrollo
    ENGINE = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})

Base = declarative_base()
Session = sessionmaker(bind=ENGINE)

# --- MODELOS ---

class Jugador(Base):
    __tablename__ = 'jugadores'
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
    __tablename__ = 'eventos'
    id = Column(Integer, primary_key=True)
    fecha = Column(String)
    rival = Column(String)
    cuota_default = Column(Integer)

class Pago(Base):
    __tablename__ = 'pagos'
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
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)

class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    tipo = Column(String)
    precio = Column(Float)

class Venta(Base):
    __tablename__ = 'ventas'
    id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    producto_id = Column(Integer)
    cantidad = Column(Integer)
    total = Column(Float)
    jugador_id = Column(Integer, ForeignKey('jugadores.id'))

# --- FUNCIONES ---

def get_session():
    return Session()

def init_db():
    Base.metadata.create_all(ENGINE)
    session = get_session()
    try:
        # Crea el admin inicial solo si la tabla está vacía
        if session.query(User).count() == 0:
            admin_user = User(username="admin", password="admin123", role="admin")
            session.add(admin_user)
            session.commit()
    except Exception as e:
        print(f"Error en init_db: {e}")
    finally:
        session.close()