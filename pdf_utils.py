import os
import tempfile
from pathlib import Path
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from typing import List, Tuple
from PIL import Image


def extract_images_from_pdf(pdf_path: str, output_dir: str = None, poppler_path: str = None, 
                           start_page: int = None, end_page: int = None) -> List[str]:
    """
    Extract page images from a PDF file and save them to a temporary directory.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory for saving images (if not specified, a temporary one is created)
        poppler_path: Path to Poppler executable files (e.g., "C:/Poppler/Library/bin")
        start_page: First page to extract (1-based index, default: first page)
        end_page: Last page to extract (1-based index, default: last page)
        
    Returns:
        List of paths to saved images
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="datasheet_parser_")
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    # Check if Poppler path exists
    if poppler_path is None:
        # Try to find Poppler in standard locations
        possible_paths = [
            "C:/Program Files/poppler/bin",
            "C:/Program Files (x86)/poppler/bin",
            "C:/Poppler/bin",
            "C:/Poppler/Library/bin",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "poppler/bin")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                poppler_path = path
                break
    
    # Get total page count to validate page range
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    # Validate and adjust page range
    if start_page is None:
        start_page = 1
    else:
        start_page = max(1, min(start_page, total_pages))
        
    if end_page is None:
        end_page = total_pages
    else:
        end_page = max(start_page, min(end_page, total_pages))
    
    # PDF2Image uses 0-based indexing, convert from 1-based
    first_page = start_page
    last_page = end_page
    
    # Extract pages as images
    try:
        images = convert_from_path(pdf_path, first_page=first_page, last_page=last_page, poppler_path=poppler_path)
    except Exception as e:
        if "poppler" in str(e).lower():
            raise Exception(
                "Could not find Poppler. Please install Poppler from "
                "https://github.com/oschwartz10612/poppler-windows/releases/ "
                "and specify the path using the --poppler-path argument."
            )
        raise e
    
    # Save images
    image_paths = []
    for i, image in enumerate(images):
        page_num = start_page + i
        img_path = os.path.join(output_dir, f"page_{page_num:03d}.png")
        image.save(img_path, "PNG")
        image_paths.append(img_path)
    
    return image_paths


def get_pdf_metadata(pdf_path: str) -> dict:
    """
    Get PDF file metadata.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary with metadata
    """
    reader = PdfReader(pdf_path)
    metadata = reader.metadata
    
    info = {
        "title": metadata.get("/Title", "Unknown"),
        "author": metadata.get("/Author", "Unknown"),
        "subject": metadata.get("/Subject", ""),
        "creator": metadata.get("/Creator", ""),
        "producer": metadata.get("/Producer", ""),
        "page_count": len(reader.pages)
    }
    
    return info


def resize_image_if_needed(image_path: str, max_size: int = 5 * 1024 * 1024) -> str:
    """
    Resize an image if it exceeds the specified size.
    
    Args:
        image_path: Path to the image
        max_size: Maximum size in bytes (default 5MB)
        
    Returns:
        Path to the image (original or modified)
    """
    file_size = os.path.getsize(image_path)
    
    if file_size <= max_size:
        return image_path
    
    # Open and resize the image
    with Image.open(image_path) as img:
        # Determine scaling factor
        scale_factor = (max_size / file_size) ** 0.5
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)
        
        # Resize and save
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        resized_img.save(image_path, optimize=True)
    
    return image_path 