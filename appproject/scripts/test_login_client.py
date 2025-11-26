import os
import django
import sys
# Ensure project root is on sys.path so `appproject` package can be imported
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appproject.settings')

django.setup()
from django.test import Client
from django.conf import settings

# Ensure testserver/127.0.0.1 are allowed hosts for the test client
try:
    settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ["testserver", "127.0.0.1", "localhost"]
except Exception:
    settings.ALLOWED_HOSTS = ["testserver", "127.0.0.1", "localhost"]

c = Client()
# Provide HTTP_HOST to avoid DisallowedHost from default 'testserver'
resp = c.post('/accounts/student_login/', {'username': 'z', 'password': 'z'}, SERVER={'HTTP_HOST': '127.0.0.1:8000'})
print('status_code:', resp.status_code)
# for readability, only show beginning of content
content = resp.content.decode('utf-8', errors='replace')
print('content_snippet:')
print(content[:2000])
if resp.status_code >= 500:
    print('\nServer-side error likely occurred (>=500)')
else:
    print('\nRequest completed (status < 500)')
