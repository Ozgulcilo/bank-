
#USER

import file_manager

def register_user(users, username, password, full_name):
    """Sisteme yeni bir müşteri kaydeder."""
    
    # 1. Kullanıcı adı kontrolü (Aynı isimde iki kişi olamaz)
    if username in users:
        print("Hata: Bu kullanıcı adı zaten alınmış!")
        return False

    # 2. Yeni kullanıcı bilgilerini oluştur (Başlangıç parası: 0)
    new_user = {
        "username": username,
        "password": password,  
        "full_name": full_name,
        "balance": 0.0,
        "transactions": [] # İşlem geçmişi boş başlar
    }

    # 3. Listeye ekle
    users[username] = new_user
    print(f"Hoş geldiniz {full_name}! Kaydınız başarıyla oluşturuldu.")
    return True

def login_user(users, username, password):
    """Kullanıcı adı ve şifreyi kontrol ederek giriş yaptırır."""
    
    # Sözlükte böyle bir kullanıcı var mı diye bakar yoksa user değişkeni
    #none kalır
    user = users.get(username)
    
    if user and user["password"] == password:
        print(f"Giriş başarılı! Tekrar hoş geldin, {user['full_name']}.")
        return user  # Giriş yapan kullanıcıyı geri döndür
    else:
        print("Hata: Kullanıcı adı veya şifre yanlış!")
        return None
# Bu fonksiyon kullanıcı adı ve şifreyi eşleştirir. 
# Bilgiler doğruysa kullanıcı paketini (user) döndürür, yanlışsa None (boş) döndürür.
