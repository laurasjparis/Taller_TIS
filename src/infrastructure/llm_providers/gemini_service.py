import os
import google.generativeai as genai
from typing import List
from src.domain.entities import Product

class GeminiService:
    """
    Proveedor de infraestructura IA que asocia el SDK oficial de Google Generative AI
    a un objeto instanciable para proveer de razonamiento verbal al chat.
    """
    def __init__(self):
        """
        Inicializa la conexión recuperando la GEMINI_API_KEY del environment.
        Si la clave se ausenta, configura un flag de mockeo automatizado.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            import warnings
            warnings.warn("GEMINI_API_KEY is not set.")
            self.mock = True
        else:
            self.mock = False
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def format_products_info(self, products: List[Product]) -> str:
        """
        Formatea productos legibles para el prompt estructurado del Large Language Model (LLM).
        
        Args:
            products (List[Product]): Catalogo de disponibilidad total filtrada con stock > 0.
            
        Returns:
            str: Una macro-cadena listando la data clave requerida para la compra/asistencia,
                incluyendo precios y el inventario disponible.
        """
        lines = []
        for p in products:
            lines.append(f"- {p.name} | {p.brand} | ${p.price} | Stock: {p.stock} | Tallas: {p.size} | Color: {p.color} | Info: {p.description}")
        return "\n".join(lines)

    async def generate_response(self, user_message: str, products: List[Product], context_prompt: str) -> str:
        """
        Llama asincrónicamente a Gemini usando el contexto vivo de la memoria, los productos que sí se pueden 
        vender (stock > 0), y procesa con un RolePrompt sistémico la sugerencia adecuada para enganchar
        como eCommerce exitoso.
        
        Args:
            user_message (str): La solicitud nueva y cruda que digita el humano.
            products (List[Product]): Arreglo inteligente de productos listos para ofertar.
            context_prompt (str): Memoria relacional histórica.
            
        Returns:
            str: Bloque textual elaborado devuelto con éxito por Gemini.
        """
        if self.mock:
            return "Respuesta simulada porque GEMINI_API_KEY no está configurada."
            
        products_info = self.format_products_info(products)
        
        system_instructions = (
            "Eres un asistente virtual experto en ventas de zapatos para un e-commerce.\n"
            "Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.\n\n"
            "PRODUCTOS DISPONIBLES:\n"
            f"{products_info}\n\n"
            "INSTRUCCIONES:\n"
            "- Sé amigable y profesional\n"
            "- Usa el contexto de la conversación anterior\n"
            "- Recomienda productos específicos cuando sea apropiado\n"
            "- Menciona precios, tallas y disponibilidad\n"
            "- Si no tienes información, sé honesto\n\n"
            "HISTORIAL DE CONVERSACIÓN:\n"
            f"{context_prompt}\n\n"
        )
        
        prompt = system_instructions + f"Usuario: {user_message}\nAsistente:"
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Hubo un error de conexión con la IA: {str(e)}"
