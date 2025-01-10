from flask import Flask, render_template, request, jsonify, send_file, Response
import pandas as pd
import os
from src.agents.medical_llm_agent import MedicalLLMAgent
from src.agents.visualization_agent import VisualizationAgent
from src.agents.report_generation_agent import ReportGenerationAgent
from werkzeug.utils import secure_filename
import json
import traceback
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'data', 'raw')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Initialize agents
try:
    medical_agent = MedicalLLMAgent()
    report_agent = ReportGenerationAgent()
    viz_agent = VisualizationAgent()
    logger.info("All agents initialized successfully")
except Exception as e:
    logger.error(f"Error initializing agents: {str(e)}")
    logger.error(traceback.format_exc())

# Ensure directories exist
os.makedirs('output/reports', exist_ok=True)

def get_file_size(filepath):
    """Get file size in MB"""
    return os.path.getsize(filepath) / (1024 * 1024)

def read_csv_optimized(filepath, file_size):
    """Read CSV file with optimized settings based on file size"""
    if file_size < 50:  # For files under 50MB
        return pd.read_csv(filepath)
    else:
        # For large files, read only necessary columns first
        # Read first few rows to get column info
        df_sample = pd.read_csv(filepath, nrows=5)
        numeric_cols = df_sample.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = df_sample.select_dtypes(include=['object']).columns
        
        # Read full file with optimized settings
        df = pd.read_csv(
            filepath,
            usecols=list(numeric_cols) + list(categorical_cols),
            dtype={col: 'category' for col in categorical_cols},  # Use category type for strings
            engine='c',  # Use C engine for faster reading
            low_memory=True
        )
        return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            logger.warning("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            logger.info(f"Saving file to: {filepath}")
            file.save(filepath)
            
            try:
                # Check file size
                file_size = get_file_size(filepath)
                logger.info(f"File size: {file_size:.2f} MB")
                
                # Read the CSV file with optimized settings
                start_time = time.time()
                df = read_csv_optimized(filepath, file_size)
                logger.info(f"File read completed in {time.time() - start_time:.2f} seconds")
                
                # Generate medical insights
                logger.info("Generating medical insights")
                insights = medical_agent.analyze_health_data(df)
                logger.info("Medical insights generated successfully")
                
                # Generate visualizations
                logger.info("Generating visualizations")
                visualizations = viz_agent.generate_quick_visualizations(df)
                logger.info("Visualizations generated successfully")
                
                # Generate report with plots
                logger.info("Generating report")
                report_path, report_content = report_agent.generate_report(df)
                logger.info(f"Report generated at: {report_path}")
                
                # Prepare response data
                response_data = {
                    'success': True,
                    'dataset_info': {
                        'total_records': len(df),
                        'total_features': len(df.columns),
                        'numeric_columns': len(df.select_dtypes(include=['int64', 'float64']).columns),
                        'categorical_columns': len(df.select_dtypes(include=['object']).columns)
                    },
                    'insights': insights,
                    'visualizations': visualizations,
                    'report_path': str(report_path)
                }
                
                logger.info("Sending successful response")
                return jsonify(response_data)
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                logger.error(traceback.format_exc())
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        
        logger.warning("Invalid file type")
        return jsonify({'error': 'Invalid file type. Please upload a CSV file'}), 400
    
    except Exception as e:
        logger.error(f"Unexpected error in upload_file: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/analyze/<filename>')
def analyze_file(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return jsonify({'error': 'File not found'}), 404
        
        df = pd.read_csv(filepath)
        insights = medical_agent.analyze_health_data(df)
        return jsonify({'insights': insights})
    except Exception as e:
        logger.error(f"Error in analyze_file: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/visualize/<filename>')
def visualize_file(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return jsonify({'error': 'File not found'}), 404
        
        df = pd.read_csv(filepath)
        preview_data = viz_agent.generate_preview_data(df)
        return jsonify({'preview_data': preview_data})
    except Exception as e:
        logger.error(f"Error in visualize_file: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/report/<filename>')
def generate_report(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return jsonify({'error': 'File not found'}), 404
        
        df = pd.read_csv(filepath)
        report_path, report_content = report_agent.generate_report(
            df,
            analysis_depth='detailed',
            visual_style='modern'
        )
        return send_file(report_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Error in generate_report: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/download_report/<path:report_path>')
def download_report(report_path):
    try:
        return send_file(report_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Error in download_report: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
