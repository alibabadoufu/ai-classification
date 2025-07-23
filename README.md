# 🏢 CAIS - Corporate Analysis & Intelligence Suite

**Advanced AI-powered document analysis platform for legal and compliance teams**

CAIS is a comprehensive Python-based web application that leverages cutting-edge AI to analyze legal documents, classify company jurisdictions, and assign counterparty codes. Built with DSPy for prompt optimization, Gradio for the user interface, and designed to work with in-house OpenAI-compatible LLMs.

## ✨ Features

### 📄 Document Analysis
- **Multi-format Support**: Parse PDF, DOCX, DOC, and TXT files
- **AI-Powered Classification**: Automatic jurisdiction and counterparty code assignment
- **Interactive Results**: Review and validate AI classifications
- **Batch Processing**: Analyze multiple documents simultaneously

### 🔧 DSPy Prompt Optimization
- **Automated Fine-tuning**: Optimize prompts using validated training data
- **Performance Tracking**: Monitor accuracy and improvement metrics
- **Version Management**: Track and compare different prompt versions

### 📊 Control & Monitoring
- **Usage Analytics**: Track platform usage and performance metrics
- **Prompt Management**: Set active prompts for production use
- **Real-time Dashboards**: Monitor system health and accuracy trends

### 💬 User Feedback System
- **Feedback Collection**: Gather user input for continuous improvement
- **Issue Tracking**: Categorized feedback for better support

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI-compatible LLM API endpoint
- AWS S3 bucket (optional, for production use)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cais
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the interface**
   Open your browser to `http://localhost:7860`

## ⚙️ Configuration

### Required Environment Variables

```bash
# LLM API Configuration
LLM_API_URL=http://your-llm-endpoint/v1
LLM_API_KEY=your-api-key

# S3 Configuration (optional)
S3_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

### Optional Configuration

```bash
# Application Settings
APP_HOST=0.0.0.0
APP_PORT=7860
DEBUG=false

# Prompt Settings
ACTIVE_PROMPT_VERSION=v1_base
```

## 📁 Project Structure

```
cais/
│
├── main.py                 # Main Gradio application
├── requirements.txt        # Project dependencies
├── config.py              # Configuration management
├── .env.example           # Environment variables template
│
├── src/
│   ├── __init__.py
│   ├── llm_interface.py    # LLM API interface
│   ├── data_models.py      # Pydantic data models
│   │
│   ├── parsing/
│   │   ├── __init__.py
│   │   ├── base_parser.py  # Abstract parser base class
│   │   └── document_parser.py # Document parsing implementation
│   │
│   ├── dspy_logic/
│   │   ├── __init__.py
│   │   ├── signatures.py   # DSPy signatures
│   │   └── modules.py      # DSPy modules and pipelines
│   │
│   └── utils/
│       ├── __init__.py
│       └── s3_handler.py   # S3 operations
│
└── prompts/
    ├── jurisdiction/
    │   └── v1_base.txt
    └── counterparty/
        └── v1_base.txt
```

## 🎯 Usage Guide

### 1. Document Analysis

1. **Enter User Information**
   - Provide your name for record keeping
   - Enter the company name being analyzed

2. **Upload Documents**
   - Upload one or more legal documents (PDF, DOCX, TXT)
   - Upload counterparty Excel file with codes and descriptions

3. **Review Results**
   - Check AI classifications for accuracy
   - Mark correct/incorrect classifications
   - Submit validated results as training data

### 2. Prompt Optimization

1. **Select Prompt Type**
   - Choose jurisdiction or counterparty classification prompt
   - Review current performance metrics

2. **Set Training Data Range**
   - Specify date range for training examples
   - Ensure sufficient validated data exists

3. **Run Optimization**
   - DSPy will optimize prompts using BootstrapFewShot
   - Review optimization results and metrics

### 3. System Management

1. **Prompt Management**
   - View available prompt versions
   - Set active prompts for production use

2. **Monitor Performance**
   - Track usage metrics and trends
   - Monitor classification accuracy over time

### 4. Feedback Submission

1. **Categorize Feedback**
   - Select appropriate feedback category
   - Provide detailed description

2. **Submit for Review**
   - Feedback is stored for analysis
   - Use for continuous platform improvement

## 🔧 Technical Details

### AI Components

- **DSPy Framework**: Prompt optimization and management
- **LLM Integration**: OpenAI-compatible API support
- **Classification Pipeline**: Dual-task architecture for jurisdiction and counterparty analysis

### Document Processing

- **unstructured.io**: Advanced document parsing
- **Multi-format Support**: PDF, DOCX, DOC, TXT
- **Excel Integration**: Counterparty code mapping

### Data Management

- **S3 Integration**: Secure document and data storage
- **Training Data Pipeline**: Automated collection and management
- **Version Control**: Prompt and model versioning

## 🛠️ Development

### Adding New Document Types

1. Extend `BaseParser` in `src/parsing/base_parser.py`
2. Implement parsing logic in `DocumentParser`
3. Update supported formats list

### Custom DSPy Modules

1. Define new signatures in `src/dspy_logic/signatures.py`
2. Implement modules in `src/dspy_logic/modules.py`
3. Integrate with main analysis pipeline

### Adding New Features

1. Create new Gradio tab in `main.py`
2. Implement backend logic in appropriate `src/` module
3. Update data models if needed

## 🐛 Troubleshooting

### Common Issues

**Document Upload Fails**
- Check file format compatibility
- Ensure file size is reasonable (< 100MB)
- Verify unstructured.io installation

**LLM API Errors**
- Verify API endpoint URL and key
- Check network connectivity
- Review API rate limits

**S3 Connection Issues**
- Validate AWS credentials
- Check bucket permissions
- Verify region settings

**DSPy Optimization Fails**
- Ensure sufficient training data
- Check DSPy installation
- Review prompt format compatibility

### Performance Optimization

- Use smaller document batches for faster processing
- Configure appropriate LLM timeout settings
- Monitor S3 transfer speeds

## 📚 API Reference

### Core Classes

- `LLMInterface`: Handles all LLM API interactions
- `DocumentParser`: Processes various document formats
- `S3Handler`: Manages cloud storage operations
- `DocumentAnalysisModule`: Main DSPy analysis pipeline

### Data Models

- `AnalysisResult`: Complete analysis output structure
- `TrainingExample`: Training data format
- `UserFeedback`: Feedback submission format

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- 📧 Email: support@cais-platform.com
- 📖 Documentation: [User Guide](https://docs.cais-platform.com)
- 💬 Issues: Use GitHub Issues for bug reports

---

**CAIS v1.0** | Built with ❤️ for Legal & Compliance Teams | Powered by DSPy, Gradio, and advanced AI