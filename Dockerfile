# Use the full Bookworm image for better build reliability
FROM python:3.11-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 10000

# Install only the essential system libraries for WeasyPrint and PostgreSQL
# The full 'bookworm' image already contains build-essential and python3-dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code from the backend folder
COPY backend/ /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port
EXPOSE 10000

# Start Gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT smetools_payroll_backend.wsgi:application
