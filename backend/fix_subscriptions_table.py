
from app.core.database import get_db_cursor
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

def fix_subscriptions_table():
    print("Fixing Subscriptions Table...")
    try:
        with get_db_cursor() as cursor:
            # 1. Rename existing table
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"Subscriptions_Backup_{timestamp}"
            
            # Check if Subscriptions exists
            cursor.execute("SELECT 1 FROM sys.tables WHERE name = 'Subscriptions'")
            if cursor.fetchone():
                print(f"Backing up existing Subscriptions table to {backup_name}...")
                cursor.execute(f"EXEC sp_rename 'Subscriptions', '{backup_name}'")
            
            # 2. Create new table
            print("Creating new Subscriptions table...")
            cursor.execute("""
                CREATE TABLE Subscriptions (
                    Id INT IDENTITY(1,1) PRIMARY KEY,
                    ClientId INT NOT NULL,
                    ProductId INT,
                    Amount DECIMAL(18, 2) NOT NULL,
                    PaymentFrequency NVARCHAR(50),
                    StartDate DATETIME,
                    EndDate DATETIME,
                    Status NVARCHAR(50) DEFAULT 'Pending',
                    CreatedBy NVARCHAR(450),
                    CreatedAt DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (ClientId) REFERENCES Clients(Id),
                    FOREIGN KEY (ProductId) REFERENCES Products(Id)
                )
            """)
            print("Subscriptions table created successfully.")

    except Exception as e:
        print(f"Failed to fix table: {e}")

if __name__ == "__main__":
    fix_subscriptions_table()
