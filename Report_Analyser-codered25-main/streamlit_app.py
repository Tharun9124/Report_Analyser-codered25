import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import base64
from src.agents.medical_llm_agent import MedicalLLMAgent
from src.agents.report_generation_agent import ReportGenerationAgent
from src.database.db_manager import DatabaseManager
import json
import google.generativeai as genai
from typing import List

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_page_style():
    # Add background image and gradient overlay
    st.markdown('''
        <style>
            [data-testid="stAppViewContainer"] {
                background: linear-gradient(rgba(44, 62, 80, 0.92), rgba(52, 152, 219, 0.92)), 
                            url("https://wallpapercave.com/wp/wp7109751.jpg");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }

            [data-testid="stHeader"] {
                background-color: transparent;
            }

            [data-testid="stToolbar"] {
                background-color: transparent;
            }

            [data-testid="stSidebar"] {
                background-color: #2c3e50;
                width: 16rem !important;
            }
            
            [data-testid="stSidebar"] > div {
                width: 16rem !important;
            }

            /* Style text elements for better readability */
            .block-container p, .block-container li {
                color: #1a1a1a !important;
                font-weight: 500 !important;
                text-shadow: 0 0 1px rgba(255, 255, 255, 0.3);
            }

            .block-container {
                padding: 2rem 3rem !important;
                max-width: 1200px;
                margin: auto;
                background: rgba(255, 255, 255, 0.6) !important;
                border-radius: 12px;
                border: 2px solid transparent;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }

            .block-container:hover {
                border-color: #3498db;
                transform: scale(1.02);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            }

            /* Make dataframes and metrics more visible */
            [data-testid="stDataFrame"], [data-testid="stMetricValue"] {
                background: rgba(255, 255, 255, 0.85) !important;
                padding: 1rem;
                border-radius: 8px;
                border: 2px solid transparent;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(5px);
                -webkit-backdrop-filter: blur(5px);
                transition: all 0.3s ease;
            }

            [data-testid="stDataFrame"]:hover, [data-testid="stMetricValue"]:hover {
                border-color: #2c3e50;
                transform: scale(1.02);
                box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
            }

            /* Style file uploader for transparency */
            .stFileUploader {
                background: rgba(255, 255, 255, 0.75) !important;
                padding: 1rem;
                border-radius: 8px;
                border: 2px dashed rgba(44, 62, 80, 0.5);
                backdrop-filter: blur(5px);
                -webkit-backdrop-filter: blur(5px);
                transition: all 0.3s ease;
            }

            .stFileUploader:hover {
                border-color: #2ecc71;
                transform: scale(1.02);
                box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
            }

            /* Style buttons with transparency */
            .stButton > button {
                background: rgba(44, 62, 80, 0.9) !important;
                color: white !important;
                border: 2px solid transparent !important;
                padding: 0.5rem 1rem !important;
                border-radius: 6px !important;
                transition: all 0.3s ease !important;
                backdrop-filter: blur(5px);
                -webkit-backdrop-filter: blur(5px);
            }

            .stButton > button:hover {
                border-color: #3498db !important;
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }

            /* Style select boxes with transparency */
            .stSelectbox > div > div {
                background: rgba(255, 255, 255, 0.8) !important;
                border-radius: 6px;
                border: 2px solid transparent;
                transition: all 0.3s ease;
            }

            .stSelectbox > div > div:hover {
                border-color: #9b59b6;
                transform: scale(1.02);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }

            /* Style headings */
            h1, h2, h3 {
                color: #2c3e50 !important;
            }

            /* Style main content elements */
            .stMarkdown, .stButton, .stSelectbox, .stFileUploader {
                position: relative;
                z-index: 1;
            }

            /* Style buttons */
            .stButton button {
                background: #2c3e50;
                color: white;
                border-radius: 4px;
                border: none;
                padding: 0.5rem 1rem;
                transition: all 0.2s ease;
            }
            
            .stButton button:hover {
                background: #34495e;
            }

            /* File uploader styling */
            [data-testid="stFileUploader"] {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 1rem;
            }

            /* Headers styling */
            h1 {
                color: #2c3e50 !important;
                font-size: 2.2em !important;
                font-weight: 600 !important;
                margin: 0 0 1.5rem 0 !important;
                padding: 0 !important;
            }

            h2 {
                color: #34495e !important;
                font-size: 1.8em !important;
                font-weight: 500 !important;
                margin: 1rem 0 !important;
            }

            h3 {
                color: #2c3e50 !important;
                font-size: 1.4em !important;
                font-weight: 500 !important;
            }

            /* Metric styling */
            [data-testid="stMetricValue"] {
                color: #2c3e50 !important;
                font-weight: 600 !important;
            }

            /* DataFrame styling */
            .dataframe {
                border: 1px solid #dee2e6 !important;
                border-radius: 4px;
                overflow: hidden;
            }

            .dataframe thead th {
                background: #2c3e50 !important;
                color: white !important;
                padding: 0.75rem !important;
            }

            .dataframe tbody tr:nth-child(even) {
                background: #f8f9fa;
            }

            /* Plot styling */
            [data-testid="stImage"] {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 0.5rem;
            }

            /* Custom divider */
            hr {
                border: none;
                border-top: 1px solid #dee2e6;
                margin: 1.5rem 0;
            }

            /* Input widgets styling */
            .stSelectbox > div,
            .stTextInput > div,
            .stTextArea > div {
                border: 1px solid #dee2e6 !important;
                border-radius: 4px !important;
            }

            /* Remove extra spacing */
            .block-container {
                padding-top: 1rem !important;
            }

            .element-container {
                margin: 0.5rem 0 !important;
            }

            /* Clean spacing */
            .css-1544g2n {
                padding: 1rem !important;
            }

            .css-1v3fvcr {
                padding: 1rem 0 !important;
            }

            /* Metric Box Styling */
            .metric-box {
                background: white;
                border: 2px solid #2c3e50;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                transition: all 0.3s ease;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                margin: 10px 0;
            }

            .metric-box:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 12px rgba(44, 62, 80, 0.2);
                border-color: #3498db;
            }

            .metric-value {
                font-size: 28px;
                font-weight: 700;
                color: #2c3e50;
                margin-bottom: 8px;
            }

            .metric-label {
                font-size: 14px;
                color: #7f8c8d;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .logo-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 0;
            }

            .logo-title {
                color: white;
                font-size: 28px;
                font-weight: 800;
                margin-bottom: 15px;
                letter-spacing: 1px;
            }

            .logo-image {
                width: 130px;
                height: 130px;
                border-radius: 50%;
                object-fit: cover;
                border: 3px solid white;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                margin-bottom: 0;
            }

            /* Remove extra spacing from navigation */
            .st-emotion-cache-16txtl3 {
                padding-top: 0 !important;
                margin-bottom: 7rem !important;
                width: 16rem !important;
            }

            /* Adjust radio button spacing */
            .st-emotion-cache-1qg05tj {
                padding-top: 1rem !important;
                width: 16rem !important;
            }

            .social-links {
                position: fixed;
                bottom: 0;
                width: 16rem;
                background: #2c3e50;
                padding: 0.7rem;
                text-align: center;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                left: 0;
                z-index: 1000;
            }

            .social-links h4 {
                color: white;
                margin-bottom: 0.3rem;
                font-size: 0.9rem;
                font-weight: 600;
            }

            .social-icons {
                display: flex;
                justify-content: center;
                gap: 1.2rem;
                margin: 0.3rem 0;
            }

            .social-icon {
                color: white;
                font-size: 1.2rem;
                transition: color 0.3s ease;
                text-decoration: none;
            }

            .social-icon:hover {
                color: #3498db;
            }

            .contact-text {
                color: rgba(255, 255, 255, 0.7);
                font-size: 0.7rem;
                margin-top: 0.3rem;
            }
        </style>

        <script>
            // Add main class to the main content area
            document.querySelector('.main').classList.add('main');
        </script>
    ''', unsafe_allow_html=True)

    # Add class to main content area
    st.markdown('''
        <style>
            .main .block-container {
                max-width: 1200px;
                margin: auto;
            }
        </style>
    ''', unsafe_allow_html=True)

# Initialize agents
llm_agent = MedicalLLMAgent()
report_agent = ReportGenerationAgent()

# Initialize database
db = DatabaseManager()

# Set page config
st.set_page_config(
    page_title="NEON ANALYST",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# Apply custom styling
set_page_style()

# Add logo and title in sidebar
with st.sidebar:
    st.markdown("""
        <div class="logo-container">
            <div class="logo-title">NEON ANALYST</div>
            <img src="https://th.bing.com/th/id/OIP.yaW77VvL2sxxkU_fDiYO2QHaHa?w=626&h=626&rs=1&pid=ImgDetMain" 
                class="logo-image" 
                alt="Medical Logo">
        </div>
    """, unsafe_allow_html=True)

# Initialize session state
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize Gemini API
GEMINI_API_KEY = "AIzaSyAFE1w3E3ui6EKq3duWq6YkceeBFdXm4g0"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_gemini_response(question: str, chat_history: List[str]) -> str:
    try:
        # Prepare context from chat history
        context = "\n".join(chat_history[-5:])  # Get last 5 messages for context
        
        # Prepare the prompt
        prompt = f"""You are a medical report analysis assistant. You help users understand their medical reports and provide insights.
        Previous conversation context:
        {context}
        
        User question: {question}
        
        Please provide a clear, professional response."""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def show_upload_and_analyze():
    st.title("Medical Data Analysis")
    
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <p style='font-size: 1.2em; color: #7f8c8d;'>
                Upload your medical data for comprehensive analysis powered by advanced AI
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # File upload section with better styling
    uploaded_file = st.file_uploader("Upload Medical Data CSV", type=['csv'])
    
    if uploaded_file:
        try:
            # Save uploaded file
            save_dir = "uploads"
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.current_file = file_path
            
            # Read and display data
            df = pd.read_csv(file_path)
            st.session_state.df = df
            
            # Display data overview with improved metrics
            st.markdown("<h2 style='text-align: center;'>Data Overview</h2>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            
            metrics = [
                {"value": len(df), "label": "Total Records"},
                {"value": len(df.columns), "label": "Features"},
                {"value": len(df.select_dtypes(include=['int64', 'float64']).columns), "label": "Numeric Columns"},
                {"value": df.isnull().sum().sum(), "label": "Missing Values"}
            ]
            
            for col, metric in zip([col1, col2, col3, col4], metrics):
                with col:
                    st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-value">{metric['value']}</div>
                            <div class="metric-label">{metric['label']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<h3>Data Preview</h3>", unsafe_allow_html=True)
            st.dataframe(df.head(), use_container_width=True)
            
            # Analysis section with improved UI
            st.markdown("<h2 style='text-align: center;'>AI Analysis</h2>", unsafe_allow_html=True)
            
            analysis_type = st.selectbox(
                "Select Analysis Type",
                ["Basic Analysis", "Detailed Analysis with Predictions"],
                help="Choose the type of analysis to perform on your data"
            )
            
            if st.button("Run Analysis", type="primary"):
                with st.spinner("AI is analyzing your data..."):
                    # Run analysis
                    analysis_results = llm_agent.analyze(df, analysis_type)
                    st.session_state.analysis_results = analysis_results
                    
                    if "error" in analysis_results:
                        st.error(f"Analysis Error: {analysis_results['error']}")
                        return
                    
                    # Display results in tabs with improved styling
                    tab1, tab2, tab3 = st.tabs(["Insights", "Visualizations", "Predictions"])
                    
                    with tab1:
                        if "summary" in analysis_results:
                            st.markdown("""
                                <div class="insight-card">
                                    <h3>Summary</h3>
                                    {}
                                </div>
                            """.format(analysis_results["summary"]), unsafe_allow_html=True)
                        
                        if "insights" in analysis_results:
                            st.markdown("<h3>Key Insights</h3>", unsafe_allow_html=True)
                            for insight in analysis_results["insights"]:
                                st.markdown(f"""
                                    <div class="insight-card">
                                        • {insight}
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        if "recommendations" in analysis_results:
                            st.markdown("<h3>Recommendations</h3>", unsafe_allow_html=True)
                            for rec in analysis_results["recommendations"]:
                                st.markdown(f"""
                                    <div class="insight-card">
                                        • {rec}
                                    </div>
                                """, unsafe_allow_html=True)
                    
                    with tab2:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### Distribution Analysis")
                            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                            selected_col = st.selectbox("Select feature", numeric_cols)
                            fig, ax = plt.subplots(figsize=(10, 6))
                            if df[selected_col].nunique() > 10:
                                sns.histplot(data=df, x=selected_col, kde=True, ax=ax)
                            else:
                                sns.countplot(data=df, x=selected_col, ax=ax)
                            plt.title(f'Distribution of {selected_col}')
                            st.pyplot(fig)
                            plt.close()
                        
                        with col2:
                            st.markdown("#### Correlation Analysis")
                            numeric_df = df.select_dtypes(include=['int64', 'float64'])
                            fig, ax = plt.subplots(figsize=(10, 8))
                            sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
                            plt.title('Feature Correlations')
                            st.pyplot(fig)
                            plt.close()
                    
                    with tab3:
                        if "predictions" in analysis_results:
                            st.markdown("### Prediction Results")
                            accuracy = analysis_results.get('accuracy', 'N/A')
                            if accuracy != 'N/A':
                                st.markdown(f"Model Accuracy: {accuracy:.2%}")
                            
                            if "confusion_matrix" in analysis_results:
                                st.markdown("#### Confusion Matrix")
                                fig, ax = plt.subplots(figsize=(8, 6))
                                sns.heatmap(analysis_results["confusion_matrix"], 
                                          annot=True, fmt='d', cmap='Blues')
                                plt.title('Confusion Matrix')
                                st.pyplot(fig)
                                plt.close()
                        else:
                            st.info("No prediction results available for this analysis.")
                    
                    st.success("Analysis complete!")
                    
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

def show_report_generation():
    st.title("Report Generation")
    
    if st.session_state.current_file is None:
        st.warning("Please upload a file first in the Upload & Analyze section")
        return
        
    if st.session_state.analysis_results is None:
        st.warning("Please run analysis first in the Upload & Analyze section")
        return
    
    # Show live visualizations in dashboard
    if st.session_state.current_file:
        df = pd.read_csv(st.session_state.current_file)
        
        st.markdown("## Data Insights Dashboard")
        
        # Create tabs for different visualizations
        viz_tabs = st.tabs(["Distributions", "Correlations", "Statistics"])
        
        with viz_tabs[0]:
            st.markdown("### Distribution Analysis")
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            col1, col2 = st.columns([1, 2])
            with col1:
                selected_col = st.selectbox("Select feature", numeric_cols)
            with col2:
                fig, ax = plt.subplots(figsize=(10, 6))
                if df[selected_col].nunique() > 10:
                    sns.histplot(data=df, x=selected_col, kde=True, ax=ax)
                else:
                    sns.countplot(data=df, x=selected_col, ax=ax)
                plt.title(f'Distribution of {selected_col}')
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
        
        with viz_tabs[1]:
            st.markdown("### Correlation Analysis")
            numeric_df = df.select_dtypes(include=['int64', 'float64'])
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
            plt.title('Feature Correlation Analysis')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        
        with viz_tabs[2]:
            st.markdown("### Statistical Summary")
            st.dataframe(df.describe(), use_container_width=True)
    
    # Report generation section
    st.markdown("## Generate Report")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        report_options = st.multiselect(
            "Select Report Sections",
            ["Executive Summary", "Data Overview", "Key Insights", 
             "Visualizations", "Statistical Analysis", "Predictions", "Recommendations"],
            default=["Executive Summary", "Data Overview", "Key Insights", "Visualizations"],
            help="Choose which sections to include in your report"
        )
    
    with col2:
        report_format = st.radio(
            "Report Format",
            ["Standard", "Detailed"],
            help="Choose the level of detail for your report"
        )
    
    if st.button("Generate Report", type="primary"):
        with st.spinner("Generating comprehensive report..."):
            try:
                report_path = report_agent.generate_report(
                    data_file=st.session_state.current_file,
                    analysis_results=st.session_state.analysis_results,
                    report_type=report_format.lower()
                )
                
                st.success("Report generated successfully!")
                
                # Create a download button
                with open(report_path, "rb") as file:
                    btn = st.download_button(
                        label="Download Report",
                        data=file,
                        file_name=os.path.basename(report_path),
                        mime="application/pdf",
                        help="Click to download the generated report"
                    )
                
                # Show a preview section
                with st.expander("Report Preview", expanded=True):
                    st.info("This is a preview of the report content. Download the PDF for the full formatted report.")
                    st.markdown(f"""
                    ### Medical Data Analysis Report
                    - Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                    - File analyzed: {os.path.basename(st.session_state.current_file)}
                    - Report type: {report_format}
                    
                    #### Included Sections:
                    {', '.join(report_options)}
                    
                    #### Key Highlights:
                    - Total records analyzed: {len(st.session_state.df):,}
                    - Features analyzed: {len(st.session_state.df.columns)}
                    - Analysis depth: {report_format}
                    
                    Download the PDF to view the complete analysis with all visualizations and detailed insights.
                    """)
                    
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
                st.error("Please try again.")

def show_quick_summary():
    st.title("Quick Summary")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Medical Data", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if df is not None:
            # Basic dataset statistics
            st.markdown("### Dataset Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Features", len(df.columns))
            with col3:
                st.metric("Missing Values", df.isnull().sum().sum())
            
            # Quick insights
            st.markdown("### Quick Insights")
            
            # Generate quick summary using LLM
            analysis_results = llm_agent.analyze(df, "basic")
            
            if "error" not in analysis_results:
                # Display insights
                if "insights" in analysis_results:
                    for insight in analysis_results["insights"]:
                        st.info(insight)
                
                # Save to database
                metadata = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "file_type": uploaded_file.type
                }
                
                report_id = db.save_report(
                    filename=uploaded_file.name,
                    report_path="",  # No report file for quick summary
                    report_type="quick_summary",
                    analysis_results=analysis_results,
                    metadata=metadata
                )
                
                # Save summary
                summary_text = "\n".join(analysis_results.get("insights", []))
                db.save_quick_summary(report_id, summary_text)
                
                st.success("Summary saved to database!")
            else:
                st.error("Failed to generate summary. Please try again.")

def show_report_history():
    st.title("Report Analysis History")
    
    # Add custom CSS for better styling
    st.markdown("""
        <style>
        .history-card {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 5px solid #2980b9;
        }
        .report-title {
            color: #2c3e50;
            font-size: 1.2em;
            font-weight: bold;
        }
        .report-meta {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 1rem;
        }
        .insight-card {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border: 1px solid #e0e0e0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Get recent reports from database
    recent_reports = db.get_recent_reports(limit=10)
    
    if not recent_reports:
        st.info("No reports found in history. Start by analyzing some medical data!")
        return
    
    # Display reports in a modern card layout
    for report in recent_reports:
        st.markdown(f"""
            <div class="history-card">
                <div class="report-title">{report['filename']}</div>
                <div class="report-meta"> {report['created_at']} | {report['report_type']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("View Details"):
            if 'metadata' in report and report['metadata']:
                st.write(" **Metadata**")
                st.json(report['metadata'])
            
            # Get detailed report info
            details = db.get_report_details(report['id'])
            if details and 'analysis_results' in details:
                try:
                    # Handle both string and dict analysis results
                    if isinstance(details['analysis_results'], str):
                        analysis_results = json.loads(details['analysis_results'])
                    else:
                        analysis_results = details['analysis_results']
                    
                    if 'summary' in analysis_results:
                        st.write(" **Summary**")
                        st.markdown(f'<div class="insight-card">{analysis_results["summary"]}</div>', unsafe_allow_html=True)
                    
                    if 'insights' in analysis_results:
                        st.write(" **Key Insights**")
                        for insight in analysis_results['insights']:
                            st.markdown(f'<div class="insight-card">• {insight}</div>', unsafe_allow_html=True)
                    
                    if 'recommendations' in analysis_results:
                        st.write(" **Recommendations**")
                        for rec in analysis_results['recommendations']:
                            st.markdown(f'<div class="insight-card">• {rec}</div>', unsafe_allow_html=True)
                    
                    if 'accuracy' in analysis_results:
                        st.write(" **Model Performance**")
                        st.metric("Prediction Accuracy", f"{analysis_results['accuracy']:.2%}")
                        
                except json.JSONDecodeError as e:
                    st.error(f"Error parsing analysis results: {str(e)}")
                except Exception as e:
                    st.error(f"Error displaying report details: {str(e)}")

def show_chatbot():
    st.title("Chat Support")
    
    # Chat interface
    st.markdown("""
        <style>
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .user-message {
            background-color: #2c3e50;
            color: white;
            margin-left: 2rem;
        }
        .bot-message {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            margin-right: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"""
                <div class="chat-message user-message">
                    <div>{message['content']}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="chat-message bot-message">
                    <div>{message['content']}</div>
                </div>
            """, unsafe_allow_html=True)

    # Chat input
    user_input = st.text_input("Ask about your medical report:", key="chat_input")
    
    if st.button("Send", type="primary"):
        if user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Get bot response
            chat_history = [msg['content'] for msg in st.session_state.chat_history]
            response = get_gemini_response(user_input, chat_history)
            
            # Add bot response to chat history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            
            # Clear input and rerun to update chat
            st.rerun()

# Main app logic
with st.sidebar:
    page = st.radio("Navigation", ["Upload & Analyze", "Report Generation", "Quick Summary", "Report History", "Chat Support"])
    
    # Add Font Awesome for icons
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <div class="social-links">
            <h4>Contact Us</h4>
            <div class="social-icons">
                <a href="https://github.com/yourusername" target="_blank" class="social-icon">
                    <i class="fab fa-github"></i>
                </a>
                <a href="https://linkedin.com/in/yourusername" target="_blank" class="social-icon">
                    <i class="fab fa-linkedin"></i>
                </a>
                <a href="https://instagram.com/yourusername" target="_blank" class="social-icon">
                    <i class="fab fa-instagram"></i>
                </a>
            </div>
            <div class="contact-text">
                support@neonanalyst.com
            </div>
        </div>
    """, unsafe_allow_html=True)

if page == "Chat Support":
    show_chatbot()
elif page == "Upload & Analyze":
    show_upload_and_analyze()
elif page == "Report Generation":
    show_report_generation()
elif page == "Quick Summary":
    show_quick_summary()
else:
    show_report_history()
