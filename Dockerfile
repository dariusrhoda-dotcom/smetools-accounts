# Use the full Bullseye image for better build reliability and compatibility on Render
FROM python:3.11-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 10000

# Harden apt-get process and install dependencies
# We ensure update and install are joined with && to avoid using stale cache layers.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code from the backend folder
COPY backend/ /app/

# Provide dummy environment variables for collectstatic during build
ARG SECRET_KEY=dummy
ENV SECRET_KEY=$SECRET_KEY
ENV DATABASE_URL=sqlite:///:memory:
ENV DEBUG=False

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port
EXPOSE 10000

# Start Gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT smetools_payroll_backend.wsgi:application
