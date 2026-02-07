
import pyodbc
import os

# Connection String Config
SERVER = '100.102.18.75'
DATABASE = 'SMP_DB'
USER = 'balas'
PASSWORD = 'YourNewPassword123!'

CONN_STR = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USER};PWD={PASSWORD};'

def run_sql_file(filename):
    print(f"Reading {filename}...")
    try:
        with open(filename, 'r') as f:
            sql_script = f.read()
        
        # Split script by GO
        commands = sql_script.split('GO')
        
        conn = pyodbc.connect(CONN_STR, autocommit=True)
        cursor = conn.cursor()
        
        for command in commands:
            if command.strip():
                try:
                    cursor.execute(command)
                except Exception as e:
                    print(f"Error executing command: {e}")
        
        print(f"Successfully executed {filename}")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'backend', 'add_product_images.sql')
    
    if not os.path.exists(file_path):
         file_path = os.path.join(script_dir, 'add_product_images.sql')

    run_sql_file(file_path)
