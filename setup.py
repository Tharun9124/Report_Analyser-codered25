import os
import shutil
import json

def create_directory_structure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define all required directories
    directories = {
        'data': ['raw'],
        'output': [],
        'src': ['agents', 'static/css', 'static/js', 'templates'],
    }
    
    # Create directories
    for parent_dir, subdirs in directories.items():
        parent_path = os.path.join(base_dir, parent_dir)
        os.makedirs(parent_path, exist_ok=True)
        print(f"Created directory: {parent_path}")
        
        for subdir in subdirs:
            full_path = os.path.join(parent_path, subdir)
            os.makedirs(full_path, exist_ok=True)
            print(f"Created directory: {full_path}")

def create_init_files():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    init_dirs = ['src', 'src/agents']
    for dir_path in init_dirs:
        init_file = os.path.join(base_dir, dir_path, '__init__.py')
        if not os.path.exists(init_file):
            open(init_file, 'w').close()
            print(f"Created file: {init_file}")

def create_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config = {
        "input_file": "data/raw/input.csv",
        "output_dir": "output",
        "google_api_key": "AIzaSyD6iLdx2V9dwGconOcPDNPC2eU9aQu4TxA"
    }
    
    config_path = os.path.join(base_dir, 'src', 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Created config file: {config_path}")

def create_requirements():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    requirements = """pandas
matplotlib
seaborn
scikit-learn
flask>=2.0.0
werkzeug>=2.0.0
google-generativeai>=0.3.0"""
    
    req_path = os.path.join(base_dir, 'src', 'requirements.txt')
    with open(req_path, 'w') as f:
        f.write(requirements)
    print(f"Created requirements file: {req_path}")

def setup_project():
    print("Setting up Report Analyzer project...")
    print("\n1. Creating directory structure...")
    create_directory_structure()
    
    print("\n2. Creating initialization files...")
    create_init_files()
    
    print("\n3. Creating configuration file...")
    create_config()
    
    print("\n4. Creating requirements file...")
    create_requirements()
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Install required packages:")
    print("   pip install -r src/requirements.txt")
    print("2. Run the application:")
    print("   python src/app.py")
    print("3. Open in browser:")
    print("   http://localhost:5000")

if __name__ == "__main__":
    setup_project()
