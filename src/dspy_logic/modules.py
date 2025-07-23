"""
DSPy modules for CAIS classification pipelines.
Combines signatures into complete classification workflows.
"""

import dspy
from typing import Dict, Any, Optional
from .signatures import JurisdictionClassification, CounterpartyClassification


class JurisdictionClassifier(dspy.Module):
    """
    DSPy module for jurisdiction classification.
    """
    
    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(JurisdictionClassification)
    
    def forward(self, document_text: str, company_name: str) -> Dict[str, Any]:
        """
        Classify jurisdiction for a company based on legal documents.
        
        Args:
            document_text: Text content from legal documents
            company_name: Name of the company
            
        Returns:
            Dictionary with jurisdiction, reasoning, and citation
        """
        try:
            result = self.classify(
                document_text=document_text,
                company_name=company_name
            )
            
            return {
                "jurisdiction": result.jurisdiction,
                "reasoning": result.reasoning,
                "citation": result.citation,
                "confidence": 0.8  # Default confidence, can be improved with calibration
            }
            
        except Exception as e:
            return {
                "jurisdiction": "Unknown",
                "reasoning": f"Classification failed: {str(e)}",
                "citation": "N/A",
                "confidence": 0.0
            }


class CounterpartyClassifier(dspy.Module):
    """
    DSPy module for counterparty code classification.
    """
    
    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(CounterpartyClassification)
    
    def forward(
        self, 
        document_text: str, 
        company_name: str, 
        available_codes: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Classify counterparty code for a company based on legal documents.
        
        Args:
            document_text: Text content from legal documents
            company_name: Name of the company
            available_codes: Dictionary mapping codes to descriptions
            
        Returns:
            Dictionary with code, reasoning, and citation
        """
        try:
            # Format available codes for the prompt
            codes_text = "\n".join([f"{code}: {desc}" for code, desc in available_codes.items()])
            
            result = self.classify(
                document_text=document_text,
                company_name=company_name,
                available_codes=codes_text
            )
            
            # Validate that the returned code is in available codes
            code = result.code
            if code not in available_codes:
                # Try to find a close match or default to the first code
                code = list(available_codes.keys())[0] if available_codes else "UNKNOWN"
            
            return {
                "code": code,
                "reasoning": result.reasoning,
                "citation": result.citation,
                "confidence": 0.8  # Default confidence, can be improved with calibration
            }
            
        except Exception as e:
            fallback_code = list(available_codes.keys())[0] if available_codes else "UNKNOWN"
            return {
                "code": fallback_code,
                "reasoning": f"Classification failed: {str(e)}",
                "citation": "N/A",
                "confidence": 0.0
            }


class DocumentAnalysisModule(dspy.Module):
    """
    Combined module for complete document analysis including both jurisdiction and counterparty classification.
    """
    
    def __init__(self):
        super().__init__()
        self.jurisdiction_classifier = JurisdictionClassifier()
        self.counterparty_classifier = CounterpartyClassifier()
    
    def forward(
        self,
        document_text: str,
        company_name: str,
        available_codes: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Perform complete document analysis with both jurisdiction and counterparty classification.
        
        Args:
            document_text: Text content from legal documents
            company_name: Name of the company
            available_codes: Dictionary mapping counterparty codes to descriptions
            
        Returns:
            Dictionary with both jurisdiction and counterparty results
        """
        # Perform jurisdiction classification
        jurisdiction_result = self.jurisdiction_classifier.forward(
            document_text=document_text,
            company_name=company_name
        )
        
        # Perform counterparty classification
        counterparty_result = self.counterparty_classifier.forward(
            document_text=document_text,
            company_name=company_name,
            available_codes=available_codes
        )
        
        return {
            "jurisdiction": jurisdiction_result,
            "counterparty": counterparty_result
        }


class OptimizedJurisdictionClassifier(dspy.Module):
    """
    Optimized version of jurisdiction classifier with few-shot examples.
    Used after DSPy optimization process.
    """
    
    def __init__(self, few_shot_examples: Optional[list] = None):
        super().__init__()
        if few_shot_examples:
            self.classify = dspy.FewShot(JurisdictionClassification, examples=few_shot_examples)
        else:
            self.classify = dspy.ChainOfThought(JurisdictionClassification)
    
    def forward(self, document_text: str, company_name: str) -> Dict[str, Any]:
        """Forward pass with optimized prompt."""
        return JurisdictionClassifier.forward(self, document_text, company_name)


class OptimizedCounterpartyClassifier(dspy.Module):
    """
    Optimized version of counterparty classifier with few-shot examples.
    Used after DSPy optimization process.
    """
    
    def __init__(self, few_shot_examples: Optional[list] = None):
        super().__init__()
        if few_shot_examples:
            self.classify = dspy.FewShot(CounterpartyClassification, examples=few_shot_examples)
        else:
            self.classify = dspy.ChainOfThought(CounterpartyClassification)
    
    def forward(
        self, 
        document_text: str, 
        company_name: str, 
        available_codes: Dict[str, str]
    ) -> Dict[str, Any]:
        """Forward pass with optimized prompt."""
        return CounterpartyClassifier.forward(self, document_text, company_name, available_codes)