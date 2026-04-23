from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel

class SQLChatRepository(IChatRepository):
    """
    Repositorio de Chats acoplado a la infraestructura (SQLAlchemy).
    Protege a la aplicación de acoplarse con la sintaxis Query y sus fallos.
    """
    def __init__(self, db: Session):
        """
        Args:
            db (Session): Abstracción SQL Session desde el DI contenedor FastAPI.
        """
        self.db = db

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """Transformador a Entity."""
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp
        )

    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """Transformador a Registro Base."""
        return ChatMemoryModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp
        )

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Escribe individualmente por commit a ChatMessage.
        
        Args:
            message (ChatMessage): Conversación actual de bot/usuario.
            
        Returns:
            ChatMessage: Devuelve con ID final numérico auto-asignado.
        """
        model = self._entity_to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Exporta completo (ascendente) todos los textos grabados por un usuario en específico.
        
        Args:
            session_id (str): La cookie o uid referencial.
            limit (Optional[int]): Filtro general de filas.
            
        Returns:
            List[ChatMessage]: Entidades seguras del Dominio.
        """
        query = self.db.query(ChatMemoryModel).filter(ChatMemoryModel.session_id == session_id).order_by(ChatMemoryModel.timestamp.asc())
        if limit is not None:
            query = query.limit(limit)
        models = query.all()
        return [self._model_to_entity(m) for m in models]

    def delete_session_history(self, session_id: str) -> int:
        """
        Borrado masivo transaccional en tabla chat_memory para una sesión clave.
        """
        deleted_count = self.db.query(ChatMemoryModel).filter(ChatMemoryModel.session_id == session_id).delete()
        self.db.commit()
        return deleted_count

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Truncador vital de contexto que rescata los n últimos mensajes y
        los voltea cronológicamente para dar a la IA un sentido ascendente de orden temporal.
        
        Args:
            session_id (str): UID de la charla activa.
            count (int): Límite.
            
        Returns:
            List[ChatMessage]: Lo más reciente.
        """
        models = self.db.query(ChatMemoryModel)\
            .filter(ChatMemoryModel.session_id == session_id)\
            .order_by(desc(ChatMemoryModel.timestamp))\
            .limit(count)\
            .all()
        # Invertir para retornar en orden cronológico real
        models.reverse()
        return [self._model_to_entity(m) for m in models]
