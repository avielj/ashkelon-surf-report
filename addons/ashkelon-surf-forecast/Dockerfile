ARG BUILD_FROM
FROM $BUILD_FROM

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    chromium \
    chromium-chromedriver \
    curl \
    jq

# Install Python packages
RUN pip3 install --no-cache-dir \
    requests \
    beautifulsoup4 \
    lxml \
    flask \
    playwright \
    pandas

# Set up Playwright to use system chromium
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Create app directory
WORKDIR /app

# Copy application files
COPY wave_forecast.py .
COPY web_server.py .
COPY surf_forecast_simplified.py .
COPY static/ ./static/
COPY templates/ ./templates/
COPY run.sh .

# Make run script executable
RUN chmod +x run.sh

# Expose port
EXPOSE 8099

# Run the application
CMD ["./run.sh"]
