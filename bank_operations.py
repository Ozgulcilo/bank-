
from datetime import datetime
import file_manager

# Fonksiyonlar, daha sonra main.py'de diskten yüklenen `users` ve `transactions` nesnelerini almalıdır.

# Kısıtlama: Try/except kullanılamadığı için hatalar raise edilir.

def generate_transaction_id(transactions: List) -> str:
    """Benzersiz bir işlem kimliği (ID) oluşturur."""
    # Basit ID üretimi: Mevcut işlem sayısına +1 eklenir
    return f"TXN-{len(transactions) + 1:05d}" 

def record_transaction(transactions: List, user: Dict, transaction_type: str, amount: float, channel: str, notes: str) -> Dict:
    """Bir işlem kaydı oluşturur ve global işlem listesine ekler."""
    
    new_txn = {
        "id": generate_transaction_id(transactions),
        "type": transaction_type,
        "amount": amount,
        "balance_after": user["balance"], # İşlem sonrası bakiye [cite: 39]
        "timestamp": datetime.now().isoformat(), # Zaman damgası [cite: 39]
        "notes": notes,
        "username": user["username"], # İşlemin hangi kullanıcıya ait olduğunu izleme
        "channel": channel # Kanal bilgisi [cite: 39]
    }
    
    transactions.append(new_txn)
    # Ayrıca kullanıcının kendi işlem listesine de eklenir [cite: 98]
    user["transactions"].append({k: new_txn[k] for k in new_txn if k != "username"}) # Kullanıcının kendi listesine username hariç ekle
    
    return new_txn

def check_balance(user: Dict) -> float:
    """Kullanıcının mevcut bakiyesini döndürür."""
    return user.get("balance", 0.0) # Bakiye kontrolü [cite: 47]

def deposit_money(users: Dict, transactions: List, username: str, amount: float, channel: str = "branch") -> Dict:
    """Hesaba para yatırma işlemini gerçekleştirir."""
    user = users.get(username)
    if not user:
        raise ValueError(f"Kullanıcı '{username}' bulunamadı.")
        
    if amount <= 0: # Negatif veya sıfır miktarı reddet [cite: 110]
        raise ValueError("Yatırma miktarı pozitif olmalıdır.")

    # Bakiye atomik olarak güncellenir (Tekrar okuma/yazma gerekliliğini simüle etmek için) [cite: 39]
    # Try/except kullanılamadığı için, hata oluşursa veri tutarsızlığı olabilir.
    user["balance"] += amount
    
    # İşlem kaydı oluştur [cite: 39]
    transaction = record_transaction(
        transactions=transactions,
        user=user,
        transaction_type="deposit",
        amount=amount,
        channel=channel,
        notes=f"Deposit via {channel}"
    )

    return transaction


def withdraw_money(users: Dict, transactions: List, username: str, amount: float, channel: str = "branch") -> Dict:
    """Hesaptan para çekme işlemini gerçekleştirir."""
    user = users.get(username)
    if not user:
        raise ValueError(f"Kullanıcı '{username}' bulunamadı.")

    if amount <= 0: # Negatif veya sıfır miktarı reddet [cite: 110]
        raise ValueError("Çekme miktarı pozitif olmalıdır.")
        
    # Yapılandırma verilerini yükle
    _, _, config = file_manager.load_data()
    min_balance = config["min_balance"]

    # Overdraft (eksi bakiye) önleme kontrolü [cite: 41]
    if user["balance"] - amount < min_balance:
        # Minimum bakiye kuralını ihlal ediyor [cite: 41]
        raise ValueError(f"Yetersiz bakiye. İşlemden sonra bakiye en az {min_balance} olmalıdır.")

    # Bakiye atomik olarak güncellenir [cite: 39]
    user["balance"] -= amount
    
    # İşlem kaydı oluştur
    transaction = record_transaction(
        transactions=transactions,
        user=user,
        transaction_type="withdrawal",
        amount=amount,
        channel=channel,
        notes=f"Withdrawal via {channel}"
    )

    return transaction

def transfer_funds(users: Dict, transactions: List, sender_username: str, receiver_username: str, amount: float) -> Tuple[Dict, Dict]:
    """Hesaplar arasında para transferi gerçekleştirir."""
    sender = users.get(sender_username)
    receiver = users.get(receiver_username)
    
    if not sender:
        raise ValueError(f"Gönderen kullanıcı '{sender_username}' bulunamadı.")
    if not receiver:
        raise ValueError(f"Alıcı kullanıcı '{receiver_username}' bulunamadı.")
    if sender_username == receiver_username:
        raise ValueError("Kendinize transfer yapamazsınız.")

    if amount <= 0:
        raise ValueError("Transfer miktarı pozitif olmalıdır.")
        
    # Yapılandırma verilerini yükle
    _, _, config = file_manager.load_data()
    min_balance = config["min_balance"]
    
    # Overdraft (eksi bakiye) önleme kontrolü
    if sender["balance"] - amount < min_balance:
        raise ValueError(f"Gönderenin bakiyesi yetersiz. İşlemden sonra bakiye en az {min_balance} olmalıdır.")

    # 1. Gönderenden düşme (Debit)
    sender["balance"] -= amount
    
    # 2. Alıcıya ekleme (Credit) [cite: 40]
    receiver["balance"] += amount
    
    # 3. İşlem kayıtlarını oluşturma (Gönderen ve Alıcı için ayrı ayrı) [cite: 40]
    
    # Gönderen işlemi (Debit)
    sender_txn = record_transaction(
        transactions=transactions,
        user=sender,
        transaction_type="transfer_out",
        amount=amount,
        channel="Transfer",
        notes=f"Transfer to {receiver_username}"
    )

    # Alıcı işlemi (Credit)
    receiver_txn = record_transaction(
        transactions=transactions,
        user=receiver,
        transaction_type="transfer_in",
        amount=amount,
        channel="Transfer",
        notes=f"Transfer from {sender_username}"
    )

    return sender_txn, receiver_txn

def apply_interest(user: Dict, rate: float) -> Dict:
    """Kullanıcının bakiyesine faiz uygular."""
    interest_amount = user["balance"] * rate
    
    if interest_amount > 0:
        user["balance"] += interest_amount
        
        # Faiz işlemini kaydet
        transaction = record_transaction(
            transactions=file_manager.load_data()[1], # Global transaction listesini yükle
            user=user,
            transaction_type="interest_accrual",
            amount=interest_amount,
            channel="System",
            notes="Monthly interest application"
        )
        return transaction
    
    return {} # Faiz uygulanmadı

def calculate_monthly_fees(user: Dict, fee_schedule: Dict) -> Dict:
    """Kullanıcının bakiyesinden aylık ücretleri düşer."""
    fee_amount = fee_schedule.get("monthly_fee", 0.0)
    
    if fee_amount > 0 and user["balance"] >= fee_amount:
        user["balance"] -= fee_amount
        
        # Ücret işlemini kaydet
        transaction = record_transaction(
            transactions=file_manager.load_data()[1], # Global transaction listesini yükle
            user=user,
            transaction_type="fee",
            amount=fee_amount,
            channel="System",
            notes="Monthly service fee"
        )
        return transaction
    
    return {} # Ücret uygulanmadı
