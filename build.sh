#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files into staticfiles/ for WhiteNoise
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Seed starter content if database tables are empty
python manage.py seed --content
