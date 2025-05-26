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

# Create superuser using a Python script
echo "Creating superuser..."
echo "Attempting to delete existing user 'admin' and create a new superuser..."
echo "from django.contrib.auth.models import User; 
try:
    User.objects.filter(username='admin').delete()
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created successfully')
except Exception as e:
    print(f'Error during superuser creation: {str(e)}')" | python manage.py shell

echo "Superuser creation process completed."

echo "Build completed." 