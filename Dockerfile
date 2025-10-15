# Dockerfile for Visual Product Matcher (Flask + Waitress)
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable stdout/stderr flush
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

WORKDIR /app

# Install system deps for Pillow and building wheels if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

    # Make required directories
RUN mkdir -p static/uploads data/product_images

# Download sample data and build index on container start
RUN python setup_data.py

# Expose the port Spaces expects (7860 is commonly used in HF Spaces)
EXPOSE 7860

# Use waitress to serve the Flask app
CMD ["waitress-serve", "--host=0.0.0.0", "--port=7860", "--call", "app:create_app"]