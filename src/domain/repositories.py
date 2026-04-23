from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage

class IProductRepository(ABC):
    """
    Interface que define el contrato para acceder a productos.
    Las implementaciones concretas estarán en la capa de infraestructura.
    """
    
    @abstractmethod
    def get_all(self) -> List[Product]:
        """
        Obtiene la lista completa de productos del repositorio.
        
        Returns:
            List[Product]: Lista de productos sin filtros.
        """
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su ID.
        
        Args:
            product_id (int): ID del producto.
            
        Returns:
            Optional[Product]: El producto si existe, de lo contrario None.
        """
        pass

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Obtiene los productos que concuerdan con cierta marca.
        
        Args:
            brand (str): Nombre de la marca.
            
        Returns:
            List[Product]: Lista de productos de esa marca.
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """
        Obtiene los productos de una categoría específica.
        
        Args:
            category (str): Categoría objetivo.
            
        Returns:
            List[Product]: Lista de productos en la categoría.
        """
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto.
        Si tiene ID, actualiza. Si no tiene ID, crea uno nuevo.
        
        Args:
            product (Product): Entidad de producto a persistir.
            
        Returns:
            Product: Entidad persistida (con ID asignado si es nuevo).
        """
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto por su ID.
        
        Args:
            product_id (int): Identificador del producto.
            
        Returns:
            bool: True si se eliminó exitosamente, False si no existía.
        """
        pass

class IChatRepository(ABC):
    """
    Interface para gestionar el historial de conversaciones.
    Las implementaciones persistirán los mensajes a medios físicos.
    """
    
    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje de la conversación.
        
        Args:
            message (ChatMessage): El mensaje a almacenar.
            
        Returns:
            ChatMessage: El mensaje persistido con su ID.
        """
        pass

    @abstractmethod
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Obtiene todo o parte del historial asociado a un session_id.
        
        Args:
            session_id (str): El id de la sesión.
            limit (Optional[int]): Máximo de registros a buscar (opcional).
            
        Returns:
            List[ChatMessage]: El historial cronológico de la sesión de chat.
        """
        pass

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """
        Borra historial completo de una sesión a partir de su session_id.
        
        Args:
            session_id (str): El id de sesión.
            
        Returns:
            int: Número de mensajes destruidos.
        """
        pass

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Obtiene los <count> mensajes ordenados ascendentemente por tiempo de vida.
        
        Args:
            session_id (str): Identificador de la sesión.
            count (int): Cantidad a la que se desea truncar los recientes.
            
        Returns:
            List[ChatMessage]: Lista de mensajes del usuario y bot en secuencia correcta.
        """
        pass
