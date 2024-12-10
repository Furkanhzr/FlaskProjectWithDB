import pytest
import requests
import time

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="session", autouse=True)
def start_server():
    # Sunucunun çalıştığından emin olmak için biraz bekleme koyabiliriz.
    # Burada app.py'nin zaten bir başka terminalde çalıştığı varsayılıyor.
    # Eğer testler otomatik server başlatacaksa, subprocess ile app.py başlatılabilir.
    time.sleep(1)
    yield
    # Test bittikten sonra herhangi bir clean-up gerekirse yapılabilir.

def test_get_all_items():
    response = requests.get(f"{BASE_URL}/items")
    assert response.status_code == 200
    assert isinstance(response.json().get("items"), list)

def test_create_item():
    new_item = {"name": "Monitor", "price": 300}
    response = requests.post(f"{BASE_URL}/items", json=new_item)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Item created"
    assert data["item"]["name"] == "Monitor"
    assert data["item"]["price"] == 300

def test_get_specific_item():
    # Burada 1 ID'li item mevcut değilse test öncesi bir item eklemeniz gerekebilir.
    # Test senaryosunda ilk eklenen item genellikle ID=1 olur (AUTO_INCREMENT ise).
    response = requests.get(f"{BASE_URL}/items/1")
    # Eğer 1 nolu item yoksa test hata verebilir, ID'si bilinen bir ID kullanın.
    assert response.status_code == 200
    item = response.json().get("item")
    assert item["id"] == 1
    assert "name" in item and "price" in item

def test_update_item():
    updated_data = {"name": "Gaming Laptop", "price": 2000}
    response = requests.put(f"{BASE_URL}/items/1", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Item updated"
    assert data["item"]["name"] == "Gaming Laptop"
    assert data["item"]["price"] == 2000

def test_delete_item():
    # Test senaryosunda 3 ID'li bir item varsa sileceğiz.
    # Yoksa önce bir kaç item ekleyip ID 3'e kadar increment etmesini sağlayabilirsiniz.
    # Alternatif olarak, test_create_item testinin yarattığı item'in ID'sini yakalayarak kullanabilirsiniz.
    response = requests.delete(f"{BASE_URL}/items/3")
    # Eğer 3 ID'li item yoksa bu test hata verebilir, kendi senaryonuza göre düzenleyin.
    assert response.status_code == 200
    assert response.json().get("message") == "Item deleted"

    # Silinen item'ı tekrar sorgula
    response = requests.get(f"{BASE_URL}/items/3")
    assert response.status_code == 404
    assert response.json().get("message") == "Item not found"
