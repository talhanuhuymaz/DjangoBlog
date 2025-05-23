#!/bin/bash
set -o errexit

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Creating staticfiles directory..."
mkdir -p staticfiles

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser..."
python manage.py createsuperuser --noinput || true 