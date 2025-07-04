FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    gcc \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the default Flask port
EXPOSE 5000

# Have to set the OpenAI API key from env var or bind-mount .env
ENV FLASK_APP=app.py

# Start the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
