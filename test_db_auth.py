
import pyodbc
import os

SERVER = '100.102.18.75'
DATABASE = 'SMP_DB'
USER = 'balas'
PASSWORD = 'YourNewPassword123!'

CONN_STR = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USER};PWD={PASSWORD};'

print(f"Connecting to {SERVER}...")

try:
    conn = pyodbc.connect(CONN_STR, timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    row = cursor.fetchone()
    print(f"✅ Success! Connected to: {row[0]}")
    conn.close()
except pyodbc.Error as e:
    print(f"❌ Connection failed: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
