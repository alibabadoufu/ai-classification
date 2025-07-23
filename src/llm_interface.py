"""
LLM Interface for CAIS platform.
Handles all interactions with the in-house OpenAI-compatible LLM API.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from config import config


class LLMInterface:
    """Interface for communicating with the in-house LLM API."""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        """
        Initialize the LLM interface.
        
        Args:
            api_url: Override for the LLM API URL
            api_key: Override for the API key
        """
        self.api_url = api_url or config.LLM_API_URL
        self.api_key = api_key or config.LLM_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Ensure URL ends with proper endpoint
        if not self.api_url.endswith('/chat/completions'):
            if self.api_url.endswith('/'):
                self.api_url += 'chat/completions'
            else:
                self.api_url += '/chat/completions'
    
    def _make_request(
        self,
        messages: List[Dict[str, str]],
        model: str = "default",
        temperature: float = 0.1,
        max_tokens: int = 2048,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a request to the LLM API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            Exception: If API request fails
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"LLM API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM API response: {str(e)}")
    
    def generate_completion(
        self,
        prompt: str,
        system_message: str = None,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> str:
        """
        Generate a completion for a given prompt.
        
        Args:
            prompt: The user prompt
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated text content
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self._make_request(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected LLM API response format: {str(e)}")
    
    def classify_jurisdiction(
        self,
        document_text: str,
        company_name: str,
        prompt_template: str
    ) -> Dict[str, Any]:
        """
        Classify jurisdiction using the LLM.
        
        Args:
            document_text: Text content of legal documents
            company_name: Name of the company
            prompt_template: Template for the jurisdiction classification prompt
            
        Returns:
            Dictionary with jurisdiction, reasoning, and citation
        """
        # Format the prompt with the provided data
        formatted_prompt = prompt_template.format(
            document_text=document_text,
            company_name=company_name
        )
        
        system_message = """You are a legal expert specializing in corporate jurisdiction analysis.
Your task is to analyze legal documents and determine the jurisdiction of a company.
Always provide your response in the following JSON format:
{
    "jurisdiction": "specific jurisdiction",
    "reasoning": "detailed reasoning for the classification",
    "citation": "relevant text snippet from the document",
    "confidence": 0.95
}"""
        
        response_text = self.generate_completion(
            prompt=formatted_prompt,
            system_message=system_message,
            temperature=0.1
        )
        
        try:
            # Parse JSON response
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            # Fallback if response is not JSON
            return {
                "jurisdiction": "Unknown",
                "reasoning": "Failed to parse LLM response",
                "citation": response_text[:200] + "...",
                "confidence": 0.0
            }
    
    def classify_counterparty(
        self,
        document_text: str,
        company_name: str,
        available_codes: Dict[str, str],
        prompt_template: str
    ) -> Dict[str, Any]:
        """
        Classify counterparty code using the LLM.
        
        Args:
            document_text: Text content of legal documents
            company_name: Name of the company
            available_codes: Dictionary mapping codes to descriptions
            prompt_template: Template for the counterparty classification prompt
            
        Returns:
            Dictionary with code, reasoning, and citation
        """
        # Format the available codes for the prompt
        codes_text = "\n".join([f"{code}: {desc}" for code, desc in available_codes.items()])
        
        # Format the prompt with the provided data
        formatted_prompt = prompt_template.format(
            document_text=document_text,
            company_name=company_name,
            available_codes=codes_text
        )
        
        system_message = """You are a legal expert specializing in corporate counterparty classification.
Your task is to analyze legal documents and assign the most appropriate counterparty code.
Always provide your response in the following JSON format:
{
    "code": "selected_code",
    "reasoning": "detailed reasoning for the classification",
    "citation": "relevant text snippet from the document",
    "confidence": 0.95
}"""
        
        response_text = self.generate_completion(
            prompt=formatted_prompt,
            system_message=system_message,
            temperature=0.1
        )
        
        try:
            # Parse JSON response
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            # Fallback if response is not JSON
            return {
                "code": "UNKNOWN",
                "reasoning": "Failed to parse LLM response",
                "citation": response_text[:200] + "...",
                "confidence": 0.0
            }
    
    def test_connection(self) -> bool:
        """
        Test the connection to the LLM API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self.generate_completion(
                prompt="Test connection",
                temperature=0.1,
                max_tokens=10
            )
            return True
        except Exception:
            return False