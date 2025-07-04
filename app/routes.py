# app/routes.py
from flask import Blueprint, current_app, request, jsonify
from werkzeug.utils import secure_filename
import os

from app.image_processing import process_image_for_epaper
from app.utils import get_local_ip
from .models import BatteryStatus, db, DisplayRequest
from datetime import datetime
from PIL import Image
import random
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


routes = Blueprint('routes', __name__)

UPLOAD_FOLDER = os.path.join("app", "static", "images")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp"}
LOCAL_IP = get_local_ip()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Auth
@routes.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == os.getenv("ADMIN_PWD"):  
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

# Protected
@routes.route('/api/all-images', methods=['GET'])
@jwt_required()
def all_images():
    all_images = DisplayRequest.query.order_by(DisplayRequest.timestamp.desc()).all()
    return jsonify([image.to_dict() for image in all_images]), 200

    import os

@routes.route('/api/delete-image/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(image_id):
    # Buscar la entrada por ID
    image_entry = DisplayRequest.query.get(image_id)
    if not image_entry:
        return jsonify({"error": "Imagen no encontrada"}), 404

    try:
        # Borrar los archivos físicos
        processed_path = os.path.join(current_app.root_path, 'static', 'images', 
                                      os.path.basename(image_entry.image_path))

        original_name = processed_path.replace('_processed.bmp', '')
        if os.path.exists(processed_path):
            os.remove(processed_path)
        if os.path.exists(original_name):
            os.remove(original_name)

        # Borrar de la base de datos
        db.session.delete(image_entry)
        db.session.commit()

        return jsonify({"message": "Imagen eliminada correctamente"}), 200
    except Exception as e:
        print(f"Error deleting image: {e}")
        return jsonify({"error": "No se pudo eliminar la imagen"}), 500

# End protected

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

        PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:5000")
        url = f"{PUBLIC_BASE_URL}/static/images/{processed_filename}"
        display_request = DisplayRequest(image_path=url, pending=True)
        db.session.add(display_request)
        db.session.commit()

        return jsonify({'message': 'Image uploaded and processed', 'path': url}), 200

from datetime import datetime

@routes.route('/api/image-last-used', methods=['GET'])
def get_last_used_image():
    last = DisplayRequest.query.filter(DisplayRequest.was_sent == True).order_by(DisplayRequest.last_sent_at.desc()).first()
    if last:
        return jsonify({
            "image_path": last.image_path,
            "timestamp": last.last_sent_at
        }), 200
    return jsonify({"error": "No image has been used yet"}), 404

@routes.route('/api/latest-image', methods=['GET'])
def get_latest_image():
    is_esp = request.headers.get("X-Device") == "esp32"

    pending = DisplayRequest.query.filter_by(pending=True).order_by(DisplayRequest.timestamp.asc()).first()
    if pending:
        if is_esp:
            pending.pending = False
            pending.was_sent = True
            pending.last_sent_at = datetime.utcnow()
            db.session.commit()
        return jsonify({
            "image_path": pending.image_path,
            "timestamp": pending.timestamp
        }), 200

    # Si no hay pendientes, mostrar random SOLO al ESP32 y registrar como usada
    if is_esp:
        all_images = DisplayRequest.query.all()
        if all_images:
            selected = random.choice(all_images)
            selected.was_sent = True
            selected.last_sent_at = datetime.utcnow()
            db.session.commit()
            return jsonify({
                "image_path": selected.image_path,
                "timestamp": selected.timestamp
            }), 200

    return jsonify({"error": "No images available"}), 404



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
            "voltage_level": latest.voltage,
            "timestamp": latest.timestamp
        }), 200
    return jsonify({"error": "No data"}), 404
