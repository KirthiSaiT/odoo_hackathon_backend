from app.core.database import get_db_cursor
from app.core.security import Security

def create_superadmin_v2():
    try:
        email = "superadmin@odoo.com"
        password = "odoo@123"
        hashed = Security.hash_password(password)
        
        with get_db_cursor() as cursor:
            # 1. Get Tenant (Users table needs it)
            cursor.execute("SELECT TOP 1 tenant_id FROM Tenants")
            row = cursor.fetchone()
            if row:
                tenant_id = row[0]
                print(f"Using Tenant: {tenant_id}")
            else:
                # Create Tenant if missing
                print("Creating Tenant...")
                cursor.execute("INSERT INTO Tenants (tenant_name, created_by) OUTPUT INSERTED.tenant_id VALUES ('System Tenant', 'SCRIPT')")
                tenant_id = cursor.fetchone()[0]
                print(f"Created Tenant: {tenant_id}")
            
            # 2. Check/Create User
            cursor.execute("SELECT user_id FROM Users WHERE email = ?", (email,))
            if cursor.fetchone():
                print(f"Updating User {email}...")
                cursor.execute("""
                    UPDATE Users SET password_hash = ?, is_active = 1, is_email_verified = 1 
                    WHERE email = ?
                """, (hashed, email))
                cursor.execute("SELECT user_id FROM Users WHERE email = ?", (email,))
                user_id = cursor.fetchone()[0]
            else:
                print(f"Creating User {email}...")
                cursor.execute("""
                    INSERT INTO Users (tenant_id, name, email, password_hash, role, role_id, is_active, is_email_verified, created_by)
                    OUTPUT INSERTED.user_id
                    VALUES (?, 'Super Admin', ?, ?, 'ADMIN', 1, 1, 1, 'SCRIPT')
                """, (tenant_id, email, hashed))
                user_id = cursor.fetchone()[0]
            
            print(f"User ID: {user_id}")
            
            # 3. Check/Create Employee (WITHOUT TenantId)
            cursor.execute("SELECT Id FROM Employees WHERE Email = ?", (email,))
            if cursor.fetchone():
                print("Updating Employee...")
                cursor.execute("""
                    UPDATE Employees SET UserId = ?, RoleId = 1, IsActive = 1
                    WHERE Email = ?
                """, (user_id, email))
            else:
                print("Creating Employee...")
                # Insert basic employee without TenantId
                cursor.execute("""
                    INSERT INTO Employees (FirstName, LastName, Email, UserId, RoleId, IsActive, CreatedAt)
                    VALUES ('Super', 'Admin', ?, ?, 1, 1, SYSDATETIME())
                """, (email, user_id))
            
            print(f"\n✅ Superadmin Created Successfully")
            print(f"Email:    {email}")
            print(f"Password: {password}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_superadmin_v2()
