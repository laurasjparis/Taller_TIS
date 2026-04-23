from .database import SessionLocal
from .models import ProductModel

def load_initial_data() -> None:
    """
    Función de siembra (Seeder) que carga los 10 productos base si el recuento es cero.
    Inyecta marcas reales (Nike, Adidas, Puma) para que la IA disponga 
    rápidamente de un catálogo sin peticiones pesadas manualmente.
    
    Returns:
        None
    """
    db = SessionLocal()
    try:
        if db.query(ProductModel).count() == 0:
            productos = [
                ProductModel(name="Air Max 270", brand="Nike", category="Running", size="42", color="Negro", price=150.0, stock=20, description="Tenis de correr con gran amortiguación"),
                ProductModel(name="Ultraboost 22", brand="Adidas", category="Running", size="41", color="Blanco", price=180.0, stock=15, description="Ligereza y alto rendimiento en cada paso"),
                ProductModel(name="Puma Suede Classic", brand="Puma", category="Casual", size="40", color="Rojo", price=90.0, stock=30, description="Diseño clásico urbano"),
                ProductModel(name="Vans Old Skool", brand="Vans", category="Skate", size="43", color="Blanco/Negro", price=75.0, stock=50, description="El icono del skate con la banda lateral"),
                ProductModel(name="Converse Chuck Taylor All Star", brand="Converse", category="Casual", size="39", color="Azul Marino", price=60.0, stock=40, description="Las clásicas zapatillas de lona"),
                ProductModel(name="New Balance 574", brand="New Balance", category="Lifestyle", size="44", color="Gris", price=110.0, stock=25, description="Comodidad premium para el día a día"),
                ProductModel(name="Asics Gel-Kayano", brand="Asics", category="Running", size="42", color="Azul", price=160.0, stock=10, description="Estabilidad y soporte para largas distancias"),
                ProductModel(name="Reebok Club C 85", brand="Reebok", category="Casual", size="41", color="Blanco", price=85.0, stock=35, description="Estilo vintage y minimalista"),
                ProductModel(name="Timberland Premium 6-Inch", brand="Timberland", category="Boots", size="45", color="Ocre", price=200.0, stock=12, description="Botas impermeables de cuero resistente"),
                ProductModel(name="Dr. Martens 1460", brand="Dr. Martens", category="Formal/Casual", size="40", color="Negro", price=170.0, stock=8, description="Botas clásicas de 8 ojales")
            ]
            db.add_all(productos)
            db.commit()
            print("Datos iniciales de productos cargados a la base de datos.")
    except Exception as e:
        print(f"Error cargando los datos iniciales: {e}")
    finally:
        db.close()
