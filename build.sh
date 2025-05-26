#!/bin/bash
set -o errexit

# Print environment variables (excluding sensitive data)
echo "DEBUG=${DEBUG}"
echo "DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}"
echo "Checking DATABASE_URL is set: $([[ -n "${DATABASE_URL}" ]] && echo 'Yes' || echo 'No')"

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Creating staticfiles directory..."
mkdir -p staticfiles

echo "Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Only try to create a superuser if the environment variables are set
if [[ -n "${DJANGO_SUPERUSER_USERNAME}" ]] && [[ -n "${DJANGO_SUPERUSER_PASSWORD}" ]] && [[ -n "${DJANGO_SUPERUSER_EMAIL}" ]]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser already exists."
else
    echo "Skipping superuser creation. Environment variables not set."
fi

echo "Build completed." 