FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    fonts-dejavu-core \
    jq \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    playwright \
    requests \
    beautifulsoup4 \
    lxml \
    flask \
    pillow \
    matplotlib \
    arabic-reshaper \
    python-bidi \
    pandas \
    jq

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Create app directory
WORKDIR /app

# Copy application files
COPY wave_forecast.py .
COPY web_server.py .
COPY static/ ./static/
COPY templates/ ./templates/
COPY run.sh .

# Make run script executable
RUN chmod +x run.sh

# Expose port
EXPOSE 8099

# Run the application
CMD ["./run.sh"]
