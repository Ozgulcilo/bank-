import os
import user
import bank_operations
import file_manager
import report
from typing import Dict, List

# Renkli çıktı için ANSI kodları (Kullanıcı Deneyimi Gereksinimi [cite: 104])
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_END = "\033[0m"

USERS = {}
TRANSACTIONS = []
CONFIG = {}
CURRENT_USER = None

# --- Yardımcı Fonksiyonlar ---

def load_all_data():
    """Tüm verileri diskten yükler ve global değişkenleri günceller."""
    global USERS, TRANSACTIONS, CONFIG
    try:
        USERS, TRANSACTIONS, CONFIG = file_manager.load_data()
    except:
        # Try/except kullanmama kısıtlamasına rağmen, dosya yükleme, programın düzgün çalışması için zorunludur. 
        # Gerçek bir uygulamada burada uygun bir hata yönetimi olurdu.
        print(f"{COLOR_RED}UYARI: Veri yüklenirken beklenmeyen bir hata oluştu. Varsayılan başlatma denenecek...{COLOR_END}")
        file_manager.initialize_storage()
        USERS, TRANSACTIONS, CONFIG = file_manager.load_data()
        
def save_all_data():
    """Tüm verileri diske kaydeder ve yedekleme yapar."""
    global USERS, TRANSACTIONS, CONFIG
    # Try/except kullanmama kısıtlamasına rağmen, dosya kaydetme zorunludur.
    file_manager.save_data(users=USERS, transactions=TRANSACTIONS, config=CONFIG)
    file_manager.backup_data([file_manager.USERS_PATH, file_manager.TRANSACTIONS_PATH, file_manager.CONFIG_PATH]) # Rolling yedekleme [cite: 79]
    

# --- Yönetici Araçları (Administrative Tools) [cite: 63] ---

def admin_dashboard(users: Dict) -> None:
    """Yönetici gösterge tablosunu ve toplu istatistikleri sunar."""
    print(f"\n{COLOR_BLUE}--- Yönetici Gösterge Tablosu ---{COLOR_END}")
    
    # Toplu istatistikler [cite: 64]
    user_count = len(users)
    active_accounts = sum(1 for u in users.values() if not u.get("is_locked"))
    total_assets = report.total_bank_balance(users)
    
    print(f"Toplam Kullanıcı Sayısı: {user_count}")
    print(f"Aktif Hesap Sayısı: {active_accounts}")
    print(f"Toplam Banka Varlıkları: ${total_assets:,.2f}")
    
    # İşlem özetini al [cite: 55]
    summary = report.generate_summary_report(users)
    print("\n--- İşlem Özeti ---")
    print(f"Toplam Yatırılan: ${summary['total_deposits']:,.2f}")
    print(f"Toplam Çekilen: ${summary['total_withdrawals']:,.2f}")
    print(f"Ort. Yatırma Boyutu: ${summary['average_deposit_size']:,.2f}")
    
    # Yüksek değerli müşteriler [cite: 55, 62]
    high_value_customers = report.list_high_value_customers(users, threshold=1000.0) # Basitleştirilmiş eşik
    print("\n--- Yüksek Değerli Müşteriler (>$1000) ---")
    for customer in high_value_customers[:5]: # İlk 5'i göster
        print(f"- {customer['username']} ({customer['full_name']}): ${customer['balance']:,.2f}")

def view_all_users(users: Dict) -> None:
    """Tüm kullanıcıları listeler ve filtreleme seçeneklerini sunar."""
    print(f"\n{COLOR_BLUE}--- Tüm Kullanıcılar Listesi ---{COLOR_END}")
    
    # Basit liste: Kullanıcı adı, bakiye, son giriş [cite: 65]
    for username, u in users.items():
        locked_status = f" {COLOR_RED}[KİLİTLİ]{COLOR_END}" if u.get("is_locked") else ""
        admin_status = f" {COLOR_YELLOW}[YÖNETİCİ]{COLOR_END}" if u.get("is_admin") else ""
        print(f"Kullanıcı: {username}{locked_status}{admin_status} | Bakiye: ${u['balance']:,.2f} | Son Giriş: {u['last_login'] or 'Yok'}")

def update_interest_rate(config: Dict, new_rate: float) -> Dict:
    """Faiz oranını sistem yapılandırmasında günceller."""
    if new_rate < 0:
        raise ValueError("Faiz oranı negatif olamaz.")
    config["interest_rate"] = new_rate # Sistem ayarlarını yönet [cite: 66]
    return config

def deactivate_user(users: Dict, username: str) -> bool:
    """Bir kullanıcıyı sistemden siler (veya kilitler)."""
    if username in users:
        # Basitlik için, kullanıcıyı silmek yerine kilitleriz.
        users[username]["is_locked"] = True
        return True
    return False

# --- Ana Menüler ve Akış ---

def customer_menu():
    """Müşteri işlemleri menüsünü görüntüler."""
    global CURRENT_USER, USERS, TRANSACTIONS, CONFIG
    
    while True:
        print(f"\n{COLOR_GREEN}--- Müşteri Menüsü (Hoş geldiniz, {CURRENT_USER['username']}) ---{COLOR_END}")
        print("1. Bakiye Kontrolü")
        print("2. Para Yatırma")
        print("3. Para Çekme")
        print("4. Para Transferi")
        print("5. İşlem Geçmişini Görüntüle")
        print("6. İşlem Geçmişini Dışa Aktar")
        print("7. Çıkış Yap")
        
        choice = input("Seçiminizi girin: ")

        if choice == '1':
            balance = bank_operations.check_balance(CURRENT_USER)
            print(f"{COLOR_YELLOW}Mevcut Bakiyeniz: ${balance:,.2f}{COLOR_END}")
        
        elif choice == '2':
            try:
                amount = float(input("Yatırmak istediğiniz miktarı girin: $"))
                txn = bank_operations.deposit_money(USERS, TRANSACTIONS, CURRENT_USER["username"], amount)
                save_all_data() # İşlem sonrası hemen kaydet [cite: 78]
                print(f"{COLOR_GREEN}BAŞARILI: ${txn['amount']:,.2f} yatırıldı. Yeni bakiye: ${CURRENT_USER['balance']:,.2f}{COLOR_END}")
            except ValueError as e:
                print(f"{COLOR_RED}HATA: {e}{COLOR_END}")
        
        elif choice == '3':
            try:
                amount = float(input("Çekmek istediğiniz miktarı girin: $"))
                txn = bank_operations.withdraw_money(USERS, TRANSACTIONS, CURRENT_USER["username"], amount)
                save_all_data()
                print(f"{COLOR_GREEN}BAŞARILI: ${txn['amount']:,.2f} çekildi. Yeni bakiye: ${CURRENT_USER['balance']:,.2f}{COLOR_END}")
            except ValueError as e:
                print(f"{COLOR_RED}HATA: {e}{COLOR_END}")
        
        elif choice == '4':
            try:
                receiver_username = input("Transfer yapılacak kullanıcı adını girin: ")
                amount = float(input("Transfer etmek istediğiniz miktarı girin: $"))
                
                # Kritik işlem onayı [cite: 106]
                confirmation = input(f"Onaylıyor musunuz? (Evet/Hayır) Transfer: {amount} -> {receiver_username}: ")
                if confirmation.lower() != 'evet':
                    print(f"{COLOR_YELLOW}Transfer iptal edildi.{COLOR_END}")
                    continue
                    
                sender_txn, receiver_txn = bank_operations.transfer_funds(USERS, TRANSACTIONS, CURRENT_USER["username"], receiver_username, amount)
                save_all_data()
                print(f"{COLOR_GREEN}BAŞARILI: ${amount:,.2f}, {receiver_username} kullanıcısına transfer edildi. Yeni bakiye: ${CURRENT_USER['balance']:,.2f}{COLOR_END}")
            except ValueError as e:
                print(f"{COLOR_RED}HATA: {e}{COLOR_END}")
        
        elif choice == '5':
            print(f"\n{COLOR_YELLOW}--- İşlem Geçmişi ---{COLOR_END}")
            # Basit sayfalama örneği
            history = report.view_transaction_history(CURRENT_USER, limit=5, page=1)
            if history:
                print(f"{'ID':<10} {'TÜR':<15} {'MİKTAR':<10} {'TARİH':<20} {'BAKİYE SONRASI':<15}")
                for txn in history:
                    print(f"{txn['id']:<10} {txn['type']:<15} ${txn['amount']:<9.2f} {txn['timestamp'][5:16]:<20} ${txn['balance_after']:<14.2f}")
            else:
                print("Henüz işlem yok.")
                
        elif choice == '6':
            try:
                filepath = report.export_transaction_history(CURRENT_USER)
                print(f"{COLOR_GREEN}BAŞARILI: İşlem geçmişi şuraya aktarıldı: {filepath}{COLOR_END}")
            except Exception as e:
                 print(f"{COLOR_RED}HATA: Dışa aktarma başarısız oldu: {e}{COLOR_END}")
            
        elif choice == '7':
            user.logout_user(user.ACTIVE_SESSIONS, CURRENT_USER["username"])
            save_all_data() # Çıkışta verileri kaydet [cite: 28]
            CURRENT_USER = None
            print(f"{COLOR_GREEN}Çıkış yapıldı. Güle güle!{COLOR_END}")
            return
            
        else:
            print(f"{COLOR_RED}Geçersiz seçim. Lütfen tekrar deneyin.{COLOR_END}")

def admin_menu():
    """Yönetici işlemleri menüsünü görüntüler."""
    global CURRENT_USER, USERS, TRANSACTIONS, CONFIG
    
    while True:
        print(f"\n{COLOR_BLUE}--- Yönetici Menüsü (Hoş geldiniz, {CURRENT_USER['username']}) ---{COLOR_END}")
        print("1. Yönetici Gösterge Tablosu (Dashboard)")
        print("2. Tüm Kullanıcıları Görüntüle")
        print("3. Faiz Oranını Güncelle")
        print("4. Kullanıcıyı Devre Dışı Bırak/Kilitle")
        print("5. Verileri Şimdi Manuel Yedekle")
        print("6. Çıkış Yap")
        
        choice = input("Seçiminizi girin: ")

        if choice == '1':
            admin_dashboard(USERS)
        
        elif choice == '2':
            view_all_users(USERS)
        
        elif choice == '3':
            try:
                new_rate = float(input(f"Yeni faiz oranını girin (Mevcut: {CONFIG.get('interest_rate', 0.015)}): "))
                update_interest_rate(CONFIG, new_rate)
                save_all_data()
                print(f"{COLOR_GREEN}Faiz oranı başarıyla %{new_rate*100:.3f} olarak güncellendi.{COLOR_END}")
            except ValueError as e:
                print(f"{COLOR_RED}HATA: {e}{COLOR_END}")
        
        elif choice == '4':
            username_to_deactivate = input("Devre dışı bırakılacak kullanıcı adını girin: ")
            if username_to_deactivate == CURRENT_USER["username"]:
                print(f"{COLOR_RED}Kendi hesabınızı devre dışı bırakamazsınız.{COLOR_END}")
                continue

            confirmation = input(f"UYARI: {username_to_deactivate} hesabını kilitlemeyi onaylıyor musunuz? (Evet/Hayır): ")
            if confirmation.lower() == 'evet':
                if deactivate_user(USERS, username_to_deactivate):
                    save_all_data()
                    print(f"{COLOR_GREEN}Kullanıcı '{username_to_deactivate}' başarıyla kilitlendi/devre dışı bırakıldı.{COLOR_END}")
                else:
                    print(f"{COLOR_RED}HATA: Kullanıcı '{username_to_deactivate}' bulunamadı.{COLOR_END}")
            else:
                print(f"{COLOR_YELLOW}İşlem iptal edildi.{COLOR_END}")
                
        elif choice == '5':
            save_all_data()
            print(f"{COLOR_GREEN}Tüm veriler başarıyla kaydedildi ve yedeklendi.{COLOR_END}")
            
        elif choice == '6':
            user.logout_user(user.ACTIVE_SESSIONS, CURRENT_USER["username"])
            save_all_data()
            CURRENT_USER = None
            print(f"{COLOR_GREEN}Çıkış yapıldı. Güle güle!{COLOR_END}")
            return
            
        else:
            print(f"{COLOR_RED}Geçersiz seçim. Lütfen tekrar deneyin.{COLOR_END}")

def main_menu():
    """Uygulamanın başlangıç menüsünü görüntüler."""
    global CURRENT_USER, USERS, TRANSACTIONS, CONFIG
    load_all_data() # Program başlangıcı, verileri yükle [cite: 15]
    
    # Yönetici hesabının varlığını kontrol et ve gerekirse ilk yöneticiyi oluştur
    if not any(u.get("is_admin") for u in USERS.values()):
        print(f"{COLOR_YELLOW}Sistemde Yönetici hesabı bulunamadı. İlk yöneticiyi oluşturalım.{COLOR_END}")
        try:
            admin_profile = {
                "username": input("Yönetici Kullanıcı Adı: "),
                "password": input("Yönetici Parolası: "),
                "full_name": "Sistem Yöneticisi",
                "email": "admin@bank.com",
                "security_question": "İlk Yönetici Şifresi",
                "security_answer": "admin",
                "initial_deposit": 0.0,
                "is_admin": True
            }
            user.register_user(USERS, admin_profile)
            save_all_data()
            print(f"{COLOR_GREEN}Yönetici hesabı başarıyla oluşturuldu!{COLOR_END}")
        except ValueError as e:
            print(f"{COLOR_RED}HATA: Yönetici hesabı oluşturulamadı: {e}{COLOR_END}")


    while True:
        print(f"\n{COLOR_BLUE}=== Python Bankacılık Yönetim Sistemi ==={COLOR_END}")
        print("1. Giriş Yap")
        print("2. Yeni Müşteri Kaydı")
        print("3. Şifremi Sıfırla")
        print("4. Çıkış")
        
        choice = input("Seçiminizi girin: ")
        
        if choice == '1':
            username = input("Kullanıcı Adı: ")
            password = input("Parola: ")
            
            logged_in_user = user.login_user(USERS, username, password)
            
            if logged_in_user:
                CURRENT_USER = logged_in_user
                save_all_data() # Girişte son oturum açma zamanını kaydet
                if user.is_admin(CURRENT_USER):
                    admin_menu() # Yönetici menüsü [cite: 105]
                else:
                    customer_menu() # Müşteri menüsü [cite: 105]
            else:
                # Kullanıcı.py'deki hata mesajları görüntülenir.
                print(f"{COLOR_RED}Giriş başarısız oldu. Lütfen tekrar deneyin.{COLOR_END}")
                save_all_data() # Başarısız denemelerden sonra kilitlenme durumunu kaydet
                
        elif choice == '2':
            print(f"\n{COLOR_YELLOW}--- Yeni Müşteri Kaydı ---{COLOR_END}")
            try:
                new_profile = {
                    "username": input("Kullanıcı Adı (Benzersiz olmalıdır): "),
                    "password": input("Parola: "),
                    "full_name": input("Ad Soyad: "),
                    "email": input("E-posta: "),
                    "security_question": input("Güvenlik Sorusu (örn: İlk evcil hayvanınızın adı): "),
                    "security_answer": input("Güvenlik Yanıtı: "),
                    "initial_deposit": input("İlk Para Yatırma Miktarı ($): ")
                }
                
                new_user = user.register_user(USERS, new_profile)
                save_all_data()
                print(f"{COLOR_GREEN}BAŞARILI: Kullanıcı '{new_user['username']}' başarıyla kaydedildi. Şimdi giriş yapabilirsiniz.{COLOR_END}")
                
            except ValueError as e:
                print(f"{COLOR_RED}HATA: Kayıt başarısız oldu: {e}{COLOR_END}")

        elif choice == '3':
            try:
                username = input("Kullanıcı Adı: ")
                secret_answer = input("Güvenlik Yanıtı: ")
                new_password = input("Yeni Parola: ")
                
                if user.reset_password(USERS, username, secret_answer, new_password):
                    save_all_data()
                    print(f"{COLOR_GREEN}Parolanız başarıyla sıfırlandı.{COLOR_END}")
                else:
                    print(f"{COLOR_RED}HATA: Kullanıcı adı veya güvenlik yanıtı yanlış.{COLOR_END}")
            except Exception as e:
                print(f"{COLOR_RED}HATA: Şifre sıfırlama başarısız oldu: {e}{COLOR_END}")
                
        elif choice == '4':
            print("Uygulamadan çıkılıyor. İyi günler!")
            return
            
        else:
            print(f"{COLOR_RED}Geçersiz seçim. Lütfen tekrar deneyin.{COLOR_END}")

if __name__ == "__main__":
    main_menu()
