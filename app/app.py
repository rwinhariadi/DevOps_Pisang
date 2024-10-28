import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import os

# Inisialisasi aplikasi Flask dan pastikan folder static dan templates dikenali
app = Flask(__name__, static_folder='templates/static', template_folder='templates')

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Memuat model yang sudah dilatih
print("Current working directory:", os.getcwd())
print("Files in directory:", os.listdir())
model = load_model('/app/model/model_pisang.h5')

# Fungsi untuk preprocessing gambar
def preprocess_image(image, target_size=(150, 150)):
    image = image.resize(target_size)
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array

# Endpoint untuk menampilkan halaman unggah gambar
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint untuk melayani file statis (CSS, JavaScript, dll) secara eksplisit
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('templates/static', filename)

# Endpoint untuk menerima unggahan gambar dan melakukan prediksi
@app.route('/upload', methods=['POST'])
def upload_image():
    logging.info('Received a file upload request')

    # Cek apakah file ada dalam request
    if 'file' not in request.files:
        logging.error('No file uploaded')
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        # Memproses file gambar
        file = request.files['file']
        image = Image.open(file)
        logging.info('Image file opened successfully')
        
        # Preprocessing gambar
        processed_image = preprocess_image(image)
        logging.info('Image preprocessed successfully')
        
        # Prediksi menggunakan model
        prediction = model.predict(processed_image)
        logging.info(f'Raw model output: {prediction}')

        # Ambil nilai confidence dari output model
        confidence = None
        if isinstance(prediction, np.ndarray):
            if prediction.shape == (1, 1):  # Jika outputnya [[0.8]]
                confidence = prediction[0][0]
            elif prediction.shape == (1,):  # Jika outputnya [0.8]
                confidence = prediction[0]
            else:
                logging.error("Unexpected shape of prediction output.")
                return jsonify({'error': 'Unexpected shape of prediction output'}), 500
        elif isinstance(prediction, (list, tuple)) and len(prediction) > 0:
            confidence = prediction[0]
        else:
            logging.error("Prediction output is not in the expected format.")
            return jsonify({'error': 'Prediction output is not in the expected format'}), 500

        # Logging untuk nilai confidence
        logging.info(f'Confidence value (raw): {confidence}')

        # Tentukan hasil prediksi berdasarkan confidence
        result = 'Matang' if confidence > 0.5 else 'Belum Matang'

        # Konversi confidence ke persentase dan kirim ke front-end
        return jsonify({'prediction': result, 'accuracy': round(confidence * 100, 2)})
    except Exception as e:
        logging.error(f'Error processing image: {e}')
        return jsonify({'error': 'Gagal memproses gambar'}), 500


# Menjalankan aplikasi di port 8080
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)