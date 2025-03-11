# DataSheet Parser

Инструмент для оцифровки технической документации (даташитов) с помощью мультимодальных моделей ИИ.

## Описание

Данный проект предназначен для автоматической оцифровки PDF документов с технической документацией. Процесс включает:
1. Разделение PDF файла на отдельные страницы-изображения
2. Последовательную обработку страниц с помощью мультимодальной модели ИИ через OpenAI API
3. Сохранение результатов в структурированном Markdown формате 

## Установка

```bash
pip install -r requirements.txt
```

### Установка Poppler (обязательно)

Для работы с PDF требуется установить Poppler:

#### Windows:
1. Скачайте последнюю версию с [GitHub](https://github.com/oschwartz10612/poppler-windows/releases/)
2. Распакуйте архив в удобную директорию (например, `C:\Poppler`)
3. Добавьте путь к папке bin в переменную PATH:
   - Временно в текущем сеансе PowerShell: `$env:PATH += ";C:\Poppler\Library\bin"`
   - Или постоянно через "Параметры системы" → "Переменные среды"

#### Linux:
```bash
apt-get install poppler-utils
```

#### macOS:
```bash
brew install poppler
```

## Использование

1. Создайте файл `.env` с вашим API ключом OpenAI:
```
OPENAI_API_KEY=your_api_key_here
```

2. Запустите скрипт:
```bash
# Базовое использование
python datasheet_parser.py path_to_pdf_file.pdf

# С указанием пути к Poppler
python datasheet_parser.py path_to_pdf_file.pdf --poppler-path "C:\Poppler\Library\bin"

# С указанием определенной модели
python datasheet_parser.py path_to_pdf_file.pdf --model "gpt-4o"
```

### Доступные модели

По умолчанию используется модель `gpt-4o`. Также можно использовать:
- `gpt-4-vision-preview` - предыдущая версия мультимодальной модели
- Другие модели OpenAI с поддержкой анализа изображений

### Дополнительные опции

```
--output (-o) - Директория для сохранения результатов (по умолчанию: "output")
--model (-m) - Идентификатор модели для использования
--context-window (-c) - Количество предыдущих страниц для контекста (по умолчанию: 2)
--poppler-path (-p) - Путь к исполняемым файлам Poppler
--debug - Включить режим отладки
```

## Структура проекта

- `datasheet_parser.py` - основной скрипт для обработки PDF документов
- `pdf_utils.py` - утилиты для работы с PDF файлами
- `api_client.py` - клиент для взаимодействия с OpenAI API
- `markdown_generator.py` - утилиты для создания Markdown файлов