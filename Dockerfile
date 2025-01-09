FROM node:latest AS builder

WORKDIR /app
COPY package.json .
COPY package-lock.json .
COPY tailwind.config.js .
COPY static static
COPY templates templates

RUN npm install
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/style.css



# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and application code into the container
COPY requirements.txt /app/
COPY . /app/
COPY --from=builder /app .

# Install system dependencies required for the application
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Default environment variable for Gunicorn settings
# These can be overridden by passing different values at runtime or in docker-compose.yml
ENV GUNICORN_CMD_ARGS="--workers 3 --bind 0.0.0.0:8000"

# Run Gunicorn to serve the Flask app
CMD ["gunicorn", "main:app"]