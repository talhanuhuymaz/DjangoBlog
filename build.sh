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

# Create superuser directly
echo "Creating superuser..."
python -c "
from django.contrib.auth.models import User
try:
    if not User.objects.filter(username='Talhanuh').exists():
        User.objects.create_superuser('Talhanuh', 'admin@example.com', 'admin12345')
        print('Superuser created successfully')
    else:
        user = User.objects.get(username='Talhanuh')
        user.is_staff = True
        user.is_superuser = True
        user.set_password('admin12345')
        user.save()
        print('Existing user updated with superuser privileges')
except Exception as e:
    print(f'Error creating superuser: {str(e)}')
"

echo "Build completed." 