import logging
import sys
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.core.database import get_db_cursor

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_products():
    print("\n--- Testing ProductService.get_all_products ---")
    try:
        products = ProductService.get_all_products(page=1, size=10)
        print(f"Successfully fetched {len(products.items)} products.")
        print(f"Total count: {products.total}")
        if products.items:
            p = products.items[0]
            print(f"First product ID: {p.id}, Name: {p.name}")
            print(f"Main Image ({type(p.main_image)}): {p.main_image}")
            # print(p.json()) # Pydantic v1
            print(p.model_dump_json()) # Pydantic v2
    except Exception as e:
        print(f"FAILED to fetch products: {e}")
        import traceback
        traceback.print_exc()

def test_cart():
    print("\n--- Testing CartService.get_cart ---")
    try:
        # Get a user ID first
        user_id = None
        with get_db_cursor() as cursor:
            # Column is user_id based on check_users.py output
            cursor.execute("SELECT TOP 1 user_id FROM Users")
            row = cursor.fetchone()
            if row:
                user_id = row[0]
                print(f"Using UserID: {user_id}")
            else:
                print("No users found in database.")
                return

        if user_id:
            cart = CartService.get_cart(user_id)
            print(f"Successfully fetched cart with {cart.total_items} items.")
            if cart.items:
                 print(f"First item: {cart.items[0]}")
    except Exception as e:
        print(f"FAILED to fetch cart: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_products()
    test_cart()
