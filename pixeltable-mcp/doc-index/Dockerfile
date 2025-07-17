FROM python:3.10-slim

WORKDIR /app

# FFmpeg and build-essential are required for video processing
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

# Create directory for documents
RUN mkdir -p /app/doc_index

# Expose the port the app runs on
EXPOSE 8083

# Command to run the application
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8083"]
