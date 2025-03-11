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

## Usage

1. Create a `.env` file with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

2. Run the script:
```bash
python datasheet_parser.py path_to_pdf_file.pdf
```

## Project Structure

- `datasheet_parser.py` - main script for processing PDF documents
- `pdf_utils.py` - utilities for working with PDF files
- `api_client.py` - client for interacting with the OpenRouter API
- `markdown_generator.py` - utilities for creating Markdown files 