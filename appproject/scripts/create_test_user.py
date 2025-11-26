#!/usr/bin/env python3
"""Create or update a test Account using Django ORM.

Run this from project `appproject` dir, e.g.:
. .\.venv\Scripts\Activate.ps1; .\.venv\Scripts\python.exe .\scripts\create_test_user.py
"""
import os
import sys

proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
try:
    import django
    django.setup()
except Exception as e:
    print('Failed to setup Django:', e)
    raise

from accounts.models import Account
from django.contrib.auth.hashers import make_password

# Default test credentials (approved by user)
USERNAME = 'test_student'
EMAIL = 'test_student@example.com'
PASSWORD = 'testpass'
AGE = 10
ACCOUNT_TYPE = 'student'

def main():
    # Try to find by email first, then by user_name
    acc = Account.objects.filter(email=EMAIL).first() or Account.objects.filter(user_name=USERNAME).first()
    if acc:
        print(f'Found existing account (user_id={getattr(acc, "user_id", None)}). Updating fields and password.')
        acc.user_name = USERNAME
        acc.email = EMAIL
        acc.password = make_password(PASSWORD)
        acc.age = AGE
        acc.account_type = ACCOUNT_TYPE
        acc.save()
        print('Updated account:', getattr(acc, 'user_id', None), str(acc))
    else:
        acc = Account(user_name=USERNAME, email=EMAIL, password=make_password(PASSWORD), age=AGE, account_type=ACCOUNT_TYPE)
        acc.save()
        print('Created account:', getattr(acc, 'user_id', None), str(acc))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error creating/updating account:', e)
        raise
