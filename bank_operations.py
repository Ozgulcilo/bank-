def record_transaction(user_data, type_name, amount, channel="Şube"):
  
 transaction = {
  "type": type_name,
  "amount": amount,
  "balance_after": user_data["balance"],
  "timestamp": "Tarih Bilgisi Yok", 
  "notes": f"Kanal: {channel}"
 }
 user_data["transactions"].append(transaction)
 
def deposit_money(users_data, active_user, amount, channel="Şube"):
 # users_data'yı günceller ve döndürür.
 if amount > 0:
  active_user["balance"] += amount
  record_transaction(active_user, "deposit", amount, channel)
  users_data[active_user["username"]] = active_user 
  print(f"Yatırma başarılı. Yeni bakiyeniz: {active_user['balance']:.2f}")
  return users_data
 else:
  print("Hata: Tutar pozitif olmalıdır.")
  return users_data

def withdraw_money(users_data, active_user, amount, channel="Şube", min_balance=0.0):
 # users_data'yı günceller ve döndürür.
 if amount > 0:
  if active_user["balance"] >= amount + min_balance:
   active_user["balance"] -= amount
   record_transaction(active_user, "withdrawal", amount, channel)
   users_data[active_user["username"]] = active_user 
   print(f"Çekme başarılı. Yeni bakiyeniz: {active_user['balance']:.2f}")
   return users_data
  else:
   print("Hata: Yetersiz bakiye.")
   return users_data
 else:
  print("Hata: Tutar pozitif olmalıdır.")
  return users_data

def check_balance(active_user):
 print(f"Mevcut Bakiyeniz: {active_user['balance']:.2f}")
