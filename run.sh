#!/bin/bash

# CAIS Platform Startup Script

echo "🏢 Starting CAIS - Corporate Analysis & Intelligence Suite"
echo "=========================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before starting the server."
    echo "   Key settings to configure:"
    echo "   - LLM_API_URL: Your OpenAI-compatible API endpoint"
    echo "   - LLM_API_KEY: Your API key"
    echo "   - S3_BUCKET_NAME: Your S3 bucket name"
    echo "   - AWS credentials if using S3"
    echo ""
    echo "💡 For local testing, you can leave default values in some cases."
    echo ""
    read -p "Press Enter to continue with current .env settings or Ctrl+C to exit and edit..."
fi

# Check if required dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import gradio, dspy, boto3" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo "🚀 Starting CAIS platform..."
echo "📊 Access the application at: http://localhost:7860"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python main.py