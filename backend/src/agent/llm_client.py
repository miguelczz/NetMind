from openai import OpenAI
from ..settings import settings
from typing import Iterator

class LLMClient:
    def __init__(self):
        # Usar settings en lugar de cargar manualmente
        if not settings.openai_api_key:
            raise ValueError(
                "No se encontró la variable de entorno OPENAI_API_KEY. "
                "Asegúrate de tener un archivo .env con la línea:\n"
                "OPENAI_API_KEY=tu_api_key_aqui"
            )

        # Inicializar cliente de OpenAI
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model

    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Genera texto usando OpenAI Chat Completions.
        
        Args:
            prompt: El prompt a procesar
            max_tokens: Número máximo de tokens a generar (por defecto 1000)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Error al generar respuesta con LLM: {str(e)}")
    
    def generate_stream(self, prompt: str, max_tokens: int = 1000) -> Iterator[str]:
        """
        Genera texto usando OpenAI Chat Completions con streaming.
        
        Args:
            prompt: El prompt a procesar
            max_tokens: Número máximo de tokens a generar (por defecto 1000)
            
        Yields:
            Tokens individuales a medida que se generan
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                stream=True,  # Habilitar streaming
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise RuntimeError(f"Error al generar respuesta con LLM (streaming): {str(e)}")
    
    def complete(self, prompt: str) -> str:
        """
        Alias para generate() para compatibilidad con código existente.
        """
        return self.generate(prompt)

