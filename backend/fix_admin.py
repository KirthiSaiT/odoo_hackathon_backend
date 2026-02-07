from app.core.database import get_db_cursor
from app.core.security import Security

def fix_admin_account():
    try:
        email = "admin@odoo.com"
        new_pass = "odoo@123"
        hashed = Security.hash_password(new_pass)
        
        with get_db_cursor() as cursor:
            # 1. Update Users Table: Set Password, Active=1, EmailVerified=1
            print(f"Updating Users table for {email}...")
            cursor.execute("""
                UPDATE Users 
                SET password_hash = ?, 
                    is_active = 1, 
                    is_email_verified = 1 
                WHERE email = ?
                """, (hashed, email))
            user_rows = cursor.rowcount
            
            # 2. Update Employees Table: Set Password (plain), Active=1
            print(f"Updating Employees table for {email}...")
            cursor.execute("""
                UPDATE Employees 
                SET Password = ?, 
                    IsActive = 1 
                WHERE Email = ?
                """, (new_pass, email))
            emp_rows = cursor.rowcount
            
            print(f"------------- REPORT -------------")
            print(f"Users table updated: {user_rows} rows")
            print(f"Employees table updated: {emp_rows} rows")
            
            if user_rows == 0:
                print("⚠️ WARNING: No user found in Users table! Creating basic admin user...")
                # Insert if missing
                cursor.execute("""
                    INSERT INTO Users (name, email, password_hash, role, role_id, is_active, is_email_verified, created_by)
                    VALUES (?, ?, ?, 'ADMIN', 1, 1, 1, 'SYSTEM')
                """, ('System Admin', email, hashed))
                print("✅ Created missing admin User.")
            
            print(f"\n✅ Admin Account Fixed")
            print(f"Email: {email}")
            print(f"Pass:  {new_pass}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_admin_account()
