import os
from pathlib import Path
from typing import List, Dict, Any
import re


def create_markdown_file(content: str, output_path: str) -> None:
    """
    Создает Markdown файл с указанным содержимым.
    
    Args:
        content: Содержимое для записи в файл
        output_path: Путь для сохранения файла
    """
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Записываем содержимое в файл
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def merge_markdown_files(file_paths: List[str], output_path: str, metadata: Dict[str, Any] = None) -> None:
    """
    Объединяет несколько Markdown файлов в один с добавлением метаданных.
    
    Args:
        file_paths: Список путей к файлам для объединения
        output_path: Путь для сохранения объединенного файла
        metadata: Метаданные документа для включения в заголовок
    """
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Создаем заголовок с метаданными
    header = ""
    if metadata:
        header = "# " + str(metadata.get("title", "Документация")) + "\n\n"
        if metadata.get("author"):
            header += f"**Автор**: {metadata['author']}\n\n"
        if metadata.get("subject"):
            header += f"**Описание**: {metadata['subject']}\n\n"
        header += "---\n\n"
    
    # Объединяем содержимое файлов
    content = []
    for file_path in file_paths:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read().strip()
                content.append(file_content)
    
    # Записываем результат
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header + "\n\n".join(content))


def clean_markdown(content: str) -> str:
    """
    Очищает и форматирует Markdown содержимое.
    
    Args:
        content: Исходное содержимое Markdown
        
    Returns:
        Очищенное содержимое
    """
    # Удаляем избыточные пустые строки
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Удаляем номера страниц и колонтитулы (простая эвристика)
    content = re.sub(r'\n\s*Page \d+\s*\n', '\n', content, flags=re.IGNORECASE)
    content = re.sub(r'\n\s*\d+\s*\n', '\n', content)
    
    # Другие очистки по необходимости
    
    return content


def add_table_of_contents(content: str) -> str:
    """
    Добавляет оглавление на основе заголовков в Markdown.
    
    Args:
        content: Исходное содержимое Markdown
        
    Returns:
        Содержимое с добавленным оглавлением
    """
    # Находим все заголовки
    headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
    
    if not headers:
        return content
    
    # Создаем оглавление
    toc = "## Содержание\n\n"
    
    for header_level, header_text in headers:
        # Пропускаем оглавление, если оно уже есть
        if header_text.lower() == "содержание":
            continue
            
        # Получаем уровень заголовка
        level = len(header_level) - 1  # -1 потому что # - это уровень 1, но отступ будет 0
        
        # Создаем идентификатор для якоря
        anchor = header_text.lower().replace(' ', '-')
        anchor = re.sub(r'[^\w\-]', '', anchor)
        
        # Добавляем элемент оглавления
        toc += f"{' ' * (level * 2)}- [{header_text}](#{anchor})\n"
    
    # Вставляем оглавление после первого заголовка
    first_header_end = re.search(r'^#.+$', content, re.MULTILINE).end()
    result = content[:first_header_end] + "\n\n" + toc + "\n" + content[first_header_end:]
    
    return result 