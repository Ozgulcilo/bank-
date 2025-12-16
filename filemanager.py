import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

# Dosya yolları için sabitler
USERS_PATH = "data/users.json"
TRANSACTIONS_PATH = "data/transactions.json"
BACKUP_DIR = "backups"
CONFIG_PATH = "data/config.json"

def initialize_storage(base_dir: str = "data") -> Dict:
    """Veri depolama için temel dizinleri ve dosyaları oluşturur."""
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Başlangıç yapılandırması
    initial_config = {
        "interest_rate": 0.015, # %1.5 faiz oranı [cite: 49]
        "min_balance": 10.00, # Asgari bakiye [cite: 41]
        "fee_schedule": {"monthly_fee": 5.00}
    }
    
    # Try/except olmadan dosya oluşturma
    with open(os.path.join(base_dir, "users.json"), 'w') as f:
        json.dump({}, f)
    with open(os.path.join(base_dir, "transactions.json"), 'w') as f:
        json.dump([], f)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(initial_config, f)

    return {"users": USERS_PATH, "transactions": TRANSACTIONS_PATH, "config": CONFIG_PATH}


def load_data(users_path: str = USERS_PATH, transactions_path: str = TRANSACTIONS_PATH, config_path: str = CONFIG_PATH) -> Tuple[Dict, List, Dict]:
    """Kullanıcıları, işlemleri ve yapılandırmayı dosyadan yükler."""
    
    # Try/except olmadan yükleme
    with open(users_path, 'r') as f:
        users = json.load(f)
    
    with open(transactions_path, 'r') as f:
        transactions = json.load(f)
        
    with open(config_path, 'r') as f:
        config = json.load(f)

    return users, transactions, config

def save_data(users_path: str = USERS_PATH, transactions_path: str = TRANSACTIONS_PATH, users: Dict = None, transactions: List = None, config_path: str = CONFIG_PATH, config: Dict = None) -> None:
    """Kullanıcıları, işlemleri ve yapılandırmayı dosyaya kaydeder."""
    if users is not None:
        with open(users_path, 'w') as f:
            json.dump(users, f, indent=4)
    
    if transactions is not None:
        with open(transactions_path, 'w') as f:
            json.dump(transactions, f, indent=4)
            
    if config is not None:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
            

def backup_data(source_paths: List[str], backup_dir: str = BACKUP_DIR) -> List[str]:
    """Belirtilen dosyaların zaman damgalı yedeklerini oluşturur."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backed_up_files = []
    
    for path in source_paths:
        base_name = os.path.basename(path)
        backup_filename = f"{timestamp}_{base_name}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Dosya içeriğini okuma ve yeni dosyaya yazma
        with open(path, 'r') as src, open(backup_path, 'w') as dest:
            dest.write(src.read())
            
        backed_up_files.append(backup_path)
        
    return backed_up_files

def validate_storage_schema(users: Dict) -> bool:
    """Kullanıcı verilerindeki gerekli alanları kontrol ederek şemayı doğrular."""
    required_keys = ["hashed_password", "full_name", "balance", "transactions", "created_at"]
    
    if not isinstance(users, dict):
        return False
        
    for username, user_data in users.items():
        if not all(key in user_data for key in required_keys):
            return False
        if not isinstance(user_data["transactions"], list):
            return False
            
    return True
