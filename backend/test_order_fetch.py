from app.services.order_service import OrderService
import logging

logging.basicConfig(level=logging.INFO)

def test_fetch():
    # Attempt to fetch order with ID 5 (from previous script output)
    order = OrderService.get_order_details("5")
    print(f"Order 5: {order}")

if __name__ == "__main__":
    test_fetch()
