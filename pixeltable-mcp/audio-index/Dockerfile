FROM python:3.10-slim

WORKDIR /app

# FFmpeg and build-essential are required for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spacy model for sentence splitting
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY server.py .
COPY tools.py .

# Create directory for audio files
RUN mkdir -p /app/audio_index

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8080"]
