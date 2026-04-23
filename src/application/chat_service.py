"""
Servicio de chat AI: Coordina las llamadas entre base de datos, memoria y el IA LLM.
"""
from typing import List
from datetime import datetime
from src.domain.repositories import IProductRepository, IChatRepository
from src.domain.entities import ChatMessage, ChatContext
from src.domain.exceptions import ChatServiceError
from .dtos import ChatMessageRequestDTO, ChatMessageResponseDTO, ChatHistoryDTO

class ChatService:
    """
    Servicio de aplicación para gestionar el chat con IA.
    Este servicio orquesta la interacción entre el repositorio de productos,
    el repositorio de chat y el servicio de IA de Gemini para proporcionar
    respuestas contextuales a los usuarios.
    
    Attributes:
        product_repo (IProductRepository): Repositorio de productos.
        chat_repo (IChatRepository): Repositorio de mensajes de chat.
        ai_service (GeminiService): Servicio de IA de Google Gemini.
    """
    def __init__(self, product_repo: IProductRepository, chat_repo: IChatRepository, ai_service):
        """
        Inicializa las dependencias externas integrando SQLs en su flujo.
        """
        self.product_repo = product_repo
        self.chat_repo = chat_repo
        self.ai_service = ai_service

    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """
        Procesa un mensaje del usuario y genera una respuesta con IA.
        Este método realiza el flujo completo:
        1. Obtiene productos disponibles
        2. Recupera historial de conversación
        3. Genera respuesta con IA usando contexto
        4. Guarda mensaje del usuario y respuesta
        5. Retorna la respuesta
        
        Args:
            request (ChatMessageRequestDTO): Mensaje del usuario con session_id y cuerpo textual.
            
        Returns:
            ChatMessageResponseDTO: Respuesta generada por la IA con timestamp.
            
        Raises:
            ChatServiceError: Si hay un error de parseo o una pérdida extrema en el LLMProvider.
            
        Example:
            >>> request = ChatMessageRequestDTO(
            ...     session_id="user123",
            ...     message="Busco zapatos Nike"
            ... )
            >>> response = await chat_service.process_message(request)
            >>> print(response.assistant_message)
            "Tengo varios modelos Nike disponibles..."
        """
        try:
            # 1. Traer productos disponibles y formatearlos para la IA
            all_products = self.product_repo.get_all()
            available = [p for p in all_products if p.is_available()]
            
            # 2. Historial reciente (últimos 6 por límite natural del entity)
            history_entities = self.chat_repo.get_recent_messages(request.session_id, count=6)
            
            # 3. Construir contexto
            context = ChatContext(messages=history_entities, max_messages=6)
            context_prompt = context.format_for_prompt()
            
            # 4. Llamar IA
            response_text = await self.ai_service.generate_response(
                user_message=request.message,
                products=available,
                context_prompt=context_prompt
            )
            
            now = datetime.utcnow()
            
            # 5 y 6. Guardar en repositorio
            user_msg = ChatMessage(id=None, session_id=request.session_id, role="user", message=request.message, timestamp=now)
            assistant_msg = ChatMessage(id=None, session_id=request.session_id, role="assistant", message=response_text, timestamp=now)
            
            self.chat_repo.save_message(user_msg)
            self.chat_repo.save_message(assistant_msg)
            
            # 7. Regresar respuesta en un envoltorio estandar
            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=response_text,
                timestamp=now
            )
        except Exception as e:
            raise ChatServiceError(f"Error procesando mensaje: {str(e)}")

    def get_session_history(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """
        Obtiene todo el historial de la sesión solicitada en listado regular.
        Útil para renderizar el chat completo en React Frontend o en un cliente móvil.
        
        Args:
            session_id (str): Identificador clave del usuario actual.
            limit (int): Límite estándar temporal configurable a la GUI.
            
        Returns:
            List[ChatMessage]: Mensajes entrelazados user/assistant.
        """
        return self.chat_repo.get_session_history(session_id, limit)

    def clear_session_history(self, session_id: str) -> int:
        """
        Limpia el contexto a cero por abandono de sesión o petición pura.
        
        Args:
            session_id (str): Sesión temporal de compra o usuario registrado.
            
        Returns:
            int: Entero describiendo cuantas filas fueron liberadas del SQLite / DB.
        """
        return self.chat_repo.delete_session_history(session_id)
