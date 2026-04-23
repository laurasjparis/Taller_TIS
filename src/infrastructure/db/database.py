from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/ecommerce_chat.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Inyecta el puente de conexión a base de datos.
    Cierra por interrupción la misma conexión al desconectarse del pool.
    
    Yields:
        Session: Sesión de SQLAlchemy en tiempo real.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.
    Esta función crea las tablas definidas en los modelos ORM
    y carga los datos iniciales si la base de datos está vacía.
    
    Returns:
        None
        
    Note:
        Esta función debe ejecutarse antes de iniciar la aplicación.
    """
    from . import models
    from .init_data import load_initial_data
    Base.metadata.create_all(bind=engine)
    load_initial_data()
