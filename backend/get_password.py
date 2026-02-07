from app.core.database import get_db_cursor

def get_admin_creds():
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT Email, Password FROM Employees WHERE RoleId = 1")
            row = cursor.fetchone()
            if row:
                print(f"\n============================================")
                print(f"✅ ADMIN CREDENTIALS FOUND")
                print(f"Email:    {row[0]}")
                print(f"Password: {row[1]}")
                print(f"============================================\n")
            else:
                print("❌ No admin user found in Employees table.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_admin_creds()
