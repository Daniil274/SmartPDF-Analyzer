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
    parser = argparse.ArgumentParser(description="Datasheet parser using multimodal AI models")
    parser.add_argument("pdf_path", help="Path to the PDF datasheet file")
    parser.add_argument("--output", "-o", help="Directory for saving results", default="output")
    parser.add_argument("--model", "-m", help="Model to use", default=None)
    parser.add_argument("--context-window", "-c", type=int, help="Number of previous pages for context", default=2)
    parser.add_argument("--temp-dir", "-t", help="Temporary directory for images", default=None)
    parser.add_argument("--max-tokens", type=int, help="Maximum number of tokens for the model response", default=4096)
    parser.add_argument("--poppler-path", "-p", help="Path to Poppler executable files (e.g., C:/Poppler/Library/bin)", default=None)
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    return parser.parse_args()


def process_datasheet(pdf_path, output_dir, model=None, context_window=2, temp_dir=None, poppler_path=None, debug=False):
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
    
    Returns:
        Path to the generated Markdown file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get PDF metadata
    logger.info(f"Extracting metadata from {pdf_path}")
    metadata = get_pdf_metadata(pdf_path)
    logger.info(f"Title: {metadata.get('title', 'Unknown')}, pages: {metadata.get('page_count', 0)}")
    
    # Determine output filename based on PDF name
    output_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Extract page images
    logger.info(f"Extracting pages from PDF as images")
    image_paths = extract_images_from_pdf(pdf_path, temp_dir, poppler_path)
    logger.info(f"Extracted {len(image_paths)} pages")
    
    # Initialize API client
    client = OpenAIClient(model=model)
    
    # Process each page
    page_markdown_files = []
    context = ""
    context_pages = []
    
    logger.info(f"Starting page processing")
    for i, image_path in enumerate(tqdm(image_paths)):
        page_num = i + 1
        logger.info(f"Processing page {page_num}/{len(image_paths)}")
        
        # Check and resize image if needed
        img_path = resize_image_if_needed(image_path)
        
        # Create instructions for the model
        instructions = (
            f"This is page {page_num} of {len(image_paths)} from the datasheet. "
            f"Extract all technical information and format it in Markdown. "
            f"Use headings, tables, lists, and other Markdown elements for optimal presentation. "
            f"Maintain technical integrity while creating a clean, structured document."
        )
        
        # Process the page
        try:
            logger.info(f"Sending page {page_num} image to API")
            markdown_content = client.process_page(
                image_path=img_path,
                previous_context=context,
                instructions=instructions
            )
            
            # Clean the Markdown
            clean_content = clean_markdown(markdown_content)
            
            # Save result for individual page
            page_md_file = os.path.join(output_dir, f"{output_name}_page_{page_num:03d}.md")
            create_markdown_file(clean_content, page_md_file)
            page_markdown_files.append(page_md_file)
            
            # Update context
            context_pages.append(clean_content)
            if len(context_pages) > context_window:
                context_pages.pop(0)
            context = "\n\n".join(context_pages)
            
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
    
    # Process the datasheet
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
        logger.info(f"Successfully created file: {output_file}")
        return 0
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        if args.debug:
            logger.exception("Error details:")
        return 1


if __name__ == "__main__":
    exit(main()) 