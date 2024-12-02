# Use Python official image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create a directory for config file
RUN mkdir -p /app/config

# Set environment variable for config path (if needed)
ENV CONFIG_PATH=/app/config/config.yaml

# Add a volume for the config file
VOLUME ["/app/config"]

# Set the default command
CMD ["python", "musicMille.py"]