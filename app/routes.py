# app/routes.py
from flask import Blueprint, current_app, request, jsonify
from werkzeug.utils import secure_filename
import os

from app.image_processing import process_image_for_epaper
from app.utils import get_local_ip, process_image_to_acep_palette
from .models import BatteryStatus, db, DisplayRequest
from datetime import datetime
from PIL import Image

routes = Blueprint('routes', __name__)

UPLOAD_FOLDER = os.path.join("app", "static", "images")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp"}
LOCAL_IP = get_local_ip()

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

        original_path = os.path.join(image_folder, filename)
        
        file.save(original_path)

        processed_filename = filename.rsplit(".", 1)[0] + "_processed.bmp"
        processed_path = os.path.join(image_folder, processed_filename)
        process_image_for_epaper(original_path, processed_path)

        url = f"http://{LOCAL_IP}:5000/static/images/{processed_filename}"
        display_request = DisplayRequest(image_path=url)
        db.session.add(display_request)
        db.session.commit()

        return jsonify({'message': 'Image uploaded and processed', 'path': url}), 200

@routes.route('/api/latest-image', methods=['GET'])
def get_latest_image():
    latest = DisplayRequest.query.order_by(DisplayRequest.timestamp.desc()).first()
    if latest:
        return jsonify({
            "image_path": latest.image_path
        }), 200
    return jsonify({"error": "No image found"}), 404

@routes.route('/api/battery', methods=['POST'])
def battery_status():
    data = request.get_json()
    voltage = data.get('voltage')
    
    if voltage is None:
        return jsonify({"error": "Missing voltage parameter"}), 400

    # Aquí podrías guardar en base de datos si quieres un histórico
    print(f"Battery voltage received: {voltage}V")
    battery_status = BatteryStatus(voltage=voltage)
    db.session.add(battery_status)
    db.session.commit()
    
    return jsonify({"message": "Battery status received", "voltage": voltage}), 200

@routes.route('/api/battery-latest', methods=['GET'])
def battery_latest():

    latest = BatteryStatus.query.order_by(BatteryStatus.timestamp.desc()).first()
    if latest:
        return jsonify({
            "voltage_level": latest.voltage
        }), 200
    return jsonify({"error": "No data"}), 404

