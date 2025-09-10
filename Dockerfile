FROM python:3.10-slim

# DCTFd - A Capture The Flag platform built with Django
# Developed by Srivatsan Sk
# MIT License - Copyright (c) 2025 Srivatsan Sk

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_ENVIRONMENT=production
ENV DJANGO_SETTINGS_MODULE=DCTFd.settings

# Create and set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev \
        gcc \
        python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn

# Copy project files
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run as non-root user
RUN useradd -m dctfd
RUN chown -R dctfd:dctfd /app
USER dctfd

# Expose port for Gunicorn
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "DCTFd.wsgi:application"]
