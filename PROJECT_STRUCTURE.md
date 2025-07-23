# 🏗️ CAIS Project Structure

This document outlines the complete structure of the CAIS (Corporate Analysis & Intelligence Suite) platform.

```
CAIS/
├── 📄 main.py                          # Main Gradio application (4 tabs)
├── ⚙️ config.py                        # Configuration management
├── 📋 requirements.txt                 # Python dependencies
├── 🔧 .env.example                     # Environment variables template
├── 📖 README.md                        # Main documentation
├── 🚀 run.sh                           # Startup script
├── 🎯 demo.py                          # Demo and testing script
├── 📊 sample_counterparty_codes.xlsx   # Sample counterparty codes
│
├── 📁 src/                             # Core application modules
│   ├── 📄 __init__.py
│   ├── 📊 data_models.py               # Pydantic models
│   ├── 🤖 llm_interface.py             # LLM API interface
│   │
│   ├── 📁 parsing/                     # Document parsing modules
│   │   ├── 📄 __init__.py
│   │   ├── 🔧 base_parser.py           # Abstract parser base class
│   │   └── 📄 document_parser.py       # Concrete parser implementation
│   │
│   ├── 📁 dspy_logic/                  # DSPy AI modules
│   │   ├── 📄 __init__.py
│   │   ├── ✍️ signatures.py            # DSPy signatures
│   │   └── 🧠 modules.py               # DSPy modules and pipelines
│   │
│   └── 📁 utils/                       # Utility functions
│       ├── 📄 __init__.py
│       └── ☁️ s3_handler.py            # S3 operations
│
└── 📁 prompts/                         # Prompt templates
    ├── 📁 jurisdiction/                # Jurisdiction classification prompts
    │   └── 📄 v1_base.txt
    └── 📁 counterparty/                # Counterparty classification prompts
        └── 📄 v1_base.txt
```

## 🔧 Key Components

### **Main Application (`main.py`)**
- **Tab 1: Document Analysis** - Upload and analyze legal documents
- **Tab 2: Fine-Tuning** - DSPy prompt optimization with training data
- **Tab 3: Control Panel** - Admin features and system management
- **Tab 4: Feedback** - User feedback submission and analytics

### **Core Modules**

#### **Data Models (`src/data_models.py`)**
- `AnalysisResult` - Structured analysis outputs
- `TrainingExample` - Training data for DSPy optimization
- `UserFeedback` - User feedback submissions
- `PromptVersion` - Prompt version tracking
- `UsageMetrics` - Platform usage analytics

#### **LLM Interface (`src/llm_interface.py`)**
- OpenAI-compatible API integration
- Retry logic and error handling
- Response validation and processing

#### **Document Parsing (`src/parsing/`)**
- `BaseParser` - Abstract parser interface
- `DocumentParser` - Concrete implementation using unstructured.io
- Support for PDF, DOCX, DOC, TXT, Excel files

#### **DSPy AI Logic (`src/dspy_logic/`)**
- `JurisdictionClassification` - Signature for jurisdiction analysis
- `CounterpartyClassification` - Signature for counterparty coding
- `DocumentAnalysisModule` - Complete analysis pipeline

#### **S3 Integration (`src/utils/s3_handler.py`)**
- Document upload/download
- Analysis results storage
- Training data management

### **Configuration**
- Environment-based configuration
- LLM API settings
- S3 bucket configuration
- Application parameters

## 🚀 Getting Started

1. **Setup Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Settings**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run Demo**
   ```bash
   python demo.py
   ```

4. **Start Application**
   ```bash
   ./run.sh
   # or
   python main.py
   ```

## 📊 Features

- ✅ **Multi-format Document Parsing**
- ✅ **AI-Powered Classification**
- ✅ **DSPy Prompt Optimization**
- ✅ **Interactive Gradio Interface**
- ✅ **S3 Data Storage**
- ✅ **User Feedback Loop**
- ✅ **Analytics & Metrics**
- ✅ **Version Control for Prompts**

## 🎯 Usage Workflow

1. **Upload Documents** - Legal documents and counterparty codes
2. **AI Analysis** - Automatic jurisdiction and counterparty classification
3. **Review Results** - Validate and correct AI predictions
4. **Feedback Collection** - User corrections feed back into training
5. **Prompt Optimization** - DSPy optimizes prompts using validated data
6. **Continuous Improvement** - System learns and improves over time