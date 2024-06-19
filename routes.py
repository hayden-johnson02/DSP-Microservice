import os
import requests
from flask import Blueprint, request, redirect, url_for, render_template, flash, send_from_directory
from werkzeug.utils import secure_filename
from models import Image
from extensions import db
from config import Config

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))

            new_image = Image(filename=filename)
            db.session.add(new_image)
            db.session.commit()

            flash('File successfully uploaded')
            return redirect(url_for('main.index'))

    images = Image.query.all()
    processed_filename = request.args.get('processed_filename')
    return render_template('index.html', images=images, processed_filename=processed_filename)

@main.route('/filter', methods=['POST'])
def filter():
    file_id = request.form.get('file_id')
    filter_type = request.form.get('filter_type')
    image = Image.query.get(file_id)

    if not image:
        flash('Image not found')
        return redirect(url_for('main.index'))

    filepath = os.path.join(Config.UPLOAD_FOLDER, image.filename)
    files = {'file': open(filepath, 'rb')}
    data = {'filter': filter_type}

    response = requests.post('http://localhost:5001/filter', files=files, data=data)
    if response.status_code == 200:
        processed_filename = response.json().get('processed_file')
        flash('Image successfully processed')
        return redirect(url_for('main.index', processed_filename=processed_filename))
    else:
        flash('Image processing failed')
        return redirect(url_for('main.index'))
    
@main.route('/edge-detection', methods=['POST'])
def edge_detection():
    file_id = request.form.get('file_id')
    edge_type = request.form.get('edge_type')
    image = Image.query.get(file_id)

    if not image:
        flash('Image not found')
        return redirect(url_for('main.index'))

    filepath = os.path.join(Config.UPLOAD_FOLDER, image.filename)
    files = {'file': open(filepath, 'rb')}
    data = {'edge_type': edge_type}

    response = requests.post('http://localhost:5002/edge-detection', files=files, data=data)
    if response.status_code == 200:
        processed_filename = response.json().get('processed_file')
        flash('Edge detection successfully applied')
        return redirect(url_for('main.index', processed_filename=processed_filename))
    else:
        flash('Edge detection failed')
        return redirect(url_for('main.index'))
    
@main.route('/transform', methods=['POST'])
def transform():
    file_id = request.form.get('file_id')
    transform_type = request.form.get('transform_type')
    image = Image.query.get(file_id)

    if not image:
        flash('Image not found')
        return redirect(url_for('main.index'))

    filepath = os.path.join(Config.UPLOAD_FOLDER, image.filename)
    files = {'file': open(filepath, 'rb')}
    data = {'transform_type': transform_type}

    response = requests.post('http://localhost:5003/transform', files=files, data=data)
    if response.status_code == 200:
        processed_filename = response.json().get('processed_file')
        flash('Image successfully transformed')
        return redirect(url_for('main.index', processed_filename=processed_filename))
    else:
        flash('Image transformation failed')
        return redirect(url_for('main.index'))

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
    