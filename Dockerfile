FROM python:3.9-slim

WORKDIR /app

# Install required system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ src/
COPY config.yaml .

# Create non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Command to run the processor
CMD ["python", "-m", "src.processor"]