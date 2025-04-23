from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from . import db
from .models import DisplayRequest
import os

from .utils import process_image

from flask import current_app as app

@app.route("/display/text", methods=["POST"])
def display_text():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Text is required"}), 400

    entry = DisplayRequest(type="text", content=text)
    db.session.add(entry)
    db.session.commit()

    return jsonify({"message": "Text added to queue"}), 201

@app.route("/display/image", methods=["POST"])
def display_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(filepath)

    # Optionally process it here
    processed_path = process_image(filepath)

    entry = DisplayRequest(type="image", content=os.path.basename(processed_path))
    db.session.add(entry)
    db.session.commit()

    return jsonify({"message": "Image added to queue"}), 201
