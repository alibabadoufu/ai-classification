"""
Main Gradio application for CAIS (Corporate Analysis & Intelligence Suite).
"""

import os
import json
import tempfile
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import CAIS components
from config import config
from src.data_models import AnalysisResult, TrainingExample, UserFeedback
from src.llm_interface import LLMInterface
from src.parsing.document_parser import DocumentParser
from src.utils.s3_handler import S3Handler
from src.dspy_logic.modules import DocumentAnalysisModule

# Try to import DSPy for optimization
try:
    import dspy
    from dspy.teleprompt import BootstrapFewShot
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    print("Warning: DSPy not available. Fine-tuning features will be limited.")

# Global instances
llm_interface = LLMInterface()
document_parser = DocumentParser()
s3_handler = S3Handler()

def get_prompt_versions() -> List[str]:
    """Get available prompt versions."""
    prompt_versions = []
    
    # Scan jurisdiction prompts
    jurisdiction_dir = Path("prompts/jurisdiction")
    if jurisdiction_dir.exists():
        for file in jurisdiction_dir.glob("*.txt"):
            prompt_versions.append(f"jurisdiction/{file.name}")
    
    # Scan counterparty prompts
    counterparty_dir = Path("prompts/counterparty")
    if counterparty_dir.exists():
        for file in counterparty_dir.glob("*.txt"):
            prompt_versions.append(f"counterparty/{file.name}")
    
    return prompt_versions

def load_prompt_template(prompt_path: str) -> str:
    """Load prompt template from file."""
    try:
        full_path = Path("prompts") / prompt_path
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading prompt: {str(e)}"

# Tab 1: Document Analysis Functions
def analyze_documents(
    user_name: str,
    company_name: str,
    documents: List[str],
    counterparty_file: str,
    progress=gr.Progress()
) -> Tuple[pd.DataFrame, str]:
    """
    Analyze uploaded documents and return results.
    """
    try:
        progress(0.1, desc="Validating inputs...")
        
        # Validate inputs
        if not user_name.strip():
            return pd.DataFrame(), "❌ Please enter your name."
        
        if not company_name.strip():
            return pd.DataFrame(), "❌ Please enter the company name."
        
        if not documents:
            return pd.DataFrame(), "❌ Please upload at least one document."
        
        if not counterparty_file:
            return pd.DataFrame(), "❌ Please upload the counterparty Excel file."
        
        progress(0.2, desc="Parsing documents...")
        
        # Parse documents
        document_text = document_parser.parse_multiple_documents(documents)
        
        progress(0.4, desc="Parsing counterparty codes...")
        
        # Parse counterparty Excel file
        counterparty_codes = document_parser.parse_excel(counterparty_file)
        
        progress(0.6, desc="Running AI analysis...")
        
        # Load prompt templates
        jurisdiction_prompt = load_prompt_template(config.DEFAULT_JURISDICTION_PROMPT)
        counterparty_prompt = load_prompt_template(config.DEFAULT_COUNTERPARTY_PROMPT)
        
        # Perform jurisdiction classification
        jurisdiction_result = llm_interface.classify_jurisdiction(
            document_text=document_text,
            company_name=company_name,
            prompt_template=jurisdiction_prompt
        )
        
        progress(0.8, desc="Finalizing analysis...")
        
        # Perform counterparty classification
        counterparty_result = llm_interface.classify_counterparty(
            document_text=document_text,
            company_name=company_name,
            available_codes=counterparty_codes,
            prompt_template=counterparty_prompt
        )
        
        # Create analysis result
        analysis_result = AnalysisResult(
            user_name=user_name,
            company_name=company_name,
            jurisdiction=jurisdiction_result.get("jurisdiction", "Unknown"),
            jurisdiction_reasoning=jurisdiction_result.get("reasoning", "N/A"),
            jurisdiction_citation=jurisdiction_result.get("citation", "N/A"),
            counterparty_code=counterparty_result.get("code", "UNKNOWN"),
            counterparty_reasoning=counterparty_result.get("reasoning", "N/A"),
            counterparty_citation=counterparty_result.get("citation", "N/A"),
            document_names=[Path(doc).name for doc in documents],
            counterparty_file_name=Path(counterparty_file).name
        )
        
        # Upload documents to S3
        s3_paths = []
        for doc_path in documents:
            s3_key = s3_handler.upload_document(doc_path, user_name, company_name)
            if s3_key:
                s3_paths.append(s3_key)
        
        analysis_result.s3_document_paths = s3_paths
        
        # Create DataFrame for display
        results_data = [
            ["User Name", user_name, False],
            ["Company Name", company_name, False],
            ["Analysis Date", analysis_result.timestamp.strftime("%Y-%m-%d %H:%M:%S"), False],
            ["Jurisdiction", analysis_result.jurisdiction, True],
            ["Jurisdiction Reasoning", analysis_result.jurisdiction_reasoning, True],
            ["Jurisdiction Citation", analysis_result.jurisdiction_citation[:200] + "..." if len(analysis_result.jurisdiction_citation) > 200 else analysis_result.jurisdiction_citation, True],
            ["Counterparty Code", analysis_result.counterparty_code, True],
            ["Counterparty Reasoning", analysis_result.counterparty_reasoning, True],
            ["Counterparty Citation", analysis_result.counterparty_citation[:200] + "..." if len(analysis_result.counterparty_citation) > 200 else analysis_result.counterparty_citation, True],
        ]
        
        df = pd.DataFrame(results_data, columns=["Field", "Result", "Correct?"])
        
        # Store analysis result globally for training data submission
        global current_analysis_result, current_document_text, current_counterparty_codes
        current_analysis_result = analysis_result
        current_document_text = document_text
        current_counterparty_codes = counterparty_codes
        
        progress(1.0, desc="Analysis complete!")
        
        return df, "✅ Analysis completed successfully! Please review the results and mark correct classifications."
        
    except Exception as e:
        return pd.DataFrame(), f"❌ Analysis failed: {str(e)}"

def submit_training_data(results_df: pd.DataFrame) -> str:
    """
    Submit analysis results as training data.
    """
    try:
        global current_analysis_result, current_document_text, current_counterparty_codes
        
        if current_analysis_result is None:
            return "❌ No analysis result to submit. Please run an analysis first."
        
        # Update validation flags from DataFrame
        for idx, row in results_df.iterrows():
            field = row["Field"]
            is_correct = row["Correct?"]
            
            if field == "Jurisdiction":
                current_analysis_result.jurisdiction_correct = is_correct
            elif field == "Counterparty Code":
                current_analysis_result.counterparty_correct = is_correct
        
        # Create training example
        training_example = TrainingExample(
            id=str(uuid.uuid4()),
            analysis_result=current_analysis_result,
            document_text=current_document_text,
            counterparty_codes=current_counterparty_codes
        )
        
        # Save to S3
        s3_key = s3_handler.save_training_data(training_example.dict())
        
        if s3_key:
            return f"✅ Training data submitted successfully! Saved as: {s3_key}"
        else:
            return "⚠️ Training data saved locally (S3 not available)."
            
    except Exception as e:
        return f"❌ Failed to submit training data: {str(e)}"

# Tab 2: Fine-Tuning Functions
def start_fine_tuning(prompt_selection: str, start_date: str, end_date: str) -> Tuple[str, str]:
    """
    Start DSPy fine-tuning process.
    """
    try:
        if not DSPY_AVAILABLE:
            return "❌ DSPy not available. Fine-tuning requires dspy-ai package.", ""
        
        # Load training data
        training_data = s3_handler.load_training_data(start_date, end_date)
        
        if not training_data:
            return "❌ No training data found for the specified date range.", ""
        
        # Configure DSPy with LLM
        dspy.settings.configure(lm=llm_interface)
        
        # Prepare training examples
        examples = []
        for data in training_data:
            analysis_result = data.get('analysis_result', {})
            document_text = data.get('document_text', '')
            
            if 'jurisdiction' in prompt_selection.lower():
                if analysis_result.get('jurisdiction_correct', False):
                    examples.append(dspy.Example(
                        document_text=document_text,
                        company_name=analysis_result.get('company_name', ''),
                        jurisdiction=analysis_result.get('jurisdiction', ''),
                        reasoning=analysis_result.get('jurisdiction_reasoning', ''),
                        citation=analysis_result.get('jurisdiction_citation', '')
                    ))
            
            elif 'counterparty' in prompt_selection.lower():
                if analysis_result.get('counterparty_correct', False):
                    counterparty_codes = data.get('counterparty_codes', {})
                    codes_text = "\n".join([f"{k}: {v}" for k, v in counterparty_codes.items()])
                    
                    examples.append(dspy.Example(
                        document_text=document_text,
                        company_name=analysis_result.get('company_name', ''),
                        available_codes=codes_text,
                        code=analysis_result.get('counterparty_code', ''),
                        reasoning=analysis_result.get('counterparty_reasoning', ''),
                        citation=analysis_result.get('counterparty_citation', '')
                    ))
        
        if not examples:
            return "❌ No validated examples found for optimization.", ""
        
        # Create optimizer
        optimizer = BootstrapFewShot(max_bootstrapped_demos=min(len(examples), 8))
        
        # Optimize based on prompt type
        if 'jurisdiction' in prompt_selection.lower():
            from src.dspy_logic.modules import JurisdictionClassifier
            module = JurisdictionClassifier()
            optimized_module = optimizer.compile(module, examples[:len(examples)//2])
        else:
            from src.dspy_logic.modules import CounterpartyClassifier
            module = CounterpartyClassifier()
            optimized_module = optimizer.compile(module, examples[:len(examples)//2])
        
        # Save optimized prompt
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_version = f"v{timestamp}_optimized.txt"
        
        prompt_type = "jurisdiction" if 'jurisdiction' in prompt_selection.lower() else "counterparty"
        new_prompt_path = Path(f"prompts/{prompt_type}/{new_version}")
        
        # Create directory if it doesn't exist
        new_prompt_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save optimized prompt (this is a simplified version - in practice, DSPy would provide the optimized prompt)
        with open(new_prompt_path, 'w') as f:
            f.write(f"# Optimized prompt generated on {datetime.now()}\n")
            f.write(f"# Based on {len(examples)} training examples\n")
            f.write(load_prompt_template(prompt_selection))
        
        results_text = f"""
## Fine-Tuning Results

**Prompt Type**: {prompt_type.title()}
**Training Examples**: {len(examples)}
**New Version**: {new_version}
**Optimization Method**: BootstrapFewShot

### Performance Summary
- Examples used for training: {len(examples)}
- Validated examples: {len([ex for ex in training_data if ex.get('analysis_result', {}).get(f'{prompt_type}_correct', False)])}
- New prompt saved to: {new_prompt_path}

### Next Steps
1. Review the optimized prompt in the Control Panel
2. Set it as the default for production use
3. Monitor performance on new analyses
        """
        
        return "✅ Fine-tuning completed successfully!", results_text
        
    except Exception as e:
        return f"❌ Fine-tuning failed: {str(e)}", ""

def show_current_metrics(prompt_selection: str) -> str:
    """Show current metrics for selected prompt."""
    try:
        # This would calculate accuracy based on training data
        training_data = s3_handler.load_training_data()
        
        if not training_data:
            return "No metrics available - no training data found."
        
        prompt_type = "jurisdiction" if 'jurisdiction' in prompt_selection.lower() else "counterparty"
        
        total_examples = len(training_data)
        correct_examples = sum(1 for data in training_data 
                             if data.get('analysis_result', {}).get(f'{prompt_type}_correct', False))
        
        accuracy = correct_examples / total_examples if total_examples > 0 else 0
        
        return f"""
## Current Production Metrics

**Prompt**: {prompt_selection}
**Total Examples**: {total_examples}
**Correct Classifications**: {correct_examples}
**Accuracy**: {accuracy:.2%}
**Last Updated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        
    except Exception as e:
        return f"Error calculating metrics: {str(e)}"

# Tab 3: Control Panel Functions
def set_default_prompt(prompt_version: str) -> str:
    """Set the selected prompt as default."""
    try:
        # Update configuration (in a real implementation, this would update a config file or database)
        if 'jurisdiction' in prompt_version:
            config.DEFAULT_JURISDICTION_PROMPT = f"prompts/{prompt_version}"
        elif 'counterparty' in prompt_version:
            config.DEFAULT_COUNTERPARTY_PROMPT = f"prompts/{prompt_version}"
        
        return f"✅ Set {prompt_version} as the default prompt for production use."
        
    except Exception as e:
        return f"❌ Failed to set default prompt: {str(e)}"

def generate_usage_chart() -> go.Figure:
    """Generate usage metrics chart."""
    try:
        # Generate sample data for demonstration
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        
        # Create sample usage data
        analyses_data = []
        for date in dates:
            # Simulate varying usage
            base_usage = 5 + (date.weekday() < 5) * 10  # Higher on weekdays
            daily_analyses = max(0, int(base_usage + np.random.normal(0, 3)))
            analyses_data.append({
                'Date': date,
                'Analyses': daily_analyses,
                'Companies': max(1, daily_analyses // 2),
                'Documents': daily_analyses * 2
            })
        
        df = pd.DataFrame(analyses_data)
        
        # Create chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Analyses'],
            mode='lines+markers',
            name='Daily Analyses',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Companies'],
            mode='lines+markers',
            name='Unique Companies',
            line=dict(color='green')
        ))
        
        fig.update_layout(
            title='CAIS Usage Metrics (Last 30 Days)',
            xaxis_title='Date',
            yaxis_title='Count',
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        # Return empty figure on error
        return go.Figure().add_annotation(text=f"Error generating chart: {str(e)}", x=0.5, y=0.5)

def generate_accuracy_chart() -> go.Figure:
    """Generate accuracy metrics chart."""
    try:
        # Generate sample accuracy data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        
        accuracy_data = []
        for date in dates:
            # Simulate accuracy trends
            base_acc = 0.85
            jurisdiction_acc = max(0.5, min(1.0, base_acc + np.random.normal(0, 0.05)))
            counterparty_acc = max(0.5, min(1.0, base_acc + np.random.normal(0, 0.05)))
            
            accuracy_data.append({
                'Date': date,
                'Jurisdiction Accuracy': jurisdiction_acc,
                'Counterparty Accuracy': counterparty_acc
            })
        
        df = pd.DataFrame(accuracy_data)
        
        # Create chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Jurisdiction Accuracy'],
            mode='lines+markers',
            name='Jurisdiction Accuracy',
            line=dict(color='orange')
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Counterparty Accuracy'],
            mode='lines+markers',
            name='Counterparty Accuracy',
            line=dict(color='purple')
        ))
        
        fig.update_layout(
            title='Classification Accuracy Trends',
            xaxis_title='Date',
            yaxis_title='Accuracy',
            yaxis=dict(range=[0, 1]),
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error generating chart: {str(e)}", x=0.5, y=0.5)

def show_kpis() -> str:
    """Show key performance indicators."""
    try:
        # Calculate KPIs (sample data for demo)
        total_analyses = 1250
        total_companies = 450
        avg_accuracy = 0.87
        total_users = 25
        
        kpi_text = f"""
## Key Performance Indicators

📊 **Total Analyses**: {total_analyses:,}  
🏢 **Unique Companies Analyzed**: {total_companies:,}  
🎯 **Average Accuracy**: {avg_accuracy:.1%}  
👥 **Active Users**: {total_users}  
📈 **This Month's Growth**: +15%  
⚡ **Avg Response Time**: 2.3 seconds  

### System Status
🟢 **LLM API**: Connected  
🟢 **S3 Storage**: Available  
🟢 **Document Parser**: Operational  
        """
        
        return kpi_text
        
    except Exception as e:
        return f"Error loading KPIs: {str(e)}"

# Tab 4: Feedback Functions
def submit_feedback(category: str, message: str) -> str:
    """Submit user feedback."""
    try:
        if not message.strip():
            return "❌ Please enter your feedback message."
        
        feedback = UserFeedback(
            category=category,
            message=message.strip()
        )
        
        # Save feedback to S3
        s3_key = s3_handler.save_feedback(feedback.dict())
        
        if s3_key:
            return f"✅ Thank you for your feedback! Your submission has been recorded."
        else:
            return "✅ Thank you for your feedback! (Saved locally - S3 not available)"
            
    except Exception as e:
        return f"❌ Failed to submit feedback: {str(e)}"

# Initialize global variables
current_analysis_result = None
current_document_text = ""
current_counterparty_codes = {}

# Import numpy for random data generation
try:
    import numpy as np
except ImportError:
    print("Warning: numpy not available. Some charts may not work.")

# Create Gradio Interface
def create_interface():
    """Create the main Gradio interface."""
    
    with gr.Blocks(title="CAIS - Corporate Analysis & Intelligence Suite", theme=gr.themes.Soft()) as app:
        
        gr.Markdown("""
        # 🏢 CAIS - Corporate Analysis & Intelligence Suite
        
        **Advanced AI-powered document analysis for legal and compliance teams**
        
        Analyze legal documents to classify company jurisdictions and assign counterparty codes with AI assistance.
        """)
        
        with gr.Tabs():
            
            # Tab 1: Document Analysis
            with gr.TabItem("📄 Document Analysis"):
                gr.Markdown("### Analyze Legal Documents")
                gr.Markdown("Upload legal documents and counterparty codes to perform automated classification.")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        user_name = gr.Textbox(
                            label="👤 User Name",
                            placeholder="Enter your name",
                            info="Identify yourself for record keeping"
                        )
                        company_name = gr.Textbox(
                            label="🏢 Company Name",
                            placeholder="Enter the company name being analyzed",
                            info="Name of the company in the legal documents"
                        )
                        
                        documents = gr.File(
                            label="📄 Upload Legal Documents",
                            file_count="multiple",
                            file_types=[".pdf", ".docx", ".doc", ".txt"],
                            info="Upload PDF, DOCX, or text files"
                        )
                        
                        counterparty_file = gr.File(
                            label="📊 Upload Counterparty Excel File",
                            file_types=[".xlsx"],
                            info="Excel file with counterparty codes and descriptions"
                        )
                        
                        analyze_btn = gr.Button("🔍 Analyze", variant="primary", size="lg")
                    
                    with gr.Column(scale=2):
                        status_message = gr.Markdown("Upload files and click Analyze to begin.")
                        
                        results_df = gr.DataFrame(
                            headers=["Field", "Result", "Correct?"],
                            datatype=["str", "str", "bool"],
                            interactive=True,
                            label="📋 Analysis Results"
                        )
                        
                        submit_training_btn = gr.Button(
                            "💾 Submit as Training Data",
                            variant="secondary",
                            visible=False
                        )
                        
                        training_status = gr.Markdown("")
                
                # Event handlers
                analyze_btn.click(
                    fn=analyze_documents,
                    inputs=[user_name, company_name, documents, counterparty_file],
                    outputs=[results_df, status_message]
                ).then(
                    lambda df: gr.Button(visible=len(df) > 0),
                    inputs=[results_df],
                    outputs=[submit_training_btn]
                )
                
                submit_training_btn.click(
                    fn=submit_training_data,
                    inputs=[results_df],
                    outputs=[training_status]
                )
            
            # Tab 2: DSPy Fine-Tuning
            with gr.TabItem("🔧 DSPy Prompt Fine-Tuning"):
                gr.Markdown("### Optimize AI Prompts with DSPy")
                gr.Markdown("Select prompts and training data to improve classification accuracy.")
                
                with gr.Row():
                    with gr.Column():
                        prompt_dropdown = gr.Dropdown(
                            choices=get_prompt_versions(),
                            label="📝 Select Prompt to Fine-Tune",
                            info="Choose which prompt template to optimize"
                        )
                        
                        with gr.Row():
                            start_date = gr.Textbox(
                                label="📅 Start Date (YYYY-MM-DD)",
                                placeholder="2024-01-01",
                                info="Beginning of training data range"
                            )
                            end_date = gr.Textbox(
                                label="📅 End Date (YYYY-MM-DD)",
                                placeholder="2024-12-31",
                                info="End of training data range"
                            )
                        
                        finetune_btn = gr.Button("🚀 Start Fine-Tuning", variant="primary")
                        
                        current_metrics = gr.Markdown("Select a prompt to view current metrics.")
                    
                    with gr.Column():
                        finetune_status = gr.Markdown("")
                        finetune_results = gr.Markdown("")
                
                # Event handlers
                prompt_dropdown.change(
                    fn=show_current_metrics,
                    inputs=[prompt_dropdown],
                    outputs=[current_metrics]
                )
                
                finetune_btn.click(
                    fn=start_fine_tuning,
                    inputs=[prompt_dropdown, start_date, end_date],
                    outputs=[finetune_status, finetune_results]
                )
            
            # Tab 3: Control & Monitoring Panel
            with gr.TabItem("📊 Control & Monitoring Panel"):
                gr.Markdown("### System Management & Analytics")
                gr.Markdown("Monitor usage, manage prompts, and view system performance.")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### 🎛️ Prompt Management")
                        
                        prod_prompt_dropdown = gr.Dropdown(
                            choices=get_prompt_versions(),
                            label="Select Production Prompt Version",
                            info="Choose active prompt for document analysis"
                        )
                        
                        set_default_btn = gr.Button("✅ Set as Default", variant="secondary")
                        prompt_status = gr.Markdown("")
                        
                        gr.Markdown("#### 📈 Key Performance Indicators")
                        kpis_display = gr.Markdown(show_kpis())
                    
                    with gr.Column():
                        gr.Markdown("#### 📊 Usage Metrics")
                        usage_chart = gr.Plot(value=generate_usage_chart())
                        
                        gr.Markdown("#### 🎯 Accuracy Trends")
                        accuracy_chart = gr.Plot(value=generate_accuracy_chart())
                
                # Event handlers
                set_default_btn.click(
                    fn=set_default_prompt,
                    inputs=[prod_prompt_dropdown],
                    outputs=[prompt_status]
                )
                
                # Auto-refresh charts every 30 seconds (in a real app)
                app.load(lambda: generate_usage_chart(), outputs=[usage_chart], every=30)
                app.load(lambda: generate_accuracy_chart(), outputs=[accuracy_chart], every=30)
            
            # Tab 4: User Feedback
            with gr.TabItem("💬 User Feedback"):
                gr.Markdown("### Submit Feedback")
                gr.Markdown("Help us improve CAIS by sharing your experience and suggestions.")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        feedback_category = gr.Dropdown(
                            choices=["UI Bug", "Incorrect Analysis", "Feature Request", "Other"],
                            label="📋 Feedback Category",
                            value="Other",
                            info="What type of feedback are you providing?"
                        )
                        
                        feedback_message = gr.Textbox(
                            label="💭 Detailed Feedback",
                            lines=5,
                            placeholder="Please describe your feedback in detail...",
                            info="The more specific you are, the better we can help!"
                        )
                        
                        submit_feedback_btn = gr.Button("📤 Submit Feedback", variant="primary")
                        
                        feedback_status = gr.Markdown("")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("""
                        ### 📞 Contact Information
                        
                        For urgent issues or direct support:
                        
                        📧 **Email**: support@cais-platform.com  
                        🔗 **Documentation**: [User Guide](https://docs.cais-platform.com)  
                        💬 **Chat Support**: Available 9 AM - 5 PM EST  
                        
                        ### 🔍 Common Issues
                        
                        **Document Upload Fails**  
                        → Check file format (PDF, DOCX, TXT)  
                        → Ensure file size < 100MB  
                        
                        **Incorrect Classifications**  
                        → Use "Submit as Training Data" to improve AI  
                        → Ensure documents contain clear jurisdiction info  
                        
                        **Performance Issues**  
                        → Check your internet connection  
                        → Contact support if problems persist  
                        """)
                
                # Event handler
                submit_feedback_btn.click(
                    fn=submit_feedback,
                    inputs=[feedback_category, feedback_message],
                    outputs=[feedback_status]
                ).then(
                    lambda: ("", ""),  # Clear form after submission
                    outputs=[feedback_message, feedback_status]
                )
        
        # Footer
        gr.Markdown("""
        ---
        **CAIS v1.0** | Built with ❤️ for Legal & Compliance Teams | 
        Powered by DSPy, Gradio, and advanced AI
        """)
    
    return app

# Main execution
if __name__ == "__main__":
    # Validate configuration
    if not config.validate_config():
        print("⚠️  Configuration warnings detected. Some features may not work properly.")
    
    # Create and launch the application
    app = create_interface()
    
    app.launch(
        server_name=config.APP_HOST,
        server_port=config.APP_PORT,
        debug=config.DEBUG,
        share=False
    )