import file_manager
import user
import bank_operations

def main_menu_loop():
 # Veri durumu (current_users_data ve current_active_user) yerel olarak tutoyoer
 current_users_data = {}
 current_active_user = None

 try:
  current_users_data = file_manager.load_data()
 except:

  print("UYARI: İlk çalıştırma. Boş veri ile devam ediliyor.")
  file_manager.setup_storage()
  current_users_data = file_manager.load_data()


 while True:
  if current_active_user:
   print("\n## Hesap Menüsü ##")
   print("1. Bakiye Görüntüle")
   print("2. Para Yatır")
   print("3. Para Çek")
   print("4. Çıkış Yap")
   choice = input("Seçim: ")
   
   if choice == '1':
    bank_operations.check_balance(current_active_user)
   elif choice == '2':
    amount_str = input("Yatırılacak tutar: ")
    amount_float = float(amount_str) 
    current_users_data = bank_operations.deposit_money(current_users_data, current_active_user, amount_float)
    file_manager.save_data(current_users_data)
   elif choice == '3':
    amount_str = input("Çekilecek tutar: ")
    amount_float = float(amount_str) 
    current_users_data = bank_operations.withdraw_money(current_users_data, current_active_user, amount_float)
    file_manager.save_data(current_users_data)
   elif choice == '4':
    file_manager.save_data(current_users_data)
    current_active_user = None
    print("Oturum kapatıldı.")
   else:
    print("Geçersiz seçim.")
  
  else:
   print("\n## Giriş Menüsü ##")
   print("1. Giriş Yap")
   print("2. Kayıt Ol")
   print("3. Çıkış")
   choice = input("Seçim: ")
   
   if choice == '1':
    u = input("Kullanıcı Adı: ")
    p = input("Şifre: ")
    current_users_data, logged_in_user = user.login_user(current_users_data, u, p)
    current_active_user = logged_in_user
    file_manager.save_data(current_users_data)
   elif choice == '2':
    u = input("Yeni Kullanıcı Adı: ")
    p = input("Şifre: ")
    f = input("Ad Soyad: ")
    i_str = input("Başlangıç Depozitosu: ")
    i_float = float(i_str) 
    
    current_users_data, success = user.register_user(current_users_data, u, p, f, i_float)
    if success:
     file_manager.save_data(current_users_data)
   elif choice == '3':
    print("Programdan çıkılıyor.")
    break
   else:
    print("Geçersiz seçim.")

if __name__ == "__main__":
 main_menu_loop()
