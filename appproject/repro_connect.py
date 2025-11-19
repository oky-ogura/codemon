import os, sys
import traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE','appproject.settings')
try:
    import django
    django.setup()
except Exception:
    traceback.print_exc()
    sys.exit(2)
from django.conf import settings
print('DATABASES:', settings.DATABASES)
try:
    import psycopg2
except Exception:
    print('psycopg2 import failed')
    traceback.print_exc()
    sys.exit(3)
params = settings.DATABASES['default']
print('Params repr:')
for k,v in params.items():
    print(f'{k}:', repr(v))
try:
    conn = psycopg2.connect(dbname=params['NAME'], user=params['USER'], password=params['PASSWORD'], host=params['HOST'], port=params['PORT'])
    print('Connected OK')
    conn.close()
except Exception as e:
    traceback.print_exc()
    print('TYPE:', type(e))
    sys.exit(1)
