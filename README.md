# DataSheet Parser

A tool for digitizing technical documentation (datasheets) using multimodal AI models.

## Description

This project is designed for automatic digitization of PDF documents containing technical documentation. The process includes:
1. Splitting the PDF file into individual page images
2. Sequential processing of pages using a multimodal AI model via OpenAI API
3. Saving the results in a structured Markdown format

## Installation

```bash
pip install -r requirements.txt
```

### Installing Poppler (required)

To work with PDFs, you need to install Poppler:

#### Windows:
1. Download the latest version from [GitHub](https://github.com/oschwartz10612/poppler-windows/releases/)
2. Extract the archive to a convenient directory (e.g., `C:\Poppler`)
3. Add the bin folder path to the PATH environment variable:
   - Temporarily in the current PowerShell session: `$env:PATH += ";C:\Poppler\Library\bin"`
   - Or permanently through "System Settings" → "Environment Variables"

#### Linux:
```bash
apt-get install poppler-utils
```

#### macOS:
```bash
brew install poppler
```

## Usage

1. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

2. Run the script:
```bash
# Basic usage
python datasheet_parser.py path_to_pdf_file.pdf

# Specifying Poppler path
python datasheet_parser.py path_to_pdf_file.pdf --poppler-path "C:\Poppler\Library\bin"

# Using a specific model
python datasheet_parser.py path_to_pdf_file.pdf --model "gpt-4o"
```

### Available Models

The default model is `gpt-4o`. You can also use:
- `gpt-4-vision-preview` - previous version of the multimodal model
- Other OpenAI models with image analysis support

### Additional Options

```
--output (-o) - Output directory for results (default: "output")
--model (-m) - Model identifier to use
--context-window (-c) - Number of previous pages to include as context (default: 2)
--poppler-path (-p) - Path to Poppler executable files
--debug - Enable debug mode
```

## Project Structure

- `datasheet_parser.py` - main script for processing PDF documents
- `pdf_utils.py` - utilities for working with PDF files
- `api_client.py` - client for interacting with OpenAI API
- `markdown_generator.py` - utilities for creating Markdown files

*Note: For a Russian version of this README, see [READMEru.md](READMEru.md)* 