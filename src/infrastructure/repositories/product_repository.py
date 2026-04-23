from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel

class SQLProductRepository(IProductRepository):
    """
    Repositorio sólido que encapsula la base de datos para la entidad Product.
    Implementación concreta de IProductRepository. Base acoplada a SQLAlchemy.
    """
    def __init__(self, db: Session):
        """
        Asigna la sesión de DB a la instancia en cada llamado desde la API.
        
        Args:
            db (Session): Dependencia inyectada.
        """
        self.db = db

    def _model_to_entity(self, model: ProductModel) -> Product:
        """Traduce de un Registro ORM SQL a un Objeto Inteligente de Dominio (Entity)."""
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """Convierte una entidad in-memory en un objeto salvable ORM DB."""
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description
        )

    def get_all(self) -> List[Product]:
        """
        Trae todos los ProductModels y los retorna como List[Product] puros.
        """
        models = self.db.query(ProductModel).all()
        return [self._model_to_entity(m) for m in models]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Consigue un único Product según el id, O retorna Null si no ubica nada."""
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return self._model_to_entity(model) if model else None

    def get_by_brand(self, brand: str) -> List[Product]:
        """Filtra y devuelve todos los modelos mapeados a la entidad si la marca coincide."""
        models = self.db.query(ProductModel).filter(ProductModel.brand == brand).all()
        return [self._model_to_entity(m) for m in models]

    def get_by_category(self, category: str) -> List[Product]:
        """Devuelve iterables de Product para dicha categoría."""
        models = self.db.query(ProductModel).filter(ProductModel.category == category).all()
        return [self._model_to_entity(m) for m in models]

    def save(self, product: Product) -> Product:
        """
        Almacena Product o hace UP-date.
        
        Args:
            product (Product): Product limpio a escribir.
            
        Returns:
            Product: Registro sincronizado (frecuentemente posee Id nuevo).
        """
        if product.id:
            model = self.db.query(ProductModel).filter(ProductModel.id == product.id).first()
            if model:
                model.name = product.name
                model.brand = product.brand
                model.category = product.category
                model.size = product.size
                model.color = product.color
                model.price = product.price
                model.stock = product.stock
                model.description = product.description
                self.db.commit()
                self.db.refresh(model)
                return self._model_to_entity(model)
                
        model = self._entity_to_model(product)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def delete(self, product_id: int) -> bool:
        """
        Elimina limpiamente la fila referida y lanza Commit.
        
        Args:
            product_id (int): Entero objetivo en SQL.
            
        Returns:
            bool: Success status.
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False
