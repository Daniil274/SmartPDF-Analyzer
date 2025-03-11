import os
import tempfile
from pathlib import Path
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from typing import List, Tuple
from PIL import Image


def extract_images_from_pdf(pdf_path: str, output_dir: str = None, poppler_path: str = None) -> List[str]:
    """
    Извлекает изображения страниц из PDF файла и сохраняет их во временную директорию.
    
    Args:
        pdf_path: Путь к PDF файлу
        output_dir: Директория для сохранения изображений (если не указана, создается временная)
        poppler_path: Путь к исполняемым файлам Poppler (например, "C:/Poppler/Library/bin")
        
    Returns:
        Список путей к сохраненным изображениям
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="datasheet_parser_")
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    # Проверяем, существует ли путь к Poppler
    if poppler_path is None:
        # Попытка найти poppler в стандартных местах
        possible_paths = [
            "C:/Program Files/poppler/bin",
            "C:/Program Files (x86)/poppler/bin",
            "C:/Poppler/bin",
            "C:/Poppler/Library/bin",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "poppler/bin")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                poppler_path = path
                break
    
    # Извлечение страниц как изображений
    try:
        images = convert_from_path(pdf_path, poppler_path=poppler_path)
    except Exception as e:
        if "poppler" in str(e).lower():
            raise Exception(
                "Не удалось найти Poppler. Пожалуйста, установите Poppler с "
                "https://github.com/oschwartz10612/poppler-windows/releases/ "
                "и укажите путь к нему с помощью аргумента --poppler-path."
            )
        raise e
    
    # Сохранение изображений
    image_paths = []
    for i, image in enumerate(images):
        img_path = os.path.join(output_dir, f"page_{i+1:03d}.png")
        image.save(img_path, "PNG")
        image_paths.append(img_path)
    
    return image_paths


def get_pdf_metadata(pdf_path: str) -> dict:
    """
    Получает метаданные PDF файла.
    
    Args:
        pdf_path: Путь к PDF файлу
        
    Returns:
        Словарь с метаданными
    """
    reader = PdfReader(pdf_path)
    metadata = reader.metadata
    
    info = {
        "title": metadata.get("/Title", "Unknown"),
        "author": metadata.get("/Author", "Unknown"),
        "subject": metadata.get("/Subject", ""),
        "creator": metadata.get("/Creator", ""),
        "producer": metadata.get("/Producer", ""),
        "page_count": len(reader.pages)
    }
    
    return info


def resize_image_if_needed(image_path: str, max_size: int = 5 * 1024 * 1024) -> str:
    """
    Изменяет размер изображения, если оно превышает указанный размер.
    
    Args:
        image_path: Путь к изображению
        max_size: Максимальный размер в байтах (по умолчанию 5MB)
        
    Returns:
        Путь к изображению (оригинальному или измененному)
    """
    file_size = os.path.getsize(image_path)
    
    if file_size <= max_size:
        return image_path
    
    # Открываем и изменяем размер изображения
    with Image.open(image_path) as img:
        # Определяем коэффициент масштабирования
        scale_factor = (max_size / file_size) ** 0.5
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)
        
        # Изменяем размер и сохраняем
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        resized_img.save(image_path, optimize=True)
    
    return image_path 