#!/usr/bin/env python3
"""Login as test_student and GET /accounts/account_entry/ to verify no OperationalError."""
import os
import sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')
import django
django.setup()
from django.test import Client
from django.conf import settings

try:
    settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ["testserver", "127.0.0.1", "localhost"]
except Exception:
    settings.ALLOWED_HOSTS = ["testserver", "127.0.0.1", "localhost"]

USERNAME = 'test_student'
PASSWORD = 'testpass'

client = Client()
# login
resp = client.post('/accounts/student_login/', {'username': USERNAME, 'password': PASSWORD}, SERVER={'HTTP_HOST': '127.0.0.1:8000'})
print('login status:', resp.status_code)

# now GET account_entry
resp2 = client.get('/accounts/account_entry/', SERVER={'HTTP_HOST': '127.0.0.1:8000'})
print('account_entry status:', resp2.status_code)
content = resp2.content.decode('utf-8', errors='replace')
print('content snippet:')
print(content[:2000])
