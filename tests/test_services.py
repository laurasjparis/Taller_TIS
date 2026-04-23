import pytest
from unittest.mock import Mock, AsyncMock
from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.application.dtos import ProductDTO, ChatMessageRequestDTO
from src.domain.entities import Product
from src.domain.exceptions import ProductNotFoundError

class TestProductService:
    def test_get_product_success(self):
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = Product(
            id=1, name="Tenis", brand="Nike", category="Deportivo",
            size="42", color="Blanco", price=100.0, stock=5, description="Test"
        )
        
        service = ProductService(mock_repo)
        result = service.get_product_by_id(1)
        
        assert result.id == 1
        assert result.name == "Tenis"
        mock_repo.get_by_id.assert_called_once_with(1)

    def test_get_product_not_found(self):
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None
        
        service = ProductService(mock_repo)
        
        with pytest.raises(ProductNotFoundError):
            service.get_product_by_id(99)

class TestChatService:
    @pytest.mark.asyncio
    async def test_process_message_success(self):
        mock_product_repo = Mock()
        mock_product_repo.get_all.return_value = []
        
        mock_chat_repo = Mock()
        mock_chat_repo.get_recent_messages.return_value = []
        
        mock_ai_service = AsyncMock()
        mock_ai_service.generate_response.return_value = "Hola desde AI"
        
        service = ChatService(mock_product_repo, mock_chat_repo, mock_ai_service)
        request = ChatMessageRequestDTO(session_id="s1", message="Hola")
        
        response = await service.process_message(request)
        assert response.assistant_message == "Hola desde AI"
        assert response.user_message == "Hola"
        assert mock_chat_repo.save_message.call_count == 2
