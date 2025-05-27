#!/bin/bash
set -o errexit

echo "=== Starting build process ==="
echo "Current date: $(date)"

# Print environment variables (excluding sensitive data)
echo "=== Environment Check ==="
echo "DEBUG=${DEBUG}"
echo "DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}"
echo "Checking DATABASE_URL is set: $([[ -n "${DATABASE_URL}" ]] && echo 'Yes' || echo 'No')"

echo "=== Installing dependencies ==="
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "=== Creating staticfiles directory ==="
mkdir -p staticfiles

echo "=== Running database migrations ==="
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear

# Create superuser if environment variable is set
echo "=== Checking for superuser creation ==="
if [[ $CREATE_SUPERUSER ]]; then
    echo "Creating superuser from environment variables..."
    python manage.py createsuperuser --no-input
    echo "Superuser creation completed"
fi

echo "=== Build process completed ==="
echo "Current date: $(date)" 