import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

class Config:
    UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config.from_object(Config)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/filter', methods=['POST'])
def filter_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        filter_type = request.form.get('filter')
        if not filter_type:
            return jsonify({'error': 'No filter type specified'}), 400

        image = cv2.imread(filepath)
        processed_image = apply_filter(image, filter_type)
        if processed_image is None:
            return jsonify({'error': 'Invalid filter type'}), 400

        output_filename = f"filtered_{filename}"
        output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        cv2.imwrite(output_filepath, processed_image)

        return jsonify({'processed_file': output_filename}), 200

def apply_filter(image, filter_type):
    if filter_type == 'gaussian':
        return cv2.GaussianBlur(image, (15, 15), 0)
    elif filter_type == 'median':
        return cv2.medianBlur(image, 5)
    elif filter_type == 'bilateral':
        return cv2.bilateralFilter(image, 9, 75, 75)
    else:
        return None

if __name__ == '__main__':
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
    app.run(debug=True, port=5001)
