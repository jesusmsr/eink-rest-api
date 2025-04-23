# app/routes.py
from flask import Blueprint, current_app, request, jsonify
from werkzeug.utils import secure_filename
import os
from .models import db, DisplayRequest
from datetime import datetime

routes = Blueprint('routes', __name__)

UPLOAD_FOLDER = "app/static/images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route('/api/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename}"
        image_folder = os.path.join(current_app.root_path, 'static', 'images')
        os.makedirs(image_folder, exist_ok=True)

        filepath = os.path.join(image_folder, filename)
        file.save(filepath)
        
        relative_path = filepath.replace("\\", "/")
        display_request = DisplayRequest(image_path=relative_path)
        db.session.add(display_request)
        db.session.commit()

        return jsonify({'message': 'Image uploaded', 'path': relative_path}), 200

@routes.route('/api/latest-image', methods=['GET'])
def get_latest_image():
    latest = DisplayRequest.query.order_by(DisplayRequest.timestamp.desc()).first()
    if latest:
        return jsonify({
            "image_path": latest.image_path
        }), 200
    return jsonify({"error": "No image found"}), 404
