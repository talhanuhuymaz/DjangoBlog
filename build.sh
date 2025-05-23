#!/bin/bash
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Create staticfiles directory
mkdir -p staticfiles

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input --clear 