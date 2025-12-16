from typing import Dict, List
from datetime import datetime
import csv
import file_manager

def view_transaction_history(user: Dict, limit: int = 10, page: int = 1) -> List:
    """Kullanıcının en son işlemlerini sayfalama ile görüntüler."""
    history = user.get("transactions", [])
    
    # İşlemleri ters çevir, böylece en yenisi başta olur
    history.reverse() 
    
    start_index = (page - 1) * limit
    end_index = start_index + limit
    
    # Sayfalama uygula [cite: 53]
    return history[start_index:end_index]

def export_transaction_history(user: Dict, directory: str = "exports") -> str:
    """İşlem geçmişini zaman damgalı CSV dosyasına dışa aktarır."""
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filepath = os.path.join(directory, f"{user['username']}_history_{timestamp}.csv") # Dışa aktarma dosyası [cite: 54]
    
    history = user.get("transactions", [])
    
    if not history:
        return "İşlem geçmişi bulunamadı."
        
    # İşlem sözlüklerindeki tüm anahtarları başlık olarak kullan
    fieldnames = list(history[0].keys())

    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(history)
        
    return filepath

def generate_summary_report(users: Dict) -> Dict:
    """Tüm banka için toplam para yatırma, çekme ve ortalama işlem boyutunu hesaplar."""
    all_transactions = file_manager.load_data()[1] # Global işlem listesini yükle
    total_deposits = 0.0
    total_withdrawals = 0.0
    deposit_count = 0
    withdrawal_count = 0
    
    for txn in all_transactions:
        if txn["type"] in ["deposit", "transfer_in", "interest_accrual"]:
            total_deposits += txn["amount"]
            deposit_count += 1
        elif txn["type"] in ["withdrawal", "transfer_out", "fee"]:
            total_withdrawals += txn["amount"]
            withdrawal_count += 1
            
    # Analizler: Toplam para yatırma/çekme, ortalama işlem boyutu [cite: 55]
    avg_deposit = total_deposits / deposit_count if deposit_count > 0 else 0
    avg_withdrawal = total_withdrawals / withdrawal_count if withdrawal_count > 0 else 0
    
    return {
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "average_deposit_size": avg_deposit,
        "average_withdrawal_size": avg_withdrawal,
    }

def total_bank_balance(users: Dict) -> float:
    """Bankadaki tüm kullanıcıların toplam bakiyesini hesaplar."""
    return sum(user.get("balance", 0.0) for user in users.values()) # Toplam bakiye [cite: 59]

def list_high_value_customers(users: Dict, threshold: float = 10000.0) -> List[Dict]:
    """Belirli bir eşiğin üzerindeki bakiyeye sahip müşterileri listeler."""
    high_value_customers = [
        {"username": u["username"], "balance": u["balance"], "full_name": u["full_name"]}
        for u in users.values() 
        if u.get("balance", 0.0) >= threshold and not u.get("is_admin", False)
    ] # Top N müşteriler [cite: 55, 62]
    
    # Bakiyeye göre sırala (en yüksekten en düşüğe)
    high_value_customers.sort(key=lambda x: x["balance"], reverse=True)
    
    return high_value_customers
