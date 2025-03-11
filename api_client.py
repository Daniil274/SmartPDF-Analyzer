import os
import base64
import requests
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any


# Загрузка переменных окружения
load_dotenv()

# API ключ из переменных окружения
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# URL для API запросов
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Модель с мультимодальной поддержкой
DEFAULT_MODEL = "anthropic/claude-3-opus-20240229"  # Можно выбрать другую модель, поддерживающую обработку изображений


class OpenRouterClient:
    """Клиент для взаимодействия с OpenRouter API"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Инициализирует клиент OpenRouter.
        
        Args:
            api_key: API ключ для OpenRouter (если не указан, берется из переменных окружения)
            model: Идентификатор модели (если не указан, используется значение по умолчанию)
        """
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("API ключ OpenRouter не указан. Укажите его в .env файле или при создании клиента.")
        
        self.model = model or DEFAULT_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://datasheetparser.local",  # Укажите фактический домен вашего приложения
        }
    
    def encode_image(self, image_path: str) -> str:
        """
        Кодирует изображение в base64.
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            Строка base64
        """
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    def process_page(self, 
                    image_path: str, 
                    previous_context: str = "", 
                    instructions: str = "Извлеки всю текстовую информацию со страницы даташита и отформатируй её в Markdown") -> str:
        """
        Обрабатывает страницу даташита через API.
        
        Args:
            image_path: Путь к изображению страницы
            previous_context: Контекст из предыдущих страниц
            instructions: Инструкции для модели
            
        Returns:
            Извлеченный и отформатированный текст
        """
        # Кодируем изображение
        base64_image = self.encode_image(image_path)
        
        # Формируем сообщения для модели
        messages = []
        
        # Добавляем системную инструкцию
        system_message = (
            "Ты - специалист по извлечению и структурированию информации из технической документации. "
            "Твоя задача - извлечь всю полезную информацию со страниц даташита и форматировать её в Markdown. "
            "Используй таблицы, списки, заголовки и другие элементы Markdown для наилучшего представления. "
            "Оставь только существенную техническую информацию, игнорируя номера страниц, колонтитулы, "
            "маркеры и другие элементы форматирования, не относящиеся к содержанию."
        )
        
        messages.append({"role": "system", "content": system_message})
        
        # Если есть предыдущий контекст, добавляем его
        if previous_context:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Вот контекст из предыдущих страниц даташита:"},
                    {"type": "text", "text": previous_context}
                ]
            })
        
        # Добавляем текущее изображение с инструкциями
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": instructions},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]
        })
        
        # Формируем запрос
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 0.1,  # Низкая температура для более детерминированных ответов
        }
        
        # Отправляем запрос
        response = requests.post(OPENROUTER_API_URL, headers=self.headers, json=payload)
        
        # Проверяем ответ
        if response.status_code != 200:
            raise Exception(f"Ошибка API: {response.status_code}, {response.text}")
        
        # Извлекаем ответ
        result = response.json()
        return result["choices"][0]["message"]["content"] 