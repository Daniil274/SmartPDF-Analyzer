# SmartPDF Analyzer

A tool for extracting text from PDF documents using multimodal AI models.

## Description

This project is designed for extracting text from PDF documents. The process includes:
1. Splitting the PDF file into individual page images
2. Processing each page independently using a multimodal AI model via OpenAI API
3. Optional translation of the content into a specified target language
4. Saving the results in a structured Markdown format

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

1. Create a `.env` file with your API keys and server configuration:
```
# OpenAI API configuration
OPENAI_API_KEY=your_api_key_here

# OpenRouter configuration (optional)
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```

2. Run the script:
```bash
# Basic usage - extract text in original language
python datasheet_parser.py path_to_pdf_file.pdf

# Extract and translate text
python datasheet_parser.py path_to_pdf_file.pdf --translate --target-language "Russian"

# Advanced usage with multiple options
python datasheet_parser.py path_to_pdf_file.pdf \
    --translate --target-language "German" \
    --model "gpt-4o" \
    --poppler-path "C:\Poppler\Library\bin" \
    --output "translated_docs"
```

### Available Models

The default model is `gpt-4o`. You can also use:
- `gpt-4-vision-preview` - previous version of the multimodal model
- Other OpenAI models with image analysis support

### Alternative Models via OpenRouter

For cost-effective processing, you can use alternative models through [OpenRouter](https://openrouter.ai/):
- `qwen/qwen2.5-vl-72b-instruct` - **recommended** - powerful multimodal model with excellent text extraction capabilities
- `amazon/nova-lite-v1` - efficient and cost-effective model for document analysis
- `google/gemini-2.0-flash-001` - fast and accurate alternative

To use these models:
1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Get your API key
3. Set the environment variable:
```
OPENAI_API_KEY=your_api_key_here
```
4. Use the model with the `--model` flag:
```bash
python datasheet_parser.py document.pdf --model "qwen/qwen2.5-vl-72b-instruct"
```

### Additional Options

```
--output (-o) - Output directory for results (default: "output")
--model (-m) - Model identifier to use
--poppler-path (-p) - Path to Poppler executable files
--debug - Enable debug mode
--translate (-tr) - Enable translation of the extracted text
--target-language (-tl) - Target language for translation
--start-page (-sp) - First page to process (1-based index)
--end-page (-ep) - Last page to process (1-based index)
```

### Key Features

#### Verbatim Text Extraction
- The tool extracts text exactly as it appears in the document
- No interpretation or summarization of content
- Diagrams and images are ignored - only visible text is extracted
- Original text structure and format is preserved as closely as possible

#### Page Range Selection

The parser allows you to process only specific pages from a PDF document:

- **Selective Processing**: Specify a range of pages to extract and process
- **Flexible Range**: Use either start page, end page, or both to define the range
- **Output Naming**: Generated files include the page range in their names (e.g., `document_p5-10_full.md`)
- **Resource Efficiency**: Reduces processing time and API costs when working with large documents

Example usage with page range selection:
```bash
# Process only pages 5-10
python datasheet_parser.py document.pdf --start-page 5 --end-page 10

# Process from page 3 to the end
python datasheet_parser.py document.pdf --start-page 3

# Process from the beginning to page 15
python datasheet_parser.py document.pdf --end-page 15

# Combine with translation
python datasheet_parser.py document.pdf --start-page 5 --end-page 10 --translate --target-language "French"
```

#### Translation Feature

The parser includes a powerful translation capability that can convert document text into different languages:

- **Direct Translation**: Content is translated directly during the extraction process
- **Format Preservation**: Maintains text structure and formatting
- **Technical Accuracy**: Preserves units, formulas, model numbers, and technical specifications
- **Language Support**: Works with any target language supported by the AI model
- **Naming Convention**: Output files include the target language in their names (e.g., `document_german_full.md`)

Example usage with translation:
```bash
# Basic translation
python datasheet_parser.py document.pdf --translate --target-language "French"

# Translation with specific model and output directory
python datasheet_parser.py document.pdf \
    --translate --target-language "Spanish" \
    --model "gpt-4o" \
    --output "spanish_docs"
```

## Project Structure

- `datasheet_parser.py` - main script for processing PDF documents
- `pdf_utils.py` - utilities for working with PDF files
- `api_client.py` - client for interacting with OpenAI API
- `markdown_generator.py` - utilities for creating Markdown files
- `prompts.py` - system messages and instructions for the AI model

*Note: For a Russian version of this README, see [READMEru.md](READMEru.md)* 