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

@app.route('/edge-detection', methods=['POST'])
def edge_detection():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        edge_type = request.form.get('edge_type')
        if not edge_type:
            return jsonify({'error': 'No edge detection type specified'}), 400

        image = cv2.imread(filepath, 0)
        edges = apply_edge_detection(image, edge_type)
        if edges is None:
            return jsonify({'error': 'Invalid edge detection type'}), 400

        output_filename = f"edges_{filename}"
        output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        cv2.imwrite(output_filepath, edges)

        return jsonify({'processed_file': output_filename}), 200

def apply_edge_detection(image, edge_type):
    if edge_type == 'canny':
        return cv2.Canny(image, 100, 200)
    elif edge_type == 'sobel':
        return cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=5)
    elif edge_type == 'laplacian':
        return cv2.Laplacian(image, cv2.CV_64F)
    else:
        return None

if __name__ == '__main__':
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
    app.run(debug=True, port=5002)
