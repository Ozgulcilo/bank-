import hashlib        # Parola şifreleme (hashing) için kütüphane
from datetime import datetime # Zaman damgaları (created_at, last_login) için

# file_manager.py'den gerekli fonksiyonları ve değişkenleri içe aktarır
from file_manager import save_users_to_file, USERS_FILE 

def hash_password(password: str) -> str:
    """
    Parolayı hashlib.sha256 kullanarak hash'ler (Güvenlik gereksinimi).
    """
    # Parolayı byte dizisine dönüştür ve SHA256 algoritmasıyla şifrelw
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(users: dict, profile: dict) -> dict | None:
    """
    Yeni bir kullanıcı kaydeder (Hesap açma).
    """
    username = profile.get("username")
    password = profile.get("password")
    initial_deposit = profile.get("initial_deposit", 0.0) # Başlangıç bakiyesi

    if not username or not password: return None
    if username in users: # Benzersiz kullanıcı adı kontrolü
        print(f"Hata: '{username}' kullanıcı adı zaten mevcut.")
        return None
    if initial_deposit < 0: # Başlangıç ın negatif olmasını engelle
        print("Hata: Başlangıç depozitosu negatif olamaz.")
        return None

    # Yeni kullanıcı için veri modelini oluşturur
    new_user = {
        "username": username,
        "hashed_password": hash_password(password), # Hashlenmiş parola saklanır 
        "full_name": profile.get("full_name", "N/A"),
        "balance": initial_deposit, # Müşterinin bakiyesi
        "created_at": datetime.now().isoformat(), # Hesabın oluşturulma zamanı
        "last_login": None,
        "transactions": [], # İşlem geçmişi listesi 
        "login_attempts": 0, # Başarısız giriş denemesi sayacı
        "locked": False # Hesap kilit durumu
    }

    users[username] = new_user          # Kullanıcıyı ana sözlüğe ekle
    save_users_to_file(USERS_FILE, users) # Değişikliği diske kaydet
    print(f"Kullanıcı '{username}' başarıyla kaydedildi.")
    return new_user


def login_user(users: dict, username: str, password: str) -> dict | None:
    """
    Mevcut bir kullanıcıyı kimlik doğrular (Giriş yapma).
    """
    user = users.get(username)
    if not user: return None

    # Kilitli hesap kontrolü
    if user.get("locked", False):
        print("Hata: Hesap, çok fazla başarısız deneme nedeniyle kilitlendi.")
        return None

    input_hash = hash_password(password) # Girilen parolayı hashle
    
    if input_hash == user["hashed_password"]: # Hash'leri karşılaştır
        # Başarılı Giriş
        user["last_login"] = datetime.now().isoformat()
        user["login_attempts"] = 0          # Başarılı girişte sayacı sıfırla
        save_users_to_file(USERS_FILE, users)
        return user 
    else:
        # Başarısız Giriş: Sayaç artırılır
        user["login_attempts"] = user.get("login_attempts", 0) + 1
        
        if user["login_attempts"] >= 3:
            user["locked"] = True # 3. başarısız denemede hesabı kilitler
            print("Uyarı: Çok fazla başarısız deneme! Hesap kilitlendi.")
            
        save_users_to_file(USERS_FILE, users) # Güncel deneme sayısını kaydet
        print(f"Giriş başarısız. Kalan deneme: {3 - user['login_attempts']}")
        return None
        
def logout_user(active_sessions: dict, username: str) -> None:
    """Kullanıcının oturumunu kapatır."""
    print(f"Kullanıcı '{username}' oturumu kapatıldı.")

# İlk olarak `hashlib` ve `datetime` kütüphanelerini içe aktardım. Ardından, kullanıcıları dosyaya kaydetmek için `file_manager.py` içindeki fonksiyonları ekledim.
# `hash_password` fonksiyonunda parolayı UTF-8’e çevirip SHA256 algoritmasıyla şifreledim. Sonra yeni kullanıcı kaydı için `register_user` fonksiyonunu yazdım;
#burada önce kullanıcı adı ve parolanın girilip girilmediğini kontrol ettim, kullanıcı adının önceden var olup olmadığını ve başlangıç bakiyesinin negatif olmadığını denetledim. Tüm bu kontroller geçerse,
#kullanıcının bilgilerini bir sözlük halinde topladım, parolasını hashledim, oluşturulma zamanını ekledim ve kullanıcıyı `users` sözlüğüne ekleyerek dosyaya kaydettim. Giriş işlemi için `login_user`
#fonksiyonunu yazarken önce kullanıcının var olup olmadığını kontrol ettim, ardından hesabın kilitli olup olmadığına baktım. Giriş yapan kişinin parolasını yeniden hashleyip sistemde kayıtlı hash’le
#karşılaştırdım; doğruysa son giriş zamanını güncelledim ve yanlışsa giriş deneme sayısını artırdım. Üç başarısız denemeden sonra hesabın otomatik olarak kilitlenmesini sağladım. Son olarak da 
#`logout_user` fonksiyonunda sadece oturum kapatan kullanıcının adını ekrana yazdırarak basit bir çıkış işlemi gerçekleştirdim. Bu adımların tamamı, sistemin düzgün çalışması ve
#güvenli olması için birbirini tamamlayacak şekilde tasarlandı.
