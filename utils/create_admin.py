import os
import sys

# Ensure current working directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin_user():
    username = 'admin'
    email = 'admin@example.com'
    password = 'adminpass123'

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser successfully created! Username: '{username}', Password: '{password}'")
    else:
        print(f"Superuser '{username}' already exists.")

if __name__ == '__main__':
    create_admin_user()
