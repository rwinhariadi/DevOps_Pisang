import base64
import logging
import os
from io import BytesIO

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS  # Untuk menangani CORS
from PIL import Image
from tensorflow.keras.models import load_model

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Aktifkan CORS untuk mengizinkan permintaan dari frontend
CORS(app)

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Path model
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "model_pisang.h5")
logging.info(f"Loading model from: {model_path}")
try:
    model = load_model(model_path)
    logging.info("Model loaded successfully")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    model = None

# Data history (disimpan dalam memori untuk sementara)
history = [] # type: ignore


# Fungsi untuk preprocessing gambar
def preprocess_image(image, target_size=(150, 150)):
    try:
        image = image.resize(target_size)
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        return image_array
    except Exception as e:
        logging.error(f"Error in image preprocessing: {e}")
        raise


# Endpoint untuk menerima unggahan gambar dan melakukan prediksi
@app.route("/upload", methods=["POST"])
def upload_image():
    logging.info("Received a file upload request")

    if "file" not in request.files:
        logging.error("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    try:
        file = request.files["file"]
        image = Image.open(file)
        logging.info("Image file opened successfully")

        # Preprocess image
        processed_image = preprocess_image(image)
        logging.info("Image preprocessed successfully")

        # Perform prediction
        if model is None:
            raise ValueError("Model is not loaded")

        prediction = model.predict(processed_image)
        confidence = prediction[0][0]
        result = "Matang" if confidence > 0.5 else "Belum Matang"
        color = "Kuning" if result == "Matang" else "Hijau"

        # Convert image to base64 for storing in history
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_data = f"data:image/jpeg;base64,{image_base64}"

        # Cek apakah data sudah ada di history
        if not any(item["image"] == image_data for item in history):
            history.append({"image": image_data, "color": color, "status": result})
            logging.info("Data added to history")
        else:
            logging.info("Duplicate image detected, not added to history")

        # Return response to frontend
        return jsonify({"prediction": result, "accuracy": round(confidence * 100, 2)})
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return jsonify({"error": "Gagal memproses gambar"}), 500


@app.route("/add-history", methods=["POST"])
def add_history():
    try:
        data = request.json  # Ambil data JSON dari request
        if not any(item["image"] == data["image"] for item in history):
            history.append(data)
            logging.info("History added successfully")
            return jsonify({"message": "History added successfully"}), 200
        else:
            logging.info("Duplicate image detected in add-history, not added")
            return jsonify({"message": "Duplicate image detected"}), 200
    except Exception as e:
        logging.error(f"Error adding history: {e}")
        return jsonify({"error": "Failed to add history"}), 500


# Endpoint untuk mengambil data history
@app.route("/get-history", methods=["GET"])
def get_history():
    logging.info("History data fetched successfully")
    return jsonify(history), 200


# Jalankan aplikasi Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
