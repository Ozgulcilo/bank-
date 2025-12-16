import hashlib
from datetime import datetime
from typing import Dict, Optional
import file_manager

# Simüle edilmiş aktif oturumlar ve başarısız giriş denemeleri
ACTIVE_SESSIONS = {}
FAILED_ATTEMPTS = {}
MAX_FAILED_ATTEMPTS = 3 # Başarısız deneme sınırı [cite: 27]


def hash_password(password: str) -> str:
    """Parolayı SHA256 ile hashler."""
    return hashlib.sha256(password.encode()).hexdigest() # Parola hashleme [cite: 112]

def register_user(users: Dict, profile: Dict) -> Dict:
    """Yeni bir müşteri kaydeder ve kullanıcı sözlüğüne ekler."""
    username = profile["username"]
    
    if username in users:
        raise ValueError("Kullanıcı adı zaten mevcut.")

    # Gerekli alanları kontrol edin (try/except kullanılamazsa basit kontrol)
    required_keys = ["username", "password", "full_name", "email", "security_question", "security_answer", "initial_deposit"]
    if not all(key in profile for key in required_keys):
        raise ValueError("Eksik profil bilgisi.")
        
    initial_deposit = float(profile["initial_deposit"])
    if initial_deposit < 0: # Negatif miktarı reddet [cite: 110]
        raise ValueError("İlk para yatırma miktarı negatif olamaz.")
        
    
    new_user = {
        "username": username,
        "hashed_password": hash_password(profile["password"]), # Hashlenmiş parola [cite: 26]
        "full_name": profile["full_name"],
        "email": profile["email"],
        "security_question": profile["security_question"],
        "security_answer": profile["security_answer"],
        "balance": initial_deposit, # İlk bakiye [cite: 26]
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "transactions": [], # Boş işlem listesi [cite: 98]
        "is_locked": False,
        "is_admin": profile.get("is_admin", False)
    }

    # İlk para yatırma işlemi kaydı
    if initial_deposit > 0:
        new_user["transactions"].append({
            "id": f"TXN-{len(file_manager.load_data()[1])+1:03d}", # Basit ID üretimi
            "type": "deposit", 
            "amount": initial_deposit, 
            "balance_after": initial_deposit, 
            "timestamp": new_user["created_at"], 
            "notes": "Initial deposit" # İlk para yatırma notu [cite: 99]
        })
    
    users[username] = new_user
    return new_user

def login_user(users: Dict, username: str, password: str) -> Optional[Dict]:
    """Kullanıcının kimliğini doğrular ve başarılı olursa kullanıcı sözlüğünü döndürür."""
    user = users.get(username)
    
    if not user:
        return None # Kullanıcı mevcut değil

    if user.get("is_locked"):
        print("Hesap kilitli. Yöneticiyle iletişime geçin.")
        return None

    if username in ACTIVE_SESSIONS:
        # Tek oturum önleme [cite: 114]
        print("Bu kullanıcı zaten başka bir oturumda giriş yapmış.")
        return None
        
    if user["hashed_password"] == hash_password(password):
        # Başarılı giriş
        user["last_login"] = datetime.now().isoformat()
        FAILED_ATTEMPTS.pop(username, None) # Başarısız denemeleri sıfırla
        ACTIVE_SESSIONS[username] = user # Oturumu kaydet [cite: 114]
        return user
    else:
        # Başarısız giriş
        count = FAILED_ATTEMPTS.get(username, 0) + 1
        FAILED_ATTEMPTS[username] = count
        
        if count >= MAX_FAILED_ATTEMPTS:
            user["is_locked"] = True # Hesabı kilitle [cite: 27]
            print(f"UYARI: {username} hesabı, 3 başarısız denemeden sonra kilitlendi.")
            
        print(f"Hatalı parola. Kalan deneme: {MAX_FAILED_ATTEMPTS - count}")
        return None

def logout_user(active_sessions: Dict, username: str) -> None:
    """Aktif oturumdan bir kullanıcıyı çıkarır ve verileri kaydeder."""
    active_sessions.pop(username, None) # Oturumdan kaldır [cite: 28]
    # Not: Verilerin diske yazılması main.py'de yapılmalıdır.

def reset_password(users: Dict, username: str, secret_answer: str, new_password: str) -> bool:
    """Güvenlik sorusuna yanıt vererek parolanın sıfırlanmasını sağlar."""
    user = users.get(username)
    if not user:
        return False

    if user.get("security_answer") == secret_answer:
        user["hashed_password"] = hash_password(new_password)
        return True
    return False

def is_admin(user: Dict) -> bool:
    """Kullanıcının yönetici olup olmadığını kontrol eder."""
    return user.get("is_admin", False)
