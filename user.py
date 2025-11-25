def register_user(users_data, username, password, full_name, initial_deposit):
 # users_data'yı günceller ve güncel users_data'yı döndürür.
 if username in users_data:
  print("Hata: Bu kullanıcı adı zaten mevcut.")
  return users_data, False

 if initial_deposit >= 0:
  new_user = {
   "username": username,
   "password": password, 
   "full_name": full_name,
   "balance": float(initial_deposit),
   "is_locked": False,
   "failed_attempts": 0,
   "transactions": []
  }
  users_data[username] = new_user
  print(f"Kayıt başarılı. Hoş geldiniz, {full_name}!")
  return users_data, True
 else:
  print("Hata: Başlangıç depozitosu negatif olamaz.")
  return users_data, False


def login_user(users_data, username, password):
 # users_data'yı ve aktif kullanıcıyı (sözlük) döndürür.
 user_data = users_data.get(username)
 
 if user_data:
  if user_data["is_locked"] == False:
   if user_data["password"] == password:
    user_data["failed_attempts"] = 0
    print(f"Giriş başarılı. Hoş geldiniz, {user_data['full_name']}!")
    return users_data, user_data
   else:
    user_data["failed_attempts"] += 1
    print("Hata: Yanlış şifre.")
    
    if user_data["failed_attempts"] >= 3:
     user_data["is_locked"] = True
     print("Uyarı: Hesap kilitlenmiştir.")
    
    return users_data, None 
  else:
   print("Hata: Hesap kilitli.")
   return users_data, None
 else:
  print("Hata: Kullanıcı bulunamadı.")
  return users_data, None
