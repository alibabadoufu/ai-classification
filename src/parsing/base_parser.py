"""
Abstract base class for document parsers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path


class BaseParser(ABC):
    """Abstract base class for document parsers."""
    
    def __init__(self):
        """Initialize the parser."""
        pass
    
    @abstractmethod
    def parse_document(self, file_path: str) -> str:
        """
        Parse a document and extract text content.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content
            
        Raises:
            Exception: If parsing fails
        """
        pass
    
    @abstractmethod
    def parse_excel(self, file_path: str) -> Dict[str, str]:
        """
        Parse an Excel file containing counterparty codes.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Dictionary mapping codes to descriptions
            
        Raises:
            Exception: If parsing fails
        """
        pass
    
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported file extensions
        """
        pass
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate if the file can be parsed by this parser.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is supported, False otherwise
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.supported_formats()
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get metadata information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file metadata
        """
        file_path = Path(file_path)
        
        return {
            "name": file_path.name,
            "size": file_path.stat().st_size if file_path.exists() else 0,
            "extension": file_path.suffix.lower(),
            "supported": self.validate_file(str(file_path))
        }