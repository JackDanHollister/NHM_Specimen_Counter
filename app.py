#!/usr/bin/env python3
"""
YOLO Specimen Counter Web Service
A Flask web app that allows users to upload images via phone and get specimen counts back.
"""

import os
import sys
import subprocess
import shutil
import zipfile
import glob
from pathlib import Path
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, send_file, flash, jsonify, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'yolo_specimen_counter_secret_key_2025'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'yolo_count_specimens/images_to_test'
RESULTS_FOLDER = 'shareable_results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG', 'JPEG', 'PNG'}
MAX_FILES = 10

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Model zoo directory for selectable models
MODEL_ZOO_DIR = Path(__file__).resolve().parent / "model_zoo"
MODEL_ZOO_DIR.mkdir(exist_ok=True)


def get_available_models():
    """Return list of available model paths."""
    models = sorted(MODEL_ZOO_DIR.glob("*.pt"))
    fallback = Path(__file__).resolve().parent / "best.pt"
    if fallback.exists() and fallback not in models:
        models.insert(0, fallback)
    return [str(path) for path in models]

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {ext.lower() for ext in ALLOWED_EXTENSIONS}

def cleanup_old_uploads():
    """Remove all files from upload directory"""
    for file_path in glob.glob(os.path.join(UPLOAD_FOLDER, "*")):
        if os.path.isfile(file_path):
            os.remove(file_path)

def get_latest_results_folder():
    """Get the most recent results folder"""
    results_pattern = os.path.join(RESULTS_FOLDER, "specimen_counts_*")
    results_folders = glob.glob(results_pattern)
    if not results_folders:
        return None
    return max(results_folders, key=os.path.getctime)

def create_results_zip(results_folder):
    """Create a zip file of the results"""
    if not results_folder or not os.path.exists(results_folder):
        return None
    
    zip_filename = f"specimen_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join('static', zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add annotated images
        annotated_dir = os.path.join(results_folder, 'annotated_images')
        if os.path.exists(annotated_dir):
            for root, dirs, files in os.walk(annotated_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join('annotated_images', file)
                    zipf.write(file_path, arcname)
        
        # Add summary files
        summary_dir = os.path.join(results_folder, 'summary')
        if os.path.exists(summary_dir):
            for root, dirs, files in os.walk(summary_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join('summary', file)
                    zipf.write(file_path, arcname)
    
    return zip_filename

@app.route('/')
def upload_page():
    """Main upload page"""
    model_paths = get_available_models()
    models = [{'path': m, 'name': Path(m).name} for m in model_paths]
    default_model = models[0]['path'] if models else ''
    session['selected_model'] = default_model
    return render_template('upload.html', models=models, default_model=default_model)

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    if 'files' not in request.files:
        flash('No files selected')
        return redirect(request.url)

    available_models = get_available_models()
    if not available_models:
        flash('No models available. Add .pt files to model_zoo/.')
        return redirect(request.url)
    
    files = request.files.getlist('files')
    
    if not files or all(f.filename == '' for f in files):
        flash('No files selected')
        return redirect(request.url)
    
    if len(files) > MAX_FILES:
        flash(f'Maximum {MAX_FILES} files allowed')
        return redirect(request.url)

    # Persist selected model for processing step
    selected_model = request.form.get('model_name', '').strip()
    if selected_model not in available_models and available_models:
        selected_model = available_models[0]
    session['selected_model'] = selected_model
    
    # Clean up any old uploads first
    cleanup_old_uploads()
    
    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            uploaded_files.append(filename)
    
    if not uploaded_files:
        flash('No valid image files found')
        return redirect(request.url)
    
    flash(f'Successfully uploaded {len(uploaded_files)} files')
    return redirect(url_for('process_images'))

@app.route('/process')
def process_images():
    """Show processing page and trigger YOLO processing"""
    return render_template('processing.html')

@app.route('/run_yolo')
def run_yolo():
    """Run the YOLO processing script"""
    try:
        model_path = session.get('selected_model') or ''
        available_models = get_available_models()
        if not model_path and available_models:
            model_path = available_models[0]
        if model_path and model_path not in available_models:
            model_path = available_models[0] if available_models else ''

        if not model_path:
            return jsonify({'status': 'error', 'message': 'No model available. Add .pt files to model_zoo/.'})

        # Run the existing YOLO script
        result = subprocess.run([
            '/usr/local/bin/python',
            'run_count_specimens_with_counts.py',
            '--model-path',
            model_path
        ], 
        capture_output=True, 
        text=True, 
        cwd='/home/appuser/yolo'
        )
        
        if result.returncode == 0:
            return jsonify({'status': 'success', 'message': 'Processing completed'})
        else:
            return jsonify({'status': 'error', 'message': f'Processing failed: {result.stderr}'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error running YOLO: {str(e)}'})

@app.route('/results')
def show_results():
    """Show results page with download link"""
    results_folder = get_latest_results_folder()
    
    if not results_folder:
        flash('No results found. Please upload and process images first.')
        return redirect(url_for('upload_page'))
    
    # Parse summary information
    summary_file = os.path.join(results_folder, 'summary', 'detection_summary.txt')
    stats = {
        'images_processed': 0,
        'total_specimens': 0,
        'average_per_image': 0.0,
        'timestamp': ''
    }
    
    if os.path.exists(summary_file):
        with open(summary_file, 'r') as f:
            content = f.read()
            # Parse the summary file to extract stats
            lines = content.split('\n')
            for line in lines:
                if 'Total Images Processed:' in line:
                    stats['images_processed'] = int(line.split(':')[-1].strip())
                elif 'Total Specimens Detected:' in line:
                    stats['total_specimens'] = int(line.split(':')[-1].strip())
                elif 'Average Specimens per Image:' in line:
                    stats['average_per_image'] = float(line.split(':')[-1].strip())
    
    # Create zip file
    zip_filename = create_results_zip(results_folder)
    
    return render_template('results.html', stats=stats, zip_filename=zip_filename)

@app.route('/download/<filename>')
def download_file(filename):
    """Serve zip file for download"""
    file_path = os.path.join('static', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('File not found')
        return redirect(url_for('upload_page'))

if __name__ == '__main__':
    print("🔬 YOLO Specimen Counter Web Service Starting...")
    print("🌐 Local access: http://localhost:5000 (internal use)")
    app.run(host='0.0.0.0', port=5000, debug=True)
