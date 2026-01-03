
#REPORT

def show_user_history(transactions, username):
    """Belirli bir kullanıcının geçmiş işlemlerini listeler."""
    print(f" {username} İÇİN İŞLEM GEÇMİŞİ ---")
    
    found = False
    # Tüm işlem defterini (transactions listesini) tek tek geziyoruz
    for txn in transactions:
        # Eğer işlemin sahibi bizim kullanıcımız ise ekrana yazdır
        if txn["username"] == username:
            print(f"[{txn['date']}] {txn['type'].upper()}: {txn['amount']} TL - {txn['description']}")
            found = True
    
    if not found:
        print("Henüz bir işlem kaydınız bulunmuyor.")

def show_summary(user):
    """Kullanıcının mevcut durumunu özetler."""
    print("--- HESAP ÖZETİ ---")
    print(f"İsim: {user['full_name']}")
    print(f"Güncel Bakiye: {user['balance']} TL")
