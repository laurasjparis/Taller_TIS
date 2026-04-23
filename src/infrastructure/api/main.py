from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List, Optional
from sqlalchemy.orm import Session

from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.llm_providers.gemini_service import GeminiService

from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.application.dtos import ProductDTO, ChatMessageRequestDTO, ChatMessageResponseDTO, ChatHistoryDTO
from src.domain.exceptions import ProductNotFoundError

import datetime

app = FastAPI(
    title="E-commerce AI Chat API",
    description="API for E-commerce Shoe Store with AI Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """
    Función de callback pre-arranques del ciclo asíncrono de servidor (Uvicorn).
    Delegará el mandato a `init_db` a fin de ejecutar la carga de 10 productos base iniciales.
    """
    init_db()

@app.get("/", include_in_schema=False)
def serve_frontend():
    import os
    index_path = os.path.join(os.getcwd(), "frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}

@app.get("/api/health", tags=["Info"])
def health():
    """
    Health check (Comprobaciones sanitarias Liveness).
    Principalmente util si se anela la inclusión a micro-servicios en Kubernetes u orquestación Docker externa.
    """
    return {"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()}

# Inversión de dependencias de repositorios y Containerización ligera

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """
    Dependencia FastAPI proveedora de la capa transversal de dominio encapsulada en la Aplicación
    para consultar a Products a través del SQLAlchemy Session inyectada.
    """
    return ProductService(SQLProductRepository(db))

def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    """
    Dependencia FastAPI orquestadora. Entrelaza múltiples depósitos (Chat + Product) al mismo LLMService
    garantizando cohesión y desacomplamiento para el ChatService principal.
    """
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    ai_service = GeminiService()
    return ChatService(product_repo, chat_repo, ai_service)

# ================= RUTAS Y CONTROLADORES API ================= #

@app.get("/api/products", response_model=List[ProductDTO], tags=["Products"])
def get_products(service: ProductService = Depends(get_product_service)):
    """
    Obtiene la lista completa de productos disponibles.
    Este endpoint retorna todos los productos registrados en la base de datos,
    incluyendo aquellos sin stock.
    
    Args:
        service (ProductService): Servicio de productos inyectado a la vista.
        
    Returns:
        List[ProductDTO]: Lista de productos formados con toda su infraestructura limpia.
        
    Example:
        GET /products
        Response: [
            {
                "id": 1,
                "name": "Nike Air Zoom",
                "price": 120.0,
                "stock": 5, ...
            }
        ]
    """
    return service.get_all_products()

@app.get("/api/products/{product_id}", response_model=ProductDTO, tags=["Products"])
def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    """
    Aisla un elemento unitario en el Catálogo a través de su PrimaryKey idéntica.
    
    Args:
        product_id (int): Identificador en la URL (path parameter).
        service (ProductService): Dependencia inyectada.
        
    Raises:
        HTTPException: HTTP 404 lanzado si falla ProductNotFoundError.
        
    Returns:
        ProductDTO: La envoltura y JSON final.
    """
    try:
        return service.get_product_by_id(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/chat", response_model=ChatMessageResponseDTO, tags=["Chat"])
async def chat(request: ChatMessageRequestDTO, service: ChatService = Depends(get_chat_service)):
    """
    Escucha la pregunta y dispara asíncronamente a los motores conversacionales en Gemini, procesando 
    historial subyacentemente y retornando una respuesta viva.
    
    Args:
        request (ChatMessageRequestDTO): Carga post (Payload) validada.
        service (ChatService): Orquestador LLM Inyectado.
        
    Returns:
        ChatMessageResponseDTO: Cuerpo compuesto post-Generative IA y confirmación temporal.
    """
    try:
        return await service.process_message(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history/{session_id}", response_model=List[ChatHistoryDTO], tags=["Chat"])
def get_chat_history(session_id: str, limit: int = 10, service: ChatService = Depends(get_chat_service)):
    """
    Obtiene para el Frontend/UI el historial entero de una conversación previa.
    
    Args:
        session_id (str): UID correlacional a través de query params.
        limit (int): Delimitador extrañamente alto (10).
        service (ChatService): Orquestador Inyectado AI.
        
    Returns:
        List[ChatHistoryDTO]: Lista cronológica entrelazando bots y humanos listos para ser iterados (map) en GUI.
    """
    history = service.get_session_history(session_id, limit)
    return [ChatHistoryDTO.model_validate(msg) for msg in history]

@app.delete("/api/chat/history/{session_id}", tags=["Chat"])
def delete_chat_history(session_id: str, service: ChatService = Depends(get_chat_service)):
    """
    Suprime definitivamente todo registro en SQL para la sesión indicada, restaurando parámetros AI a cero.
    """
    deleted = service.clear_session_history(session_id)
    return {"deleted_messages": deleted}
