# Gunakan base image Python 3.9 atau yang sesuai
FROM python:3.9-slim

# Set lingkungan kerja dalam container
WORKDIR /container

# Copy file requirements.txt ke dalam container dan install dependencies
COPY requirements.txt .

# Install dependencies menggunakan pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file proyek ke dalam container
COPY . .

# Expose port yang akan digunakan Flask (disesuaikan dengan port di app.py)
EXPOSE 8080

# Jalankan aplikasi menggunakan perintah berikut
CMD ["python", "app/app.py"]
