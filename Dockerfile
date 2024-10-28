# Base image
FROM python:3.8-slim

# Working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Expose port and run
EXPOSE 8080
CMD ["python", "app/app.py"]