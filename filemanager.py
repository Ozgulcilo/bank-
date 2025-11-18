
BASE_DIR = 'data'
USERS_FILE = os.path.join(BASE_DIR, 'users.json')

def initialize_storage(base_dir: str) -> dict:
    """Gerekli depolama dizinlerini ve boş JSON dosyasını oluşturur."""
    try:
      # Ana veri dizinini oluşturur (exist_ok=True: Zaten varsa hata vermez)
        os.makedirs(base_dir, exist_ok=True) 
      # Yedekleme dizinini de oluşturur (Proje gereksinimi)
        os.makedirs(os.path.join(base_dir, 'backups'), exist_ok=True) 
      # Kullanıcılar dosyası mevcut değilse
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w') as f:
              # İçine boş bir JSON nesnesi yazar ({}). JSON başlatıyo
                json.dump({}, f)
        return {"status": "success"}
   
def load_data(users_path: str) -> dict:
    """Kullanıcı verilerini belirtilen JSON dosyasından yükler."""
    try:
        if not os.path.exists(users_path):
            return {} 
        with open(users_path, 'r') as f:
          # Dosyayı okur ve JSON'dan Python sözlüğüne dönüştürür
            return json.load(f) 
    except json.JSONDecodeError:
        print(f"Hata: {users_path} dosyası bozuk (geçersiz JSON).")
        return {} 
    except FileNotFoundError:
        return {}

def save_users_to_file(path: str, users: dict) -> None:
    """Kullanıcı sözlüğünü belirtilen yola JSON olarak kaydeder."""
    try:
      # 'w' modu ile dosyayı baştan yazar
      
        with open(path, 'w') as f:
            json.dump(users, f, indent=4) 
          # Okunabilirlik için girinti (indent=4) ile kaydeder
    except IOError as e:
        print(f"Hata: Kullanıcı verileri kaydedilemedi: {e}")
