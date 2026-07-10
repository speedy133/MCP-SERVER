FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY .env.example .env.example

# Default command runs the FastAPI server
# Railway will route to port 8080
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8080"]
