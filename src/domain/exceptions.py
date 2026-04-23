"""
Excepciones específicas del dominio.
Representan errores de negocio, no errores técnicos.
"""

class ProductNotFoundError(Exception):
    """
    Se lanza cuando se busca o altera un producto que no existe dentro del dominio.
    
    Attributes:
        product_id (int, optional): ID del producto no hallado.
    """
    def __init__(self, product_id: int = None):
        if product_id:
            self.message = f"Producto con ID {product_id} no encontrado"
        else:
            self.message = "Producto no encontrado"
        super().__init__(self.message)

class InvalidProductDataError(Exception):
    """
    Se lanza cuando los datos de un producto son inválidos (ej. precio negativo, 
    nombre nulo) o se hace una operación indebida como restar de un inventario vacío.
    """
    def __init__(self, message: str = "Datos de producto inválidos"):
        self.message = message
        super().__init__(self.message)

class ChatServiceError(Exception):
    """
    Se lanza cuando hay un requerimiento de chat inatendible por falla
    en la coordinación o con el servicio de IA.
    """
    def __init__(self, message: str = "Error en el servicio de chat"):
        self.message = message
        super().__init__(self.message)
