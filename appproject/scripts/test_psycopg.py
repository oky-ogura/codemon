import psycopg2
import traceback

params = {'dbname':'codemon','user':'postgres','password':'password','host':'localhost','port':5432}
print('Trying', params)
try:
    conn = psycopg2.connect(**params)
    print('Connected OK')
    conn.close()
except Exception as e:
    print('Exception repr:', repr(e))
    traceback.print_exc()
