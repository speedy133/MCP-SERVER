FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY .env.example .env.example

# Default command — app IDs come from env vars DEFAULT_PLAY_STORE_ID / DEFAULT_APP_STORE_ID
# These are read by main.py as fallbacks when no CLI args are provided
CMD ["python", "src/main.py"]
