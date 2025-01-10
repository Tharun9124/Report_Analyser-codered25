from flask import Flask, render_template, request, send_file, jsonify
import json
import os
from werkzeug.utils import secure_filename
from controller_agent import ControllerAgent

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def load_config():
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save the uploaded file
        filename = "SuperStoreUS-2015(Orders).csv"  # Use the expected filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Load and update configuration
        config = load_config()
        config['input_file'] = filepath
        config['output_dir'] = os.path.join(os.path.dirname(__file__), '..', 'output')

        # Create output directory if it doesn't exist
        os.makedirs(config['output_dir'], exist_ok=True)

        # Generate report
        controller = ControllerAgent(config)
        controller.execute()

        # Send the generated PDF back
        pdf_path = os.path.join(config['output_dir'], 'output_plots.pdf')
        if os.path.exists(pdf_path):
            return send_file(pdf_path, mimetype='application/pdf')
        else:
            return jsonify({'error': 'Failed to generate PDF'}), 500

    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
