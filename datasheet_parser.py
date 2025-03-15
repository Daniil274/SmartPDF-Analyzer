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
from api_client import OpenAIClient
from markdown_generator import create_markdown_file, merge_markdown_files, clean_markdown, add_table_of_contents
from prompts import PAGE_INSTRUCTION_TEMPLATE, PAGE_INSTRUCTION_TEMPLATE_TRANSLATE


# Logging setup
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
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Document text extraction using multimodal AI models")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", "-o", help="Directory for saving results", default="output")
    parser.add_argument("--model", "-m", help="Model to use", default=None)
    parser.add_argument("--temp-dir", "-t", help="Temporary directory for images", default=None)
    parser.add_argument("--poppler-path", "-p", help="Path to Poppler executable files (e.g., C:/Poppler/Library/bin)", default=None)
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--translate", "-tr", action="store_true", help="Enable translation of the parsed document")
    parser.add_argument("--target-language", "-tl", help="Target language for translation (e.g., 'Russian', 'German')", default=None)
    parser.add_argument("--start-page", "-sp", type=int, help="First page to process (1-based index)", default=None)
    parser.add_argument("--end-page", "-ep", type=int, help="Last page to process (1-based index)", default=None)
    
    return parser.parse_args()


def process_datasheet(pdf_path, output_dir, model=None, context_window=2, temp_dir=None, poppler_path=None, 
                     debug=False, translate=False, target_language=None, start_page=None, end_page=None, use_context=True):
    """
    Process the entire datasheet.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory for saving results
        model: Model identifier to use
        context_window: Number of previous pages for context
        temp_dir: Directory for temporary files
        poppler_path: Path to Poppler executable files
        debug: Debug mode flag
        translate: Flag indicating whether to translate the content
        target_language: Target language for translation
        start_page: First page to process (1-based index)
        end_page: Last page to process (1-based index)
        use_context: Flag indicating whether to use context from previous pages
    
    Returns:
        Path to the generated Markdown file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Настройка логгера для сохранения промптов и ответов модели
    prompt_logger = logging.getLogger("ModelPrompts")
    if debug:
        prompt_file_handler = logging.FileHandler("model_prompts.log")
        prompt_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        prompt_logger.addHandler(prompt_file_handler)
        prompt_logger.setLevel(logging.DEBUG)
    
    # Get PDF metadata
    logger.info(f"Extracting metadata from {pdf_path}")
    metadata = get_pdf_metadata(pdf_path)
    total_pages = metadata.get('page_count', 0)
    logger.info(f"Title: {metadata.get('title', 'Unknown')}, pages: {total_pages}")
    
    # Validate page range
    if start_page is not None:
        logger.info(f"Starting from page {start_page}")
    if end_page is not None:
        logger.info(f"Ending at page {end_page}")
    
    # Determine output filename based on PDF name
    output_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Add page range to filename if specified
    page_range_suffix = ""
    if start_page is not None or end_page is not None:
        start_str = str(start_page) if start_page is not None else "1"
        end_str = str(end_page) if end_page is not None else str(total_pages)
        page_range_suffix = f"_p{start_str}-{end_str}"
        output_name = f"{output_name}{page_range_suffix}"
    
    if translate and target_language:
        output_name = f"{output_name}_{target_language.lower()}"
    
    # Extract page images
    logger.info(f"Extracting pages from PDF as images")
    image_paths = extract_images_from_pdf(
        pdf_path, 
        temp_dir, 
        poppler_path,
        start_page=start_page,
        end_page=end_page
    )
    logger.info(f"Extracted {len(image_paths)} pages")
    
    # Initialize API client
    client = OpenAIClient(model=model)
    
    # Process each page
    page_markdown_files = []
    context = ""
    context_pages = []
    
    # We're disabling context by default, so we'll just log that it's disabled
    logger.info("Context feature is disabled. Each page will be processed independently.")
    
    logger.info(f"Starting page processing")
    for i, image_path in enumerate(tqdm(image_paths)):
        # Get actual page number (file name format: page_XXX.png)
        page_filename = os.path.basename(image_path)
        try:
            page_num = int(page_filename.split('_')[1].split('.')[0])
        except (IndexError, ValueError):
            page_num = i + 1  # Fallback if filename parsing fails
            
        logger.info(f"Processing page {page_num}/{total_pages}")
        
        # Check and resize image if needed
        img_path = resize_image_if_needed(image_path)
        
        # Create instructions for the model
        if translate and target_language:
            logger.info(f"Translating content to {target_language}")
            instructions = PAGE_INSTRUCTION_TEMPLATE_TRANSLATE.format(
                page_num=page_num,
                total_pages=total_pages,
                target_language=target_language
            )
        else:
            instructions = PAGE_INSTRUCTION_TEMPLATE.format(
                page_num=page_num,
                total_pages=total_pages
            )
        
        # Process the page
        try:
            logger.info(f"Sending page {page_num} image to API")
            # We're always passing an empty context now, regardless of use_context
            previous_context = ""
            
            markdown_content = client.process_page(
                image_path=img_path,
                previous_context=previous_context,
                instructions=instructions,
                translate=translate,
                target_language=target_language
            )
            
            # Clean the Markdown
            clean_content = clean_markdown(markdown_content)
            
            # Save result for individual page
            page_md_file = os.path.join(output_dir, f"{output_name}_page_{page_num:03d}.md")
            create_markdown_file(clean_content, page_md_file)
            page_markdown_files.append(page_md_file)
            
            # In debug mode: pause between requests for easier debugging
            if debug and i < len(image_paths) - 1:
                logger.debug(f"Pausing 3 seconds before processing next page")
                time.sleep(3)
                
        except Exception as e:
            logger.error(f"Error processing page {page_num}: {str(e)}")
            # Continue with next page
    
    # Merge all pages into one document
    logger.info(f"Merging {len(page_markdown_files)} pages into one document")
    output_md_file = os.path.join(output_dir, f"{output_name}_full.md")
    merge_markdown_files(page_markdown_files, output_md_file, metadata)
    
    # Add table of contents
    with open(output_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content_with_toc = add_table_of_contents(content)
    
    with open(output_md_file, 'w', encoding='utf-8') as f:
        f.write(content_with_toc)
    
    logger.info(f"Processing complete. Result saved to {output_md_file}")
    return output_md_file


def main():
    """Main function"""
    load_dotenv()
    args = parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Check if PDF file exists
    if not os.path.exists(args.pdf_path):
        logger.error(f"PDF file not found: {args.pdf_path}")
        return 1
    
    # Check translation parameters
    if args.translate and not args.target_language:
        logger.error("Translation requested but target language not specified. Use --target-language to specify the language.")
        return 1
    
    # Check page range parameters
    if args.start_page is not None and args.start_page < 1:
        logger.error("Start page must be at least 1.")
        return 1
    
    if args.end_page is not None and args.start_page is not None and args.end_page < args.start_page:
        logger.error("End page must be greater than or equal to start page.")
        return 1
    
    # Process the document
    try:
        output_file = process_datasheet(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            model=args.model,
            context_window=0,  # Context window is irrelevant as we're not using context
            temp_dir=args.temp_dir,
            poppler_path=args.poppler_path,
            debug=args.debug,
            translate=args.translate,
            target_language=args.target_language,
            start_page=args.start_page,
            end_page=args.end_page,
            use_context=False  # Always disable context
        )
        logger.info(f"Successfully created file: {output_file}")
        return 0
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        if args.debug:
            logger.exception("Error details:")
        return 1


if __name__ == "__main__":
    exit(main()) 