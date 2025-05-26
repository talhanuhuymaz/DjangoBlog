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

# Create or update superuser
echo "=== Setting up superuser ==="
python manage.py shell << EOF
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# Define credentials
USERNAME = 'admin'
PASSWORD = 'admin123'
EMAIL = 'admin@example.com'

try:
    # Try to get existing user
    user = User.objects.filter(username=USERNAME).first()
    
    if user:
        print(f"Updating existing user: {USERNAME}")
        user.password = make_password(PASSWORD)
    else:
        print(f"Creating new user: {USERNAME}")
        user = User(username=USERNAME, email=EMAIL)
        user.password = make_password(PASSWORD)
    
    # Ensure superuser permissions
    user.is_staff = True
    user.is_superuser = True
    user.save()
    
    print("=== Superuser Details ===")
    print(f"Username: {user.username}")
    print(f"Is staff: {user.is_staff}")
    print(f"Is superuser: {user.is_superuser}")
    print("Password has been set to: admin123")
    
except Exception as e:
    print(f"ERROR setting up superuser: {str(e)}")
EOF

echo "=== Build process completed ==="
echo "Current date: $(date)" 