from app.core.database import get_db_cursor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_payments_table():
    try:
        with get_db_cursor() as cursor:
            # Check if table exists
            cursor.execute("IF OBJECT_ID('dbo.Payments', 'U') IS NOT NULL DROP TABLE dbo.Payments")
            
            logger.info("Creating Payments table...")
            cursor.execute("""
            CREATE TABLE Payments (
                Id INT IDENTITY(1,1) PRIMARY KEY,
                UserId NVARCHAR(255) NOT NULL,
                OrderId INT NULL,
                StripePaymentIntentId NVARCHAR(255) NULL,
                Amount DECIMAL(18,2) NOT NULL,
                Currency NVARCHAR(10) NOT NULL DEFAULT 'INR',
                Status NVARCHAR(50) NOT NULL DEFAULT 'Pending',
                PaymentMethod NVARCHAR(50) NULL,
                CreatedAt DATETIME DEFAULT GETDATE(),
                ModifiedAt DATETIME DEFAULT GETDATE()
            );
            """)
            
            # Create Indexes
            cursor.execute("CREATE INDEX IX_Payments_UserId ON Payments(UserId)")
            cursor.execute("CREATE INDEX IX_Payments_OrderId ON Payments(OrderId)")
            cursor.execute("CREATE INDEX IX_Payments_StripePaymentIntentId ON Payments(StripePaymentIntentId)")
            
            logger.info("✅ Payments table created successfully.")
            
    except Exception as e:
        logger.error(f"❌ Error creating Payments table: {str(e)}")

if __name__ == "__main__":
    create_payments_table()
