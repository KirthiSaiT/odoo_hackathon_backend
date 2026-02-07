from app.core.database import get_db_cursor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    try:
        with get_db_cursor() as cursor:
            # Create Orders table
            logger.info("Creating Orders table...")
            cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Orders')
            BEGIN
                CREATE TABLE Orders (
                    Id INT PRIMARY KEY IDENTITY(1,1),
                    UserId NVARCHAR(255) NOT NULL,
                    TotalAmount DECIMAL(18,2) NOT NULL,
                    Status NVARCHAR(50) NOT NULL DEFAULT 'Pending',
                    CreatedAt DATETIME NOT NULL DEFAULT GETDATE()
                );
                PRINT 'Orders table created.';
            END
            ELSE
            BEGIN
                PRINT 'Orders table already exists.';
            END
            """)
            
            # Create OrderItems table
            logger.info("Creating OrderItems table...")
            cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'OrderItems')
            BEGIN
                CREATE TABLE OrderItems (
                    Id INT PRIMARY KEY IDENTITY(1,1),
                    OrderId INT NOT NULL,
                    ProductId INT NOT NULL,
                    Quantity INT NOT NULL,
                    Price DECIMAL(18,2) NOT NULL,
                    VariantId INT NULL,
                    PlanName NVARCHAR(255) NULL,
                    FOREIGN KEY (OrderId) REFERENCES Orders(Id),
                    FOREIGN KEY (ProductId) REFERENCES Products(Id)
                );
                PRINT 'OrderItems table created.';
            END
            ELSE
            BEGIN
                PRINT 'OrderItems table already exists.';
            END
            """)
            logger.info("✅ Database setup completed successfully.")
    except Exception as e:
        logger.error(f"❌ Error setting up database: {str(e)}")

if __name__ == "__main__":
    setup_database()
