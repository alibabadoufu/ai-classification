"""
DSPy signatures for CAIS classification tasks.
"""

import dspy
from typing import Dict, Any


class JurisdictionClassification(dspy.Signature):
    """
    Signature for jurisdiction classification task.
    Analyzes legal documents to determine company jurisdiction.
    """
    
    document_text = dspy.InputField(desc="Text content of the legal documents")
    company_name = dspy.InputField(desc="Name of the company being analyzed")
    
    jurisdiction = dspy.OutputField(desc="Identified jurisdiction of the company")
    reasoning = dspy.OutputField(desc="Detailed reasoning for the jurisdiction classification")
    citation = dspy.OutputField(desc="Relevant text snippet from the document that supports the classification")


class CounterpartyClassification(dspy.Signature):
    """
    Signature for counterparty code classification task.
    Analyzes legal documents to assign appropriate counterparty codes.
    """
    
    document_text = dspy.InputField(desc="Text content of the legal documents")
    company_name = dspy.InputField(desc="Name of the company being analyzed")
    available_codes = dspy.InputField(desc="List of available counterparty codes and their descriptions")
    
    code = dspy.OutputField(desc="Most appropriate counterparty code from the available options")
    reasoning = dspy.OutputField(desc="Detailed reasoning for the counterparty code assignment")
    citation = dspy.OutputField(desc="Relevant text snippet from the document that supports the classification")