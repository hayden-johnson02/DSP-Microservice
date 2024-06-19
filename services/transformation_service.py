import os
import cv2
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

class Config:
    UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config.from_object(Config)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/transform', methods=['POST'])
def transform_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        transform_type = request.form.get('transform_type')
        if not transform_type:
            return jsonify({'error': 'No transformation type specified'}), 400

        image = cv2.imread(filepath)
        transformed_image = apply_transformation(image, transform_type)
        if transformed_image is None:
            return jsonify({'error': 'Invalid transformation type'}), 400

        output_filename = f"transformed_{filename}"
        output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        cv2.imwrite(output_filepath, transformed_image)

        return jsonify({'processed_file': output_filename}), 200

def apply_transformation(image, transform_type):
    if transform_type == 'rotate':
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif transform_type == 'scale':
        width = int(image.shape[1] * 0.5)
        height = int(image.shape[0] * 0.5)
        return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    elif transform_type == 'flip':
        return cv2.flip(image, 1)
    else:
        return None

if __name__ == '__main__':
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
    app.run(debug=True, port=5003)
