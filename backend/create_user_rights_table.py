import logging
from app.core.database import get_db_cursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_user_rights_table():
    try:
        with get_db_cursor() as cursor:
            # Check if table exists
            cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'UserRights'")
            if cursor.fetchone():
                logger.info("UserRights table already exists.")
                return

            logger.info("Creating UserRights table...")
            sql = """
            CREATE TABLE UserRights (
                Id INT PRIMARY KEY IDENTITY(1,1),
                UserId INT NOT NULL,
                ModuleKey NVARCHAR(100) NOT NULL,
                CanView BIT DEFAULT 0,
                CanCreate BIT DEFAULT 0,
                CanUpdate BIT DEFAULT 0,
                CanDelete BIT DEFAULT 0
            );
            """
            cursor.execute(sql)
            logger.info("✅ UserRights table created successfully.");
            
    except Exception as e:
        logger.error(f"❌ Error creating UserRights table: {e}")

if __name__ == "__main__":
    create_user_rights_table()
