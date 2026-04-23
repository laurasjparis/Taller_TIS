from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from .database import Base
from datetime import datetime

class ProductModel(Base):
    """
    Modelo de ORM para Producto mapeado desde SQLAlchemy hacia SQLite/Postgres.
    
    Attributes:
        id (int): Primary key numérica, auto.
        name (str): Obligatorio.
        brand (str): Columna opcional.
        category (str): Columna opcional.
        size (str): Columna opcional.
        color (str): Columna opcional.
        price (float): Decimal subyacente.
        stock (int): Unidades en DB.
        description (str): Paráfrasis para Gemini.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100))
    category = Column(String(100))
    size = Column(String(20))
    color = Column(String(50))
    price = Column(Float)
    stock = Column(Integer)
    description = Column(Text)

class ChatMemoryModel(Base):
    """
    Modelo de ORM para el Historial de Chat per session.
    
    Attributes:
        id (int): Consecutivo de la plática.
        session_id (str): UID asociado unificando diálogos.
        role (str): Contexto 'user' o 'assistant'.
        message (str): Cadena de texto muy grande si es necesario (Text).
        timestamp (datetime): Cuando el bot o el usuario lanzaron la petición.
    """
    __tablename__ = "chat_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), index=True)
    role = Column(String(20))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
