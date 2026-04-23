from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class ProductDTO(BaseModel):
    """
    DTO para transferir datos de productos.
    Pydantic valida automáticamente los tipos integrados.
    
    Attributes:
        id (Optional[int]): Identificador de la base de datos (por defecto None si es nuevo).
        name (str): Nombre estricto del producto.
        brand (str): Marca del calzado.
        category (str): Categoría (por defecto: Running, Deportivo, etc).
        size (str): Talla internacional.
        color (str): Descripción del color.
        price (float): Valor mayor a cero.
        stock (int): Unidades en posesión mayores a (o igual a) cero.
        description (str): Descripción libre del zapato a sugerir.
    """
    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        """
        Valida que el precio sea mayor a 0.
        
        Raises:
            ValueError: Si el precio es <= 0.
        """
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

    @field_validator('stock')
    @classmethod
    def stock_must_be_non_negative(cls, v):
        """
        Valida que el stock no sea negativo.
        
        Raises:
            ValueError: Si es negativo.
        """
        if v < 0:
            raise ValueError("El stock no puede estar en negativo")
        return v

    model_config = ConfigDict(from_attributes=True)

class ChatMessageRequestDTO(BaseModel):
    """
    DTO para recibir mensajes del usuario mediante POST HTTP.
    
    Attributes:
        session_id (str): Llave de sesión que agrupa al usuario.
        message (str): Cadena de texto consultando el zapato.
    """
    session_id: str
    message: str

    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v):
        """Valida que el mensaje a la IA no esté vacío o compuesto por espacios."""
        if not v.strip():
            raise ValueError("El mensaje no puede estar vacío")
        return v

    @field_validator('session_id')
    @classmethod
    def session_id_not_empty(cls, v):
        """Garantiza la asociación contextual evadiendo session_ids corruptos."""
        if not v.strip():
            raise ValueError("El session_id no puede estar vacío")
        return v

class ChatMessageResponseDTO(BaseModel):
    """
    DTO para agrupar y confirmar exitosamente respuestas del chat.
    
    Attributes:
        session_id (str): Id de la sesión referida.
        user_message (str): Mensaje enviado.
        assistant_message (str): Contestación de la IA.
        timestamp (datetime): Cuando el mensaje finalizó.
    """
    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime

class ChatHistoryDTO(BaseModel):
    """
    DTO para mostrar todo el historial ordenado temporalmente en una respuesta GET.
    
    Attributes:
        id (int): Id de fila.
        role (str): Rol que envía ("user" / "assistant").
        message (str): Mensaje crudo.
        timestamp (datetime): Hora real de ocurrencia.
    """
    id: int
    role: str
    message: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
