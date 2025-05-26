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

# Create superuser using environment variables
echo "Creating superuser..."
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@example.com \
DJANGO_SUPERUSER_PASSWORD=admin123 \
python manage.py createsuperuser --noinput || true

# Ensure the user has proper permissions
echo "Verifying superuser permissions..."
python manage.py shell << EOF
from django.contrib.auth.models import User
try:
    user = User.objects.get(username='admin')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print('Successfully verified superuser permissions')
except Exception as e:
    print(f'Error verifying permissions: {str(e)}')
EOF

echo "Build completed." 