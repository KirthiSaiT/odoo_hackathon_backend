
from app.services.client_service import ClientService
from app.models.client_models import ClientCreate
from app.core.database import get_db_cursor
import logging
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_create_client():
    # Mock data
    client_data = ClientCreate(
        client_name="Test Client Debug",
        email=f"debug_test_client_{uuid.uuid4().hex[:8]}@example.com",
        contact_person="Debug Person",
        password="password123",
        product_id=1, 
        amount=100.00,
        payment_frequency="Monthly",
        subscription_start_date=datetime.now()
    )
    
    
    # Use valid UUIDs
    # import uuid # Removed duplicate import
    created_by = str(uuid.uuid4())
    # tenant_id will be fetched from DB

    print(f"Attempting to create client: {client_data}")
    print(f"Created By (UUID): {created_by}")

    try:
        # Check connection and verify Product
        with get_db_cursor() as cursor:
            # ... (existing checks)
            
            # Fetch valid Tenant ID
            cursor.execute("SELECT TOP 1 tenant_id FROM Tenants")
            row = cursor.fetchone()
            if row:
                tenant_id = row.tenant_id
                print(f"Fetched valid Tenant ID: {tenant_id}")
            else:
                print("No tenants found. Creating a dummy tenant...")
                tenant_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO Tenants (tenant_id, name, created_at, is_active)
                    VALUES (?, 'Debug Tenant', SYSDATETIME(), 1)
                """, (tenant_id,))
                # cursor.commit() # Not needed
                print(f"Created dummy Tenant ID: {tenant_id}")

            cursor.execute("SELECT 1")
            print("DB Connection successful.")
            
            # Check Products schema
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Products'")
            columns = [row.COLUMN_NAME for row in cursor.fetchall()]
            
            if 'Id' in columns and 'SalesPrice' in columns:
                 # Ensure product 1 exists
                 cursor.execute("SELECT Id FROM Products WHERE Id = 1")
                 if not cursor.fetchone():
                     print("Creating dummy product for testing...")
                     try:
                         cursor.execute("""
                             SET IDENTITY_INSERT Products ON;
                             INSERT INTO Products (Id, Name, Description, SalesPrice, ProductType, IsActive, CreatedBy, CreatedAt) 
                             VALUES (1, 'Test Product', 'Desc', 100.00, 'Service', 1, 'SYSTEM', GETDATE());
                             SET IDENTITY_INSERT Products OFF;
                         """)
                         # cursor.commit() # Removed because get_db_cursor handles commit now
                     except Exception as e:
                         print(f"Failed to create dummy product: {e}")
            
        # Verify Tenant exists
        with open("debug_log.txt", "w") as log:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT tenant_id FROM Tenants WHERE tenant_id = ?", (tenant_id,))
                if cursor.fetchone():
                    msg = f"Verified: Tenant {tenant_id} exists in DB."
                    print(msg)
                    log.write(msg + "\n")
                else:
                    msg = f"ERROR: Tenant {tenant_id} NOT found in DB!"
                    print(msg)
                    log.write(msg + "\n")

            # Call service
            print("Calling ClientService.create_client...")
            log.write("Calling ClientService.create_client...\n")
            try:
                response = ClientService.create_client(client_data, created_by, tenant_id)
                print("Client created successfully!")
                print(response)
                log.write("Client created successfully!\n")
                log.write(str(response) + "\n")
                
                with open("debug_result.txt", "w") as f:
                    f.write("SUCCESS\n")
                    f.write(str(response))
            except Exception as e:
                log.write(f"FAILED: {e}\n")
                raise e

    except Exception as e:
        print("FAILED TO CREATE CLIENT")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        
        with open("debug_result.txt", "w") as f:
            f.write("FAILED TO CREATE CLIENT\n")
            f.write(f"Error Type: {type(e).__name__}\n")
            f.write(f"Error Message: {e}\n")
            import traceback
            traceback.print_exc(file=f)
        print("Error written to debug_result.txt")

if __name__ == "__main__":
    test_create_client()
