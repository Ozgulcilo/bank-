
#MAIN

import user            # user.py dosyasından giriş/kayıt araçlarını getirir
import bank_operations # Para işlemleri araçlarını getirir
import file_manager    # Kayıt/yükleme araçlarını getirir
import report       #Geçmişi listele

def main():
    # 1. Verileri dosyadan yükle (Kullanıcılar, İşlemler, Ayarlar)
    users, transactions, config = file_manager.load_data()

    print("--- BANKA SİSTEMİNE HOŞ GELDİNİZ ---")
    
    hak = 3  # Hatalı giriş hakkı sayısı
    aktif_kullanici = None

    # GİRİŞ EKRANI
    while hak > 0:
        print(f"\nKalan Giriş Hakkı: {hak}")
        u_name = input("Kullanıcı Adı: ")
        p_word = input("Şifre: ")

        # user.py içindeki login_user fonksiyonunu kullanıyoruz
        aktif_kullanici = user.login_user(users, u_name, p_word)

        if aktif_kullanici:
            break  # Giriş başarılıysa döngüden çık
        else:
            hak -= 1
    
    if hak == 0:
        print("Hakkınız bitti. Sistem kapatılıyor!")
        return

    # İŞLEM MENÜSÜ
    while True:
        print(f"\n--- Hoş Geldiniz, {aktif_kullanici['full_name']} ---")
        print("1. Bakiye Sorgula")
        print("2. Para Yatır")
        print("3. Para Çek")
        print("4. İşlem Geçmişini Gör")
        print("5. Çıkış")
        
        secim = input("Seçiminiz: ")

        if secim == "1":
            # bank_operations içindeki check_balance fonksiyonu
            b = bank_operations.check_balance(aktif_kullanici)
            print(f"Bakiyeniz: {b} TL")

        elif secim == "2":
            m miktar = float(input("Miktar: "))
            bank_operations.deposit_money(users, transactions, aktif_kullanici["username"], miktar)
            file_manager.save_data(users, transactions, config) # Değişikliği kaydet

        elif secim == "3":
            miktar = float(input("Miktar: "))
            bank_operations.withdraw_money(users, transactions, aktif_kullanici["username"], miktar)
            file_manager.save_data(users, transactions, config) # Değişikliği kaydet
        elif secim == "4":
             # report.py içindeki fonksiyonu çağırıyoruz
             report.show_user_history(transactions, aktif_kullanici["username"])
        elif secim == "5":
            print("Çıkış yapıldı.")
            break
        else:
            print("Hatalı seçim!")

if __name__ == "__main__":
    main()
