from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from app.utils.image_processing import process_image
from app.utils.data_analysis import analyze_data

app = Blueprint('app', __name__)

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return jsonify({'success': 'File uploaded successfully'})
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'data_file' not in request.files:
        return jsonify({'error': 'No data file part'})
    data_file = request.files['data_file']
    if data_file.filename == '':
        return jsonify({'error': 'No selected data file'})
    if data_file and allowed_file(data_file.filename):
        filename = secure_filename(data_file.filename)
        data_file.save(os.path.join(UPLOAD_FOLDER, filename))
        results = analyze_data(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({'results': results})
    return jsonify({'error': 'Invalid file type'})