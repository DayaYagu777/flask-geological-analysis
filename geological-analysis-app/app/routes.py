from flask import Blueprint, request, jsonify, render_template, send_from_directory, current_app, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import json
from app.utils.image_processing import analyze_geological_image, image_to_array
from app.utils.data_analysis import load_excel_data, filter_geological_data, analyze_rmr_data, analyze_fracture_data
from app.models import get_user_by_username

bp = Blueprint('app', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def home():
    return render_template('dashboard.html')

@bp.route('/geological-analysis')
def geological_analysis():
    return render_template('geological_analysis.html')

@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return jsonify({'success': 'File uploaded successfully', 'filename': filename})
    return render_template('upload.html')

@bp.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'})
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected image'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'success': True, 'filename': filename})
    return jsonify({'error': 'Invalid file type'})

@bp.route('/upload-excel', methods=['POST'])
def upload_excel():
    if 'excel' not in request.files:
        return jsonify({'error': 'No Excel file'})
    file = request.files['excel']
    if file.filename == '':
        return jsonify({'error': 'No selected Excel file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'success': True, 'filename': filename})
    return jsonify({'error': 'Invalid file type'})

@bp.route('/serve-image/<filename>')
def serve_image(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/api/load-excel-data', methods=['POST'])
def load_excel_api():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'})
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'})
    
    excel_data = load_excel_data(filepath)
    if excel_data is not None:
        # Convert DataFrame to JSON-serializable format
        result = {
            'success': True,
            'data': excel_data.to_dict('records'),
            'columns': excel_data.columns.tolist()
        }
        return jsonify(result)
    return jsonify({'error': 'Failed to load Excel data'})

@bp.route('/api/filter-data', methods=['POST'])
def filter_data_api():
    data = request.get_json()
    mode = data.get('mode', 'rmr')  # 'rmr' or 'fracturas'
    filters = data.get('filters', {})
    
    try:
        if mode == 'rmr':
            filtered_data = analyze_rmr_data(data.get('data', []), filters)
        else:
            filtered_data = analyze_fracture_data(data.get('data', []), filters)
        
        return jsonify({'success': True, 'data': filtered_data})
    except Exception as e:
        return jsonify({'error': str(e)})

@bp.route('/api/analyze-image', methods=['POST'])
def analyze_image_api():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'})
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Image not found'})
    
    try:
        analysis_results = analyze_geological_image(filepath)
        return jsonify({'success': True, 'results': analysis_results})
    except Exception as e:
        return jsonify({'error': str(e)})

@bp.route('/api/save-measurement', methods=['POST'])
def save_measurement():
    data = request.get_json()
    measurement_data = {
        'points': data.get('points'),
        'distance': data.get('distance'),
        'scale': data.get('scale'),
        'timestamp': data.get('timestamp')
    }
    # For now, just return success. In a real app, you'd save to database
    return jsonify({'success': True, 'measurement_id': 'temp_id'})

@bp.route('/api/get-measurements', methods=['GET'])
def get_measurements():
    # For now, return empty list. In a real app, you'd fetch from database
    return jsonify({'success': True, 'measurements': []})

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = bool(request.form.get('remember'))
        
        # Find user by username
        user = get_user_by_username(username)
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('app.home'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('app.home'))

@bp.route('/analyze', methods=['POST'])
def analyze():
    if 'data_file' not in request.files:
        return jsonify({'error': 'No data file part'})
    data_file = request.files['data_file']
    if data_file.filename == '':
        return jsonify({'error': 'No selected data file'})
    if data_file and allowed_file(data_file.filename):
        filename = secure_filename(data_file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        data_file.save(filepath)
        results = load_excel_data(filepath)
        return jsonify({'results': results.to_dict('records') if results is not None else None})
    return jsonify({'error': 'Invalid file type'})
