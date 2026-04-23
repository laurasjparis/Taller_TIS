"""
Servicio de productos: Coordina validación y acceso a base de datos.
"""
from typing import List, Optional
from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.domain.exceptions import ProductNotFoundError, InvalidProductDataError
from .dtos import ProductDTO

class ProductService:
    """
    Servicio de aplicación para gestionar todas las operaciones de los productos.
    
    Este servicio actúa de intermediario entre los DTOs provenientes de un frontend (API)
    y el Repositorio de Infraestructura que accede directamente al ORM subyacente.
    Además, eleva fallos bajo un esquema estricto (ProductNotFoundError, etc.).
    
    Attributes:
        repo (IProductRepository): Interfaz inyectada que cumple con los métodos SQL persistibles.
    """
    def __init__(self, repo: IProductRepository):
        """
        Inicializador del servicio de aplicación de productos.
        
        Args:
            repo (IProductRepository): Instancia que cumpla con abstracciones del DB para IProductRepository.
        """
        self.repo = repo

    def get_all_products(self) -> List[ProductDTO]:
        """
        Devuelve el catálogo de todos los productos en formato plano (DTO).
        
        Returns:
            List[ProductDTO]: Listado de productos actuales con o sin stock.
        """
        products = self.repo.get_all()
        return [ProductDTO.model_validate(p) for p in products]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """
        Trae al producto mediante su identificador único.
        
        Args:
            product_id (int): El ID numérico entero de la base de datos.
            
        Returns:
            ProductDTO: Estructura del zapato solitario.
            
        Raises:
            ProductNotFoundError: Expuesto a la API HTTP si no se cuenta con coincidencias.
        """
        product = self.repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)
        return ProductDTO.model_validate(product)

    def search_products(self, brand: Optional[str] = None, category: Optional[str] = None) -> List[ProductDTO]:
        """
        Buscador básico para agrupar elementos que son de la misma rama de marca o categoría.
        
        Args:
            brand (Optional[str]): Consulta textual por marcas.
            category (Optional[str]): Consulta textual por categorías.
            
        Returns:
            List[ProductDTO]: Grupo filtrado y serializado.
        """
        if brand:
            return [ProductDTO.model_validate(p) for p in self.repo.get_by_brand(brand)]
        if category:
            return [ProductDTO.model_validate(p) for p in self.repo.get_by_category(category)]
        return self.get_all_products()

    def create_product(self, dto: ProductDTO) -> ProductDTO:
        """
        Agrega persistente a un nuevo zapato proveniente de RequestBody (DTO).
        
        Args:
            dto (ProductDTO): Valuación validada.
            
        Returns:
            ProductDTO: Producto ya configurado (incluye el Autoincrement de Id).
            
        Raises:
            InvalidProductDataError: Captura si algo infringe reglas subyacentes.
        """
        try:
            entity = Product(
                id=None,
                name=dto.name,
                brand=dto.brand,
                category=dto.category,
                size=dto.size,
                color=dto.color,
                price=dto.price,
                stock=dto.stock,
                description=dto.description
            )
            saved = self.repo.save(entity)
            return ProductDTO.model_validate(saved)
        except ValueError as e:
            raise InvalidProductDataError(str(e))

    def update_product(self, product_id: int, dto: ProductDTO) -> ProductDTO:
        """
        Fuerza todos los campos del RequestBody sobreescribiendo a un Producto pre-registrado.
        
        Args:
            product_id (int): Elemento en SQL para alterar.
            dto (ProductDTO): Colección nueva.
            
        Returns:
            ProductDTO: Producto exitosamente reescrito.
            
        Raises:
            ProductNotFoundError: Prevé re-escrituras sobre vacíos.
            InvalidProductDataError: Ante reglas infringidas de negocio.
        """
        existing = self.repo.get_by_id(product_id)
        if not existing:
            raise ProductNotFoundError(product_id)
        try:
            entity = Product(
                id=product_id,
                name=dto.name,
                brand=dto.brand,
                category=dto.category,
                size=dto.size,
                color=dto.color,
                price=dto.price,
                stock=dto.stock,
                description=dto.description
            )
            saved = self.repo.save(entity)
            return ProductDTO.model_validate(saved)
        except ValueError as e:
            raise InvalidProductDataError(str(e))

    def delete_product(self, product_id: int) -> bool:
        """
        Elimina destructiva e integralmente un producto.
        
        Args:
            product_id (int): Elemento afectado.
            
        Returns:
            bool: Success flag.
        """
        if not self.repo.get_by_id(product_id):
            raise ProductNotFoundError(product_id)
        return self.repo.delete(product_id)

    def get_available_products(self) -> List[ProductDTO]:
        """
        Recupera del mercado aquellos productos con verdadero límite operacional
        (Stock mayor a cero únicamente).
        
        Returns:
            List[ProductDTO]: Solamente el stock vendible.
        """
        all_prods = self.repo.get_all()
        return [ProductDTO.model_validate(p) for p in all_prods if p.is_available()]
