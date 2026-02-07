import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER", "localhost\\SQLEXPRESS")
DB_NAME = os.getenv("DB_NAME", "SMP_DB")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
TRUSTED_CONNECTION = os.getenv("TRUSTED_CONNECTION", "yes")

def get_connection_string():
    if TRUSTED_CONNECTION.lower() == "yes":
        return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection=yes;"
    else:
        return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD};"

def check_images():
    try:
        conn = pyodbc.connect(get_connection_string())
        cursor = conn.cursor()

        print("--- Checking Last 5 Products ---")
        cursor.execute("SELECT TOP 5 Id, Name, MainImage FROM Products ORDER BY CreatedAt DESC")
        products = cursor.fetchall()
        
        for p in products:
            print(f"Product: {p.Name} (ID: {p.Id}) | MainImage: {p.MainImage}")
            
            # Check Sub Images
            cursor.execute("SELECT ImageURL FROM ProductSubImages WHERE ProductId = ?", (p.Id,))
            subs = cursor.fetchall()
            if subs:
                print(f"  - Sub Images: {[s.ImageURL for s in subs]}")
            else:
                print("  - No Sub Images found.")
            print("-" * 30)

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_images()
