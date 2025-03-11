import os
from pathlib import Path
from typing import List, Dict, Any
import re


def create_markdown_file(content: str, output_path: str) -> None:
    """
    Create a Markdown file with the specified content.
    
    Args:
        content: Content to write to the file
        output_path: Path for saving the file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Write content to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def merge_markdown_files(file_paths: List[str], output_path: str, metadata: Dict[str, Any] = None) -> None:
    """
    Merge multiple Markdown files into one with metadata addition.
    
    Args:
        file_paths: List of paths to files for merging
        output_path: Path for saving the merged file
        metadata: Document metadata to include in the header
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Create header with metadata
    header = ""
    if metadata:
        header = "# " + str(metadata.get("title", "Documentation")) + "\n\n"
        if metadata.get("author"):
            header += f"**Author**: {metadata['author']}\n\n"
        if metadata.get("subject"):
            header += f"**Description**: {metadata['subject']}\n\n"
        header += "---\n\n"
    
    # Merge file contents
    content = []
    for file_path in file_paths:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read().strip()
                content.append(file_content)
    
    # Write the result
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header + "\n\n".join(content))


def clean_markdown(content: str) -> str:
    """
    Clean and format Markdown content.
    
    Args:
        content: Original Markdown content
        
    Returns:
        Cleaned content
    """
    # Remove excessive empty lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Remove page numbers and headers/footers (simple heuristic)
    content = re.sub(r'\n\s*Page \d+\s*\n', '\n', content, flags=re.IGNORECASE)
    content = re.sub(r'\n\s*\d+\s*\n', '\n', content)
    
    # Other cleanups as needed
    
    return content


def add_table_of_contents(content: str) -> str:
    """
    Add a table of contents based on headers in Markdown.
    
    Args:
        content: Original Markdown content
        
    Returns:
        Content with added table of contents
    """
    # Find all headers
    headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
    
    if not headers:
        return content
    
    # Create table of contents
    toc = "## Table of Contents\n\n"
    
    for header_level, header_text in headers:
        # Skip table of contents if it already exists
        if header_text.lower() in ["table of contents", "contents", "toc"]:
            continue
            
        # Get header level
        level = len(header_level) - 1  # -1 because # is level 1, but indentation will be 0
        
        # Create anchor identifier
        anchor = header_text.lower().replace(' ', '-')
        anchor = re.sub(r'[^\w\-]', '', anchor)
        
        # Add TOC item
        toc += f"{' ' * (level * 2)}- [{header_text}](#{anchor})\n"
    
    # Insert TOC after the first header
    first_header_end = re.search(r'^#.+$', content, re.MULTILINE).end()
    result = content[:first_header_end] + "\n\n" + toc + "\n" + content[first_header_end:]
    
    return result 