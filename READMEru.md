# DataSheet Parser

Инструмент для оцифровки технической документации (даташитов) с помощью мультимодальных моделей ИИ.

## Описание

Данный проект предназначен для автоматической оцифровки PDF документов с технической документацией. Процесс включает:
1. Разделение PDF файла на отдельные страницы-изображения
2. Последовательную обработку страниц с помощью мультимодальной модели ИИ через OpenRouter API
3. Сохранение результатов в структурированном Markdown формате 

## Установка

```bash
pip install -r requirements.txt
```

Для работы с PDF требуется установить poppler:
- Windows: https://github.com/oschwartz10612/poppler-windows/releases/
- Linux: `apt-get install poppler-utils`
- macOS: `brew install poppler`

## Использование

1. Создайте файл `.env` с вашим API ключом OpenRouter:
```
OPENROUTER_API_KEY=your_api_key_here
```

2. Запустите скрипт:
```bash
python datasheet_parser.py path_to_pdf_file.pdf
```

## Структура проекта

- `datasheet_parser.py` - основной скрипт для обработки PDF документов
- `pdf_utils.py` - утилиты для работы с PDF файлами
- `api_client.py` - клиент для взаимодействия с OpenRouter API
- `markdown_generator.py` - утилиты для создания Markdown файлов