# DataSheet Parser

A tool for digitizing technical documentation (datasheets) using multimodal AI models.

## Description

This project is designed for the automatic digitization of PDF documents containing technical documentation. The process includes:
1. Splitting the PDF file into individual page images.
2. Sequential processing of pages using a multimodal AI model via the OpenRouter API.
3. Saving the results in a structured Markdown format.

## Installation

```bash
pip install -r requirements.txt
```

To work with PDFs, you need to install poppler:
- Windows: https://github.com/oschwartz10612/poppler-windows/releases/
- Linux: `apt-get install poppler-utils`
- macOS: `brew install poppler`

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

## Usage

1. Create a `.env` file with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

2. Run the script:
```bash
# Базовое использование
python datasheet_parser.py path_to_pdf_file.pdf

# С указанием пути к Poppler
python datasheet_parser.py path_to_pdf_file.pdf --poppler-path "C:\Poppler\Library\bin"
```

### Дополнительные опции

```
--output (-o) - Директория для сохранения результатов (по умолчанию: "output")
--model (-m) - Идентификатор модели для использования
--context-window (-c) - Количество предыдущих страниц для контекста (по умолчанию: 2)
--poppler-path (-p) - Путь к исполняемым файлам Poppler
--debug - Включить режим отладки
```

## Project Structure

- `datasheet_parser.py` - main script for processing PDF documents
- `pdf_utils.py` - utilities for working with PDF files
- `api_client.py` - client for interacting with the OpenRouter API
- `markdown_generator.py` - utilities for creating Markdown files 