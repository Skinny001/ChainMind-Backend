# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Railway dynamically assigns a PORT environment variable. We default to 8000.
ENV PORT=8000 

# Install system dependencies required for Foundry and Python packages
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Foundry (forge, cast, anvil, chisel)
RUN curl -L https://foundry.paradigm.xyz | bash
# Update PATH so forge is accessible
ENV PATH="/root/.foundry/bin:${PATH}"
RUN foundryup

# Set the working directory to the standard app folder
WORKDIR /app

# Copy the entire project structure into the Docker image
# We need both backend and smartcontract folders since engine.py looks for ../../smartcontract
COPY backend/ /app/backend/
COPY smartcontract/ /app/smartcontract/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Create an empty .env file if it doesn't exist to prevent dotenv from crashing and allow Render/Railway ENV injection
RUN touch /app/backend/.env

# Initialize Foundry in the smartcontract directory (in case lib hasn't been committed to Git)
WORKDIR /app/smartcontract
RUN forge install --no-commit || true
RUN forge build

# Switch working directory to the backend so the Python app runs correctly
WORKDIR /app/backend

# Expose the API port
EXPOSE $PORT

# Start the FastAPI server using Uvicorn
# We use $PORT to support both Railway (dynamic) and Render (predictable) dynamic port bindings
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
