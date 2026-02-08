
from app.core.database import get_db_cursor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def inspect_subscriptions():
    print("Inspecting Subscriptions Schema...")
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Subscriptions")
            count = cursor.fetchone()[0]
            print(f"Subscriptions row count: {count}")
            with open("schema_info.txt", "w") as f:
                 f.write(f"Row count: {count}\n")

    except Exception as e:
        print(f"Failed to inspect schema: {e}")
        with open("schema_info.txt", "w") as f:
             f.write(f"Failed to inspect schema: {e}")

if __name__ == "__main__":
    inspect_subscriptions()
