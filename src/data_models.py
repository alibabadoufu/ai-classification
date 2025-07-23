"""
Pydantic data models for CAIS platform.
Defines structure for analysis results, training examples, and other data types.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    """Model for storing analysis results."""
    
    user_name: str = Field(..., description="Name of the analyst")
    company_name: str = Field(..., description="Name of the company being analyzed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    # Jurisdiction Classification Results
    jurisdiction: Optional[str] = Field(None, description="Identified jurisdiction")
    jurisdiction_reasoning: Optional[str] = Field(None, description="Reasoning for jurisdiction classification")
    jurisdiction_citation: Optional[str] = Field(None, description="Source text snippet for jurisdiction")
    jurisdiction_correct: Optional[bool] = Field(None, description="User validation flag for jurisdiction")
    
    # Counterparty Code Classification Results
    counterparty_code: Optional[str] = Field(None, description="Assigned counterparty code")
    counterparty_reasoning: Optional[str] = Field(None, description="Reasoning for counterparty classification")
    counterparty_citation: Optional[str] = Field(None, description="Source text snippet for counterparty")
    counterparty_correct: Optional[bool] = Field(None, description="User validation flag for counterparty")
    
    # Metadata
    document_names: List[str] = Field(default_factory=list, description="Names of uploaded documents")
    counterparty_file_name: Optional[str] = Field(None, description="Name of counterparty Excel file")
    s3_document_paths: List[str] = Field(default_factory=list, description="S3 paths of uploaded documents")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TrainingExample(BaseModel):
    """Model for storing training examples for DSPy optimization."""
    
    id: str = Field(..., description="Unique identifier for the training example")
    analysis_result: AnalysisResult = Field(..., description="Complete analysis result")
    document_text: str = Field(..., description="Parsed text from documents")
    counterparty_codes: Dict[str, str] = Field(..., description="Available counterparty codes mapping")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class JurisdictionClassificationInput(BaseModel):
    """Input model for jurisdiction classification."""
    
    document_text: str = Field(..., description="Text content of the legal documents")
    company_name: str = Field(..., description="Name of the company being analyzed")


class JurisdictionClassificationOutput(BaseModel):
    """Output model for jurisdiction classification."""
    
    jurisdiction: str = Field(..., description="Identified jurisdiction")
    reasoning: str = Field(..., description="Reasoning for the classification")
    citation: str = Field(..., description="Relevant text snippet from the document")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class CounterpartyClassificationInput(BaseModel):
    """Input model for counterparty classification."""
    
    document_text: str = Field(..., description="Text content of the legal documents")
    company_name: str = Field(..., description="Name of the company being analyzed")
    available_codes: Dict[str, str] = Field(..., description="Mapping of codes to descriptions")


class CounterpartyClassificationOutput(BaseModel):
    """Output model for counterparty classification."""
    
    code: str = Field(..., description="Assigned counterparty code")
    reasoning: str = Field(..., description="Reasoning for the classification")
    citation: str = Field(..., description="Relevant text snippet from the document")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class UserFeedback(BaseModel):
    """Model for user feedback submissions."""
    
    category: str = Field(..., description="Feedback category")
    message: str = Field(..., description="Detailed feedback message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Submission timestamp")
    user_name: Optional[str] = Field(None, description="Optional user identifier")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PromptVersion(BaseModel):
    """Model for tracking prompt versions."""
    
    version: str = Field(..., description="Version identifier")
    path: str = Field(..., description="File path to the prompt")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    accuracy: Optional[float] = Field(None, description="Accuracy on validation set")
    is_active: bool = Field(False, description="Whether this is the active version")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UsageMetrics(BaseModel):
    """Model for usage metrics and monitoring."""
    
    date: datetime = Field(..., description="Date of the metrics")
    analyses_count: int = Field(0, description="Number of analyses performed")
    unique_companies: int = Field(0, description="Number of unique companies analyzed")
    documents_processed: int = Field(0, description="Number of documents processed")
    accuracy_jurisdiction: Optional[float] = Field(None, description="Accuracy for jurisdiction classification")
    accuracy_counterparty: Optional[float] = Field(None, description="Accuracy for counterparty classification")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }