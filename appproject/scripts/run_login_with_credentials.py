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
resp = client.post('/accounts/student_login/', {'username': USERNAME, 'password': PASSWORD}, SERVER={'HTTP_HOST': '127.0.0.1:8000'})
print('status_code:', resp.status_code)
content = resp.content.decode('utf-8', errors='replace')
print('content_snippet:')
print(content[:2000])
if resp.status_code >= 500:
    print('\nServer-side error likely occurred (>=500)')
else:
    print('\nRequest completed (status < 500)')
