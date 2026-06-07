# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 10000

# Install system dependencies for WeasyPrint and PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies
# Note: dockerContext is root, so we look in backend/
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code from the backend folder
COPY backend/ /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port (Render uses $PORT, defaults to 10000)
EXPOSE 10000

# Start Gunicorn binding to the dynamic port
CMD gunicorn --bind 0.0.0.0:$PORT smetools_payroll_backend.wsgi:application
