#!/usr/bin/env python3
"""
Demo script for CAIS platform.
Shows basic functionality without requiring external services.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

def create_demo_document():
    """Create a sample legal document for testing."""
    demo_content = """
CORPORATE INCORPORATION DOCUMENT

XYZ Technology Corporation
Incorporated under Delaware General Corporation Law

Principal Office: 123 Tech Street, Wilmington, Delaware 19801, USA
Date of Incorporation: January 15, 2020

Business Purpose: 
The corporation is engaged in the development and deployment of enterprise software solutions, 
cloud computing services, and artificial intelligence technologies. The company provides 
technology consulting services to Fortune 500 companies across various industry sectors.

Registered Agent: Corporate Services of Delaware
Registered Office: 1209 Orange Street, Wilmington, Delaware 19801

Governing Law: This corporation shall be governed by the laws of the State of Delaware.

Board of Directors:
- John Smith, Chief Executive Officer
- Sarah Johnson, Chief Technology Officer  
- Michael Brown, Chief Financial Officer

The corporation is authorized to issue 10,000,000 shares of common stock.

This document serves as official proof of incorporation under Delaware state law.
    """
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(demo_content)
        return f.name

def demo_document_parsing():
    """Demonstrate document parsing functionality."""
    print("📄 Document Parsing Demo")
    print("-" * 30)
    
    try:
        from src.parsing.document_parser import DocumentParser
        
        # Create parser
        parser = DocumentParser()
        
        # Create demo document
        doc_path = create_demo_document()
        print(f"Created demo document: {os.path.basename(doc_path)}")
        
        # Parse document
        extracted_text = parser.parse_document(doc_path)
        
        print(f"✓ Successfully parsed document")
        print(f"📊 Extracted {len(extracted_text)} characters")
        print("\n📝 Sample extracted text:")
        print(extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text)
        
        # Clean up
        os.unlink(doc_path)
        return True
        
    except Exception as e:
        print(f"❌ Parsing demo failed: {e}")
        return False

def demo_data_models():
    """Demonstrate data model functionality."""
    print("\n📊 Data Models Demo")
    print("-" * 20)
    
    try:
        from src.data_models import AnalysisResult, TrainingExample, UserFeedback
        
        # Create analysis result
        analysis = AnalysisResult(
            user_name="Demo User",
            company_name="XYZ Technology Corporation",
            timestamp=datetime.now(),
            jurisdiction="Delaware",
            jurisdiction_reasoning="Company incorporated under Delaware General Corporation Law",
            counterparty_code="TECH_001",
            counterparty_reasoning="Technology services provider based on business description"
        )
        
        print("✓ Created analysis result:")
        print(f"   Company: {analysis.company_name}")
        print(f"   Jurisdiction: {analysis.jurisdiction}")
        print(f"   Counterparty Code: {analysis.counterparty_code}")
        
        # Create training example
        training = TrainingExample(
            id="demo-training-123",
            analysis_result=analysis,
            document_text="Sample legal document text...",
            counterparty_codes={"TECH_001": "Technology Services Provider"}
        )
        
        print("✓ Created training example")
        
        # Create user feedback
        feedback = UserFeedback(
            category="classification_feedback",
            message="Jurisdiction classification is accurate for this Delaware corporation.",
            user_name="Demo User"
        )
        
        print("✓ Created user feedback")
        return True
        
    except Exception as e:
        print(f"❌ Data models demo failed: {e}")
        return False

def demo_dspy_signatures():
    """Demonstrate DSPy signature functionality."""
    print("\n🤖 DSPy Signatures Demo")
    print("-" * 25)
    
    try:
        from src.dspy_logic.signatures import JurisdictionClassification, CounterpartyClassification
        
        print("✓ Jurisdiction Classification signature loaded")
        print("   Inputs: document_text, company_name") 
        print("   Outputs: jurisdiction, reasoning, citation")
        
        print("✓ Counterparty Classification signature loaded")
        print("   Inputs: document_text, company_name, available_codes")
        print("   Outputs: code, reasoning, citation")
        
        return True
        
    except Exception as e:
        print(f"❌ DSPy signatures demo failed: {e}")
        return False

def demo_counterparty_codes():
    """Demonstrate counterparty codes loading."""
    print("\n📋 Counterparty Codes Demo")
    print("-" * 26)
    
    try:
        import pandas as pd
        
        if os.path.exists("sample_counterparty_codes.xlsx"):
            df = pd.read_excel("sample_counterparty_codes.xlsx")
            print(f"✓ Loaded {len(df)} counterparty codes:")
            
            for _, row in df.head(3).iterrows():
                print(f"   {row['Code']}: {row['Description']}")
            
            if len(df) > 3:
                print(f"   ... and {len(df) - 3} more codes")
            
            return True
        else:
            print("❌ Sample counterparty codes file not found")
            return False
            
    except Exception as e:
        print(f"❌ Counterparty codes demo failed: {e}")
        return False

def main():
    """Run the complete demo."""
    print("🎯 CAIS Platform Demo")
    print("=" * 40)
    print("This demo showcases core CAIS functionality")
    print("without requiring external LLM or S3 services.\n")
    
    demos = [
        demo_document_parsing,
        demo_data_models,
        demo_dspy_signatures,
        demo_counterparty_codes
    ]
    
    success_count = 0
    for demo in demos:
        if demo():
            success_count += 1
        print()
    
    print("=" * 40)
    print(f"🎉 Demo completed: {success_count}/{len(demos)} components working")
    
    if success_count == len(demos):
        print("\n✅ All core components are functional!")
        print("🚀 Ready to start the full application with: ./run.sh")
    else:
        print("\n⚠️  Some components had issues. Check the output above.")
    
    print("\n📚 Next steps:")
    print("1. Configure .env file with your LLM API and S3 settings")
    print("2. Run ./run.sh to start the Gradio interface")
    print("3. Upload documents and test the analysis features")

if __name__ == "__main__":
    main()