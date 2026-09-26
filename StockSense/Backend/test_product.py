import requests

url = "http://127.0.0.1:5000/api/products"

data = {
    "name": "Steel Rod",
    "sku": "STL-001",
    "category_id": None,
    "unit": "kg",
    "initial_stock": 100,
    "reorder_level": 20
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.json())