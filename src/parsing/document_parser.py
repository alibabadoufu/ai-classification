"""
Concrete document parser implementation using unstructured.io and pandas.
"""

import os
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd

try:
    from unstructured.partition.auto import partition
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False
    print("Warning: unstructured library not available. Document parsing will be limited.")

from .base_parser import BaseParser


class DocumentParser(BaseParser):
    """Document parser using unstructured.io for various document types."""
    
    def __init__(self):
        """Initialize the document parser."""
        super().__init__()
        self._supported_formats = ['.pdf', '.docx', '.doc', '.txt', '.xlsx']
        
        if not UNSTRUCTURED_AVAILABLE:
            print("Warning: Limited parsing capabilities due to missing unstructured library")
    
    def supported_formats(self) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported file extensions
        """
        return self._supported_formats
    
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
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise Exception(f"File not found: {file_path}")
        
        if not self.validate_file(str(file_path)):
            raise Exception(f"Unsupported file format: {file_path.suffix}")
        
        try:
            # Handle different file types
            if file_path.suffix.lower() == '.txt':
                return self._parse_text_file(str(file_path))
            elif file_path.suffix.lower() in ['.pdf', '.docx', '.doc']:
                return self._parse_with_unstructured(str(file_path))
            else:
                raise Exception(f"Unsupported document format: {file_path.suffix}")
                
        except Exception as e:
            raise Exception(f"Failed to parse document {file_path.name}: {str(e)}")
    
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
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise Exception(f"Excel file not found: {file_path}")
        
        if file_path.suffix.lower() != '.xlsx':
            raise Exception(f"Expected .xlsx file, got: {file_path.suffix}")
        
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Try to identify code and description columns
            # Look for common column names
            code_col = None
            desc_col = None
            
            for col in df.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in ['code', 'id', 'key']):
                    code_col = col
                elif any(keyword in col_lower for keyword in ['description', 'desc', 'name', 'title']):
                    desc_col = col
            
            # If no suitable columns found, use first two columns
            if code_col is None or desc_col is None:
                if len(df.columns) >= 2:
                    code_col = df.columns[0]
                    desc_col = df.columns[1]
                else:
                    raise Exception("Excel file must have at least 2 columns for code and description")
            
            # Create dictionary mapping
            result = {}
            for _, row in df.iterrows():
                code = str(row[code_col]).strip()
                description = str(row[desc_col]).strip()
                
                if code and code != 'nan' and description and description != 'nan':
                    result[code] = description
            
            if not result:
                raise Exception("No valid code-description pairs found in Excel file")
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to parse Excel file {file_path.name}: {str(e)}")
    
    def _parse_text_file(self, file_path: str) -> str:
        """
        Parse a plain text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            File content as string
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _parse_with_unstructured(self, file_path: str) -> str:
        """
        Parse document using unstructured.io library.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Extracted text content
        """
        if not UNSTRUCTURED_AVAILABLE:
            # Fallback for when unstructured is not available
            return self._parse_fallback(file_path)
        
        try:
            # Use unstructured to partition the document
            elements = partition(filename=file_path)
            
            # Extract text from all elements
            text_content = []
            for element in elements:
                if hasattr(element, 'text') and element.text.strip():
                    text_content.append(element.text.strip())
            
            return '\n'.join(text_content)
            
        except Exception as e:
            # Fallback to basic parsing if unstructured fails
            print(f"Unstructured parsing failed for {file_path}: {str(e)}")
            return self._parse_fallback(file_path)
    
    def _parse_fallback(self, file_path: str) -> str:
        """
        Fallback parser for when unstructured is not available or fails.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Basic extracted content or error message
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.txt':
            return self._parse_text_file(file_path)
        elif file_ext == '.pdf':
            return f"[PDF Document: {Path(file_path).name}]\nNote: PDF parsing requires unstructured library for full text extraction."
        elif file_ext in ['.docx', '.doc']:
            return f"[Word Document: {Path(file_path).name}]\nNote: Word document parsing requires unstructured library for full text extraction."
        else:
            return f"[Document: {Path(file_path).name}]\nNote: This document type requires additional parsing libraries."
    
    def parse_multiple_documents(self, file_paths: List[str]) -> str:
        """
        Parse multiple documents and combine their content.
        
        Args:
            file_paths: List of document file paths
            
        Returns:
            Combined text content from all documents
        """
        combined_text = []
        
        for file_path in file_paths:
            try:
                text = self.parse_document(file_path)
                file_name = Path(file_path).name
                combined_text.append(f"=== {file_name} ===\n{text}\n")
            except Exception as e:
                print(f"Warning: Failed to parse {file_path}: {str(e)}")
                combined_text.append(f"=== {Path(file_path).name} ===\n[Parse Error: {str(e)}]\n")
        
        return '\n'.join(combined_text)