
import pyodbc
import os

# Connection String Config (matching your app)
SERVER = 'localhost\\SQLEXPRESS'
DATABASE = 'SMP_DB'
USER = 'balas'
PASSWORD = 'YourNewPassword123!'
# Try trusted connection first
CONN_STR = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USER};PWD={PASSWORD};'

def run_sql_file(filename):
    print(f"Reading {filename}...")
    try:
        with open(filename, 'r') as f:
            sql_script = f.read()
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        return

    # Split functionality for GO is needed because pyodbc can't run scripts with GO
    # But usually simple scripts without GO or split by GO works.
    # The provided script uses GO. We need to split it.
    commands = sql_script.split('GO')

    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        
        print(f"Connected to {DATABASE}. Executing commands...")
        
        for command in commands:
            if command.strip():
                try:
                    cursor.execute(command)
                    conn.commit()
                    print("Command executed successfully.")
                except Exception as e:
                    print(f"Error executing command: {e}")
                    # Continue or break?
        
        print("Done.")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'backend', 'setup_recurring_plans.sql')
    run_sql_file(file_path)
