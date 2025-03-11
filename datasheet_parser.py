#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import logging
import tempfile
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
import time

from pdf_utils import extract_images_from_pdf, get_pdf_metadata, resize_image_if_needed
from api_client import OpenRouterClient
from markdown_generator import create_markdown_file, merge_markdown_files, clean_markdown, add_table_of_contents


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("datasheet_parser.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DataSheetParser")


def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description="Парсер даташитов с использованием мультимодальных моделей ИИ")
    parser.add_argument("pdf_path", help="Путь к PDF файлу даташита")
    parser.add_argument("--output", "-o", help="Директория для сохранения результатов", default="output")
    parser.add_argument("--model", "-m", help="Модель для использования", default=None)
    parser.add_argument("--context-window", "-c", type=int, help="Количество предыдущих страниц для контекста", default=2)
    parser.add_argument("--temp-dir", "-t", help="Временная директория для изображений", default=None)
    parser.add_argument("--max-tokens", type=int, help="Максимальное количество токенов для ответа модели", default=4096)
    parser.add_argument("--poppler-path", "-p", help="Путь к исполняемым файлам Poppler (например, C:/Poppler/Library/bin)", default=None)
    parser.add_argument("--debug", action="store_true", help="Включить отладочный режим")
    
    return parser.parse_args()


def process_datasheet(pdf_path, output_dir, model=None, context_window=2, temp_dir=None, poppler_path=None, debug=False):
    """
    Обрабатывает даташит целиком.
    
    Args:
        pdf_path: Путь к PDF файлу
        output_dir: Директория для сохранения результатов
        model: Идентификатор модели для использования
        context_window: Количество предыдущих страниц для контекста
        temp_dir: Директория для временных файлов
        poppler_path: Путь к исполняемым файлам Poppler
        debug: Флаг отладочного режима
    
    Returns:
        Путь к сгенерированному Markdown файлу
    """
    # Создаем директорию для результатов, если она не существует
    os.makedirs(output_dir, exist_ok=True)
    
    # Получаем метаданные PDF
    logger.info(f"Извлечение метаданных из {pdf_path}")
    metadata = get_pdf_metadata(pdf_path)
    logger.info(f"Заголовок: {metadata.get('title', 'Unknown')}, страниц: {metadata.get('page_count', 0)}")
    
    # Определяем имя выходного файла на основе имени PDF
    output_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Извлекаем изображения страниц
    logger.info(f"Извлечение страниц из PDF как изображения")
    image_paths = extract_images_from_pdf(pdf_path, temp_dir, poppler_path)
    logger.info(f"Извлечено {len(image_paths)} страниц")
    
    # Инициализируем клиент API
    client = OpenRouterClient(model=model)
    
    # Обрабатываем каждую страницу
    page_markdown_files = []
    context = ""
    context_pages = []
    
    logger.info(f"Начинаем обработку страниц")
    for i, image_path in enumerate(tqdm(image_paths)):
        page_num = i + 1
        logger.info(f"Обработка страницы {page_num}/{len(image_paths)}")
        
        # Проверяем и при необходимости изменяем размер изображения
        img_path = resize_image_if_needed(image_path)
        
        # Создаем инструкции для модели
        instructions = (
            f"Это страница {page_num} из {len(image_paths)} даташита. "
            f"Извлеки всю техническую информацию и отформатируй её в Markdown. "
            f"Используй заголовки, таблицы, списки и другие элементы Markdown для наилучшего представления."
        )
        
        # Обрабатываем страницу
        try:
            logger.info(f"Отправляем изображение страницы {page_num} в API")
            markdown_content = client.process_page(
                image_path=img_path,
                previous_context=context,
                instructions=instructions
            )
            
            # Очищаем Markdown
            clean_content = clean_markdown(markdown_content)
            
            # Сохраняем результат для отдельной страницы
            page_md_file = os.path.join(output_dir, f"{output_name}_page_{page_num:03d}.md")
            create_markdown_file(clean_content, page_md_file)
            page_markdown_files.append(page_md_file)
            
            # Обновляем контекст
            context_pages.append(clean_content)
            if len(context_pages) > context_window:
                context_pages.pop(0)
            context = "\n\n".join(context_pages)
            
            # В отладочном режиме: пауза между запросами для удобства отладки
            if debug and i < len(image_paths) - 1:
                logger.debug(f"Пауза 3 секунды перед обработкой следующей страницы")
                time.sleep(3)
                
        except Exception as e:
            logger.error(f"Ошибка при обработке страницы {page_num}: {str(e)}")
            # Продолжаем с следующей страницей
    
    # Объединяем все страницы в один документ
    logger.info(f"Объединение {len(page_markdown_files)} страниц в один документ")
    output_md_file = os.path.join(output_dir, f"{output_name}_full.md")
    merge_markdown_files(page_markdown_files, output_md_file, metadata)
    
    # Добавляем оглавление
    with open(output_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content_with_toc = add_table_of_contents(content)
    
    with open(output_md_file, 'w', encoding='utf-8') as f:
        f.write(content_with_toc)
    
    logger.info(f"Обработка завершена. Результат сохранен в {output_md_file}")
    return output_md_file


def main():
    """Основная функция"""
    load_dotenv()
    args = parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Проверяем наличие PDF файла
    if not os.path.exists(args.pdf_path):
        logger.error(f"PDF файл не найден: {args.pdf_path}")
        return 1
    
    # Обрабатываем даташит
    try:
        output_file = process_datasheet(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            model=args.model,
            context_window=args.context_window,
            temp_dir=args.temp_dir,
            poppler_path=args.poppler_path,
            debug=args.debug
        )
        logger.info(f"Успешно создан файл: {output_file}")
        return 0
    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        if args.debug:
            logger.exception("Детали ошибки:")
        return 1


if __name__ == "__main__":
    exit(main()) 