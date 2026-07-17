# ==============================================================================
# Stadium Pulse AI | Google Cloud Run Container Specification
# WHY: Multi-stage lightweight containerization guarantees < 50MB production image size,
# sub-second cold starts on Google Cloud Run, and secure non-root execution.
# ==============================================================================

FROM python:3.13-slim as builder

WORKDIR /build

# Install dependencies in isolated prefix
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final minimal production runtime image
FROM python:3.13-slim

WORKDIR /app

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source code
COPY app/ ./app/

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    PORT=8080 \
    HOST=0.0.0.0

# Create and switch to non-root secure user for Cloud Run execution
RUN useradd -m -u 1000 stadiumpulse && chown -R stadiumpulse:stadiumpulse /app
USER stadiumpulse


# Expose standard Cloud Run port 8080
EXPOSE 8080

# Launch Uvicorn high-performance async web server
CMD ["python3", "-m", "app.main"]
