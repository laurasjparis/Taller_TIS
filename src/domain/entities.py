from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Product:
    """
    Entidad que representa un producto en el e-commerce.
    Esta clase encapsula la lógica de negocio relacionada con productos,
    incluyendo validaciones de precio, stock y disponibilidad.

    Attributes:
        id (Optional[int]): Identificador único del producto.
        name (str): Nombre del producto.
        brand (str): Marca del producto.
        category (str): Categoría del producto.
        size (str): Talla del producto.
        color (str): Color del producto.
        price (float): Precio en dólares, debe ser mayor a 0.
        stock (int): Cantidad disponible en inventario.
        description (str): Descripción detallada del producto.
    """
    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self) -> None:
        """
        Validaciones que se ejecutan después de inicializar el objeto.
        
        Raises:
            ValueError: Si el nombre está vacío, el precio es menor o igual a 0, 
                o el stock es negativo.
        """
        if not self.name:
            raise ValueError("El nombre no puede estar vacío")
        if self.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")

    def is_available(self) -> bool:
        """
        Verifica si el producto está disponible.

        Returns:
            bool: True si el stock es mayor que cero, False en caso contrario.
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """
        Reduce el stock del producto en la cantidad especificada.
        Este método valida que haya suficiente stock antes de reducir.
        Se usa típicamente cuando se realiza una venta.

        Args:
            quantity (int): Cantidad a reducir del stock. Debe ser positivo.

        Raises:
            ValueError: Si quantity es negativo o mayor al stock disponible.
            
        Example:
            >>> product = Product(id=1, name="Zapato", brand="b", category="c", size="40", color="red", price=100.0, stock=10, description="D")
            >>> product.reduce_stock(3)
            >>> print(product.stock)
            7
        """
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva")
        if self.stock < quantity:
            raise ValueError("No hay suficiente stock")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """
        Aumenta el stock del producto en la cantidad especificada.
        
        Args:
            quantity (int): Cantidad a aumentar al stock. Debe ser positiva.
            
        Raises:
            ValueError: Si quantity es negativa o igual a cero.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva")
        self.stock += quantity

@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje en el chat.
    
    Attributes:
        id (Optional[int]): Identificador único del mensaje.
        session_id (str): Identificador de la sesión de conversación.
        role (str): Rol de quien envía el mensaje ('user' o 'assistant').
        message (str): Contenido del mensaje.
        timestamp (datetime): Fecha y hora de creación.
    """
    id: Optional[int]
    session_id: str
    role: str
    message: str
    timestamp: datetime

    def __post_init__(self) -> None:
        """
        Validaciones que se ejecutan después de inicializar el objeto.
        
        Raises:
            ValueError: Si el rol no es válido, el mensaje está vacío,
                o el session_id está vacío.
        """
        if self.role not in ['user', 'assistant']:
            raise ValueError("El rol debe ser 'user' o 'assistant'")
        if not self.message:
            raise ValueError("El mensaje no puede estar vacío")
        if not self.session_id:
            raise ValueError("El session_id no puede estar vacío")

    def is_from_user(self) -> bool:
        """
        Verifica si el mensaje pertenece al usuario.
        
        Returns:
            bool: True si el rol es 'user', False en caso contrario.
        """
        return self.role == 'user'

    def is_from_assistant(self) -> bool:
        """
        Verifica si el mensaje pertenece al asistente.
        
        Returns:
            bool: True si el rol es 'assistant', False en caso contrario.
        """
        return self.role == 'assistant'

@dataclass
class ChatContext:
    """
    Value Object que encapsula el contexto de una conversación.
    Mantiene los mensajes recientes para dar coherencia al chat.
    
    Attributes:
        messages (List[ChatMessage]): Lista completa de mensajes.
        max_messages (int): Número máximo de mensajes recientes a retornar.
    """
    messages: List[ChatMessage]
    max_messages: int = 6

    def get_recent_messages(self) -> List[ChatMessage]:
        """
        Obtiene los mensajes más recientes del historial.
        
        Returns:
            List[ChatMessage]: Sublista de hasta `max_messages` mensajes recientes.
        """
        return self.messages[-self.max_messages:] if self.messages else []

    def format_for_prompt(self) -> str:
        """
        Formatea los mensajes para incluirlos en el prompt de IA.
        
        Returns:
            str: Una cadena de texto que representa el flujo de la conversación, 
            apta para ser inyectada al contexto de la IA.
        """
        recent = self.get_recent_messages()
        formatted = []
        for msg in recent:
            sender = "Usuario" if msg.is_from_user() else "Asistente"
            formatted.append(f"{sender}: {msg.message}")
        return "\n".join(formatted)
