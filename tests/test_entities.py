import pytest
from datetime import datetime
from src.domain.entities import Product, ChatMessage, ChatContext

class TestProduct:
    def test_product_validations(self):
        with pytest.raises(ValueError, match="El precio debe ser mayor a 0"):
            Product(id=1, name="Tenis", brand="Nike", category="Deporte", size="42", color="Negro", price=0.0, stock=10, description="Test")
        
        with pytest.raises(ValueError, match="El nombre no puede estar vacío"):
            Product(id=2, name="", brand="Nike", category="Deporte", size="42", color="Negro", price=100.0, stock=10, description="Test")
            
        with pytest.raises(ValueError, match="El stock no puede ser negativo"):
            Product(id=3, name="Tenis", brand="Nike", category="Deporte", size="42", color="Negro", price=100.0, stock=-1, description="Test")

    def test_product_methods(self):
        product = Product(
            id=1, name="Zapatos", brand="Nike", category="Deportivo",
            size="42", color="Negro", price=120.0, stock=10, description="Buen estado"
        )
        assert product.is_available() is True
        product.reduce_stock(2)
        assert product.stock == 8
        product.increase_stock(5)
        assert product.stock == 13
        
        with pytest.raises(ValueError, match="No hay suficiente stock"):
            product.reduce_stock(20)

class TestChatMessage:
    def test_chat_message_validations(self):
        with pytest.raises(ValueError, match="El rol debe ser 'user' o 'assistant'"):
            ChatMessage(id=1, session_id="123", role="admin", message="Hola", timestamp=datetime.now())
        
        with pytest.raises(ValueError):
            ChatMessage(id=1, session_id="123", role="user", message="", timestamp=datetime.now())

class TestChatContext:
    def test_format_for_prompt(self):
        msg1 = ChatMessage(id=1, session_id="1", role="user", message="Hola", timestamp=datetime.now())
        msg2 = ChatMessage(id=2, session_id="1", role="assistant", message="Hola, en qué te ayudo?", timestamp=datetime.now())
        ctx = ChatContext(messages=[msg1, msg2], max_messages=2)
        prompt = ctx.format_for_prompt()
        assert "Usuario: Hola" in prompt
        assert "Asistente: Hola, en qué te ayudo?" in prompt
