# Backend Dockerfile
# Build context must be the project root (set in docker-compose.yml)
# so we can copy both backend/ code and the CSV dataset.

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed by TensorFlow / HDF5
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libhdf5-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (cached layer)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the dataset
COPY ["Student data.csv", "/app/data/Student_data.csv"]

# Copy backend application code
COPY backend/ .

# Environment variables
ENV DATA_FILE=/app/data/Student_data.csv
ENV MODEL_DIR=/app/saved_models
ENV DATABASE_URI=sqlite:////app/db/student_data.db

# Create directories
RUN mkdir -p /app/saved_models /app/db

EXPOSE 5000

CMD ["python", "app.py"]
