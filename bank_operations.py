from datetime import datetime
import file_manager

# --- YARDIMCI FONKSİYONLAR ---

def generate_transaction_id(transactions):
  """
Her işleme benzersiz bir ID numarası verir.
Mantık: Mevcut işlem sayısına 1 ekleyerek her seferinde yeni bir numara üretir.
Liste uzunluğuna 1 ekler ve başına TXN- koyar (Örn: TXN-00001)
  """
    return f"TXN-{len(transactions) + 1:05d}" 

def record_transaction(transactions, user, transaction_type, amount, channel, notes):
    """Yapılan işlemi hem genel listeye hem kullanıcı geçmişine kaydeder."""
    
    # İşlem bilgilerini bir paket (sözlük) haline getiriyoruz
    new_txn = {
        "id": generate_transaction_id(transactions),
        "type": transaction_type,
        "amount": amount,
        "balance_after": user["balance"],
        #user' adlı sözlüğün içindeki
# 'balance' anahtarına ait değeri çekip çıkarmak için kullanılır.
        "timestamp": datetime.now().isoformat(),
        # datetime.now().isoformat() : İşlemin yapıldığı anı (Yıl-Ay-Gün Saat:Dakika)
# dünya standartlarında bir metin olarak kaydeder. Örn: 2025-05-20T14:30:00
        "notes": notes,
        "username": user["username"],
        "channel": channel
    }
    
    # Bankanın tüm işlemlerinin olduğu listeye ekle
    transactions.append(new_txn)
    
    # Kullanıcının kendi özel geçmişine ekle
    user["transactions"].append(new_txn)
    
    return new_txn

# --- ANA BANKACILIK FONKSİYONLARI ---

def check_balance(user):
    """Kullanıcının o anki parasını gösterir."""
    return user.get("balance", 0.0)#"balance" bilgisini ara; bulamazsa 0 kabul et.

def deposit_money(users, transactions, username, amount, channel="branch"):
    """Hesaba para yatırır."""
    user = users.get(username)
    if not user:
        print("Hata: Kullanıcı bulunamadı!")
        return

    if amount <= 0:
        print("Hata: Yatırılacak tutar 0'dan büyük olmalı!")
        return

    # Bakiyeyi güncelle
    user["balance"] += amount
    
    # Kaydı oluştur
    record_transaction(transactions, user, "deposit", amount, channel, "Para Yatırma")
    print(f"{amount} TL başarıyla yatırıldı.")

def withdraw_money(users, transactions, username, amount, channel="branch"):
    """Hesaptan para çeker."""
    user = users.get(username)
    if not user:
        print("Hata: Kullanıcı bulunamadı!")
        return

    if amount <= 0:
        print("Hata: Çekilecek tutar 0'dan büyük olmalı!")
        return
        
    # Ayarları dosyadan oku (Minimum bakiye kontrolü için)
    # file_manager içinden sadece gerekli olan config kısmını alıyoruz
    veriler = file_manager.load_data()
    config = veriler[2] # 3. sıradaki bilgi ayarlar (config)
    min_bakiye = config["min_balance"]
    # config: Bankanın çalışma kurallarını (limitler, faiz oranları vb.)
# içeren "Ayarlar" bölümüdür. Kodun dışından kolayca değiştirilebilir.

    # Yetersiz bakiye kontrolü
    if user["balance"] - amount < min_bakiye:
        print(f"Hata: Yetersiz bakiye! En az {min_bakiye} TL kalmalı.")
        return

    # Bakiyeyi düşür ve kaydet
    user["balance"] -= amount
    record_transaction(transactions, user, "withdrawal", amount, channel, "Para Çekme")
    print(f"{amount} TL başarıyla çekildi.")

def transfer_funds(users, transactions, gonderen_ad, alici_ad, miktar):
    """Bir hesaptan diğerine para gönderir."""
    gonderen = users.get(gonderen_ad)
    alici = users.get(alici_ad)
    
    if not gonderen or not alici:
        print("Hata: Kullanıcılardan biri bulunamadı!")
        return

    if miktar <= 0:
        print("Hata: Geçersiz miktar!")
        return

    if gonderen["balance"] < miktar:
        print("Hata: Gönderen bakiyesi yetersiz!")
        return

    # Parayı birinden düş, diğerine ekle
    gonderen["balance"] -= miktar
    alici["balance"] += miktar
    
    # Her iki taraf için de dekont/kayıt oluştur
    record_transaction(transactions, gonderen, "transfer_out", miktar, "Transfer", f"{alici_ad} kişisine gönderildi")
    record_transaction(transactions, alici, "transfer_in", miktar, "Transfer", f"{gonderen_ad} kişisinden geldi")
    
    print(f"{miktar} TL transfer başarıyla tamamlandı.")
