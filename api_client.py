import os
import base64
import requests
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any


# Load environment variables
load_dotenv()

# API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# URL for API requests (can be overridden to use a compatible server)
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")

# Default model
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")


class OpenAIClient:
    """Client for interacting with OpenAI API or compatible server"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: API key for OpenAI (if not specified, taken from environment variables)
            model: Model identifier (if not specified, uses default value)
            api_url: URL for API requests (if not specified, uses default value)
        """
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key not specified. Set it in the .env file or when creating the client.")
        
        self.model = model or DEFAULT_MODEL
        self.api_url = api_url or OPENAI_API_URL
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode an image to base64.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Base64 string
        """
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    def process_page(self, 
                    image_path: str, 
                    previous_context: str = "", 
                    instructions: str = "Extract all textual information from the datasheet page and format it in Markdown") -> str:
        """
        Process a datasheet page through the API.
        
        Args:
            image_path: Path to the page image
            previous_context: Context from previous pages
            instructions: Instructions for the model
            
        Returns:
            Extracted and formatted text
        """
        # Encode the image
        base64_image = self.encode_image(image_path)
        
        # Create messages for the model
        messages = []
        
        # Add system instruction
        system_message = (
            "You are an expert in extracting and structuring information from technical documentation. "
            "Your task is to extract all valuable information from datasheet pages and format it in Markdown. "
            "Use tables, lists, headings, and other Markdown elements for optimal presentation. "
            "Preserve all technical specifications, parameters, diagrams descriptions, and functional details. "
            "Format tables properly with aligned columns when representing tabular data. "
            "Include only essential technical information, ignoring page numbers, headers, footers, "
            "and other formatting elements not related to the content. "
            "Your output should be well-structured, comprehensive, and immediately usable as technical documentation."
        )
        
        messages.append({"role": "system", "content": system_message})
        
        # Create message content
        content = []
        
        # If there is previous context, add it
        if previous_context:
            content.append({
                "type": "text", 
                "text": "Here is context from previous datasheet pages:\n\n" + previous_context
            })
        
        # Add instructions and image
        content.append({"type": "text", "text": instructions})
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })
        
        messages.append({"role": "user", "content": content})
        
        # Create request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 0.1,  # Low temperature for more deterministic responses
        }
        
        # Send request
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        # Check response
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code}, {response.text}")
        
        # Extract response
        result = response.json()
        
        try:
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected response format: {str(e)}, {result}") 