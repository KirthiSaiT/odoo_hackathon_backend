import urllib.request
import json
import urllib.error

BASE_URL = "http://localhost:8000"

def test_products_endpoint():
    print("\n--- Testing GET /api/products ---")
    try:
        url = f"{BASE_URL}/api/products?page=1&size=10"
        with urllib.request.urlopen(url) as response:
            status = response.getcode()
            print(f"Status Code: {status}")
            data = json.loads(response.read().decode())
            print(f"Success! Fetched {len(data['items'])} items.")
            if data['items']:
                print(f"First item: {data['items'][0]['name']}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode()}")
    except Exception as e:
        print(f"Request Failed: {e}")

def test_cart_endpoint_no_auth():
    print("\n--- Testing GET /api/cart (No Auth) ---")
    try:
        url = f"{BASE_URL}/api/cart"
        with urllib.request.urlopen(url) as response:
            print(f"Unexpected Success: {response.status_code}")
    except urllib.error.HTTPError as e:
        print(f"Expected Error: {e.code}") # Should be 401
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    test_products_endpoint()
    test_cart_endpoint_no_auth()
