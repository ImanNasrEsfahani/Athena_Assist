# Use the official Python 3.10 image as a base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV NGROK_VERSION=2.3.35

# Set working directory
WORKDIR /app

# Install necessary packages including curl
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    zip \
    python3-pip \
    build-essential \
    gcc \
    wget \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Download and build TA-Lib from source
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Copy requirements file to the container
COPY ./requirements/base.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r base.txt


# Copy your FastAPI application code
# COPY . .

# Expose the port the app runs on; FastAPI default is 8000
EXPOSE 8000

# Volume for logs and additional access to host filesystem
# VOLUME ["/logging.ini"]

# Command to run the FastAPI application with uvicorn and ngrok
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info --reload"]