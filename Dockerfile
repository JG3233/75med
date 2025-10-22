FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
# Disable progress bar to avoid threading issues on resource-constrained systems
COPY requirements.txt .
RUN PIP_PROGRESS_BAR=off pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create instance directory and non-root user
RUN mkdir -p instance \
    && adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)"

# Start application with Gunicorn (production WSGI server)
# --bind 0.0.0.0:5000 - Listen on all interfaces
# --workers 1 - Single worker for Raspberry Pi (avoid threading issues)
# --worker-class sync - Use sync workers (no threads) to avoid "can't start new thread" errors
# --timeout 60 - Request timeout
# --access-logfile - - Log to stdout
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--worker-class", "sync", "--timeout", "60", "--access-logfile", "-", "app:app"]
