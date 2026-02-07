import sys
import os

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app.core.database import get_db_cursor

def check_images():
    try:
        print("--- Connecting to DB ---")
        with get_db_cursor() as cursor:
            print("--- Checking Last 5 Products ---")
            cursor.execute("SELECT TOP 5 Id, Name, MainImage FROM Products ORDER BY Id DESC")
            products = cursor.fetchall()
            
            for p in products:
                print(f"Product: {p.Name} (ID: {p.Id})")
                print(f"  - MainImage: {p.MainImage}")
                
                # Check Sub Images
                cursor.execute("SELECT ImageURL FROM ProductSubImages WHERE ProductId = ?", (p.Id,))
                subs = cursor.fetchall()
                if subs:
                    print(f"  - Sub Images: {[s.ImageURL for s in subs]}")
                else:
                    print("  - No Sub Images found.")
                print("-" * 30)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_images()
