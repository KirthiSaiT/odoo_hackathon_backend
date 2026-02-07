from app.core.database import get_db_cursor
from app.core.security import Security

def reset_admin_pass():
    try:
        new_pass = "odoo@123"
        # We need to hash it if we are updating Users table, but for Employees table we store plain text in this design (based on schema review)
        # Wait, the schema said: "Password VARCHAR(255)" in Employees. 
        # And Users table has PasswordHash.
        # The login uses Users table?
        # Let's check AuthService.login
        
        # AuthService.login uses Users table usually?
        # Let's check auth_service.py to be sure which table it checks.
        
        with get_db_cursor() as cursor:
            # 1. Update Employees Table (Plain text as per schema design in admin_schema.sql?)
            # Actually, let's just update both to be safe.
            cursor.execute("UPDATE Employees SET Password = ? WHERE Email = 'admin@odoo.com'", (new_pass,))
            
            # 2. Update Users Table (Hashed)
            hashed = Security.hash_password(new_pass)
            cursor.execute("UPDATE Users SET password_hash = ? WHERE email = 'admin@odoo.com'", (hashed,))
            
            print(f"\n✅ Password Reset Successful")
            print(f"Email:    admin@odoo.com")
            print(f"New Pass: {new_pass}")
            print(f"\nPlease try logging in now.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reset_admin_pass()
