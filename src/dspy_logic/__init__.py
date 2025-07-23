"""
DSPy logic module for CAIS platform.
Contains signatures and modules for AI-powered classification tasks.
"""

from .signatures import JurisdictionClassification, CounterpartyClassification
from .modules import JurisdictionClassifier, CounterpartyClassifier, DocumentAnalysisModule

__all__ = [
    'JurisdictionClassification',
    'CounterpartyClassification', 
    'JurisdictionClassifier',
    'CounterpartyClassifier',
    'DocumentAnalysisModule'
]