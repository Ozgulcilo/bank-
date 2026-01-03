
#FILE MANAGER

import json

FILENAME = "bank_data.json"

def save_data(users, transactions, config):
    """Tüm verileri JSON dosyasına kaydeder."""
    data = {
        "users": users,
        "transactions": transactions,
        "config": config
    }
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=4) # indent=4 dosyayı okunabilir yapar

def load_data():
    """Verileri dosyadan okur, dosya yoksa boş şablon döner."""
    try:
        with open(FILENAME, "r") as f:
            data = json.load(f)
            return data["users"], data["transactions"], data["config"]
    except FileNotFoundError:
        # Dosya yoksa başlangıç değerlerini döndür
        return {}, [], {"min_balance": 0, "bank_name": "Mega Bank"}
