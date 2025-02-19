import requests
import os
import sys
import json
import hashlib

# GitHub Repo Bilgileri
REPO_OWNER = "Ahmettcakar"
REPO_NAME = "pyqt5-auto-update-example"
BRANCH = "main"

# GitHub'daki ham (raw) içeriklere erişim URL'si
RAW_BASE_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/"
GITHUB_VERSION_URL = f"{RAW_BASE_URL}version.json"

def get_base_dir():
    """Çalışan dizini bulur (exe veya python ortamına göre)."""
    if getattr(sys, 'frozen', False):  # Eğer .exe olarak çalışıyorsa
        return os.path.dirname(sys.executable)  # .exe'nin olduğu klasör
    return os.path.dirname(os.path.abspath(__file__))  # Normal Python dizini

BASE_DIR = get_base_dir()
VERSION_FILE = os.path.join(BASE_DIR, "version.json")
LOG_FILE = os.path.join(BASE_DIR, "log.txt")

def log_and_print(message):
    """Mesajı hem ekrana yazdırır hem de log.txt dosyasına kaydeder."""
    print(message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception:
        pass  # Log dosyasına yazılamadıysa programı durdurmayalım

def get_file_hash(file_name):
    """Dosyanın SHA-256 hash'ini hesaplar."""
    file_path = os.path.join(BASE_DIR, file_name)

    if not os.path.exists(file_path):
        log_and_print(f"Hata: {file_name} bulunamadı!")
        return None

    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def load_local_version():
    """Yerel version.json dosyasını oku."""
    try:
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        log_and_print("Yerel version.json bulunamadı, varsayılan değerlere geçiliyor.")
        return {"version": "Bilinmiyor", "files": {}}
    except json.JSONDecodeError:
        log_and_print("Hata: version.json bozuk veya JSON hatası var.")
        return {"version": "Bilinmiyor", "files": {}}

def load_remote_version():
    """GitHub’daki version.json dosyasını indir."""
    try:
        response = requests.get(GITHUB_VERSION_URL)
        if response.status_code == 200:
            return response.json()
        else:
            log_and_print(f"❌ Hata! GitHub'daki version.json alınamadı. Status Code: {response.status_code}")
            return None
    except Exception as e:
        log_and_print(f"⚠️ İndirme hatası (version.json): {str(e)}")
        return None

def download_file_from_github(file_name):
    """GitHub'dan dosyayı indir ve kaydet."""
    download_url = f"{RAW_BASE_URL}{file_name}"

    log_and_print(f"🌍 GitHub'dan indiriliyor: {file_name}")

    try:
        response = requests.get(download_url)

        if response.status_code == 200:
            file_path = os.path.join(BASE_DIR, file_name)
            with open(file_path, "wb") as f:
                f.write(response.content)

            log_and_print(f"✅ {file_name} başarıyla indirildi ve kaydedildi.")
            return True
        elif response.status_code == 404:
            log_and_print(f"❌ GitHub'da {file_name} bulunamadı! URL yanlış olabilir.")
            return False
        else:
            log_and_print(f"❌ GitHub'dan {file_name} alınamadı! Hata kodu: {response.status_code}")
            return False

    except Exception as e:
        log_and_print(f"⚠️ İndirme sırasında hata oluştu: {e}")
        return False

def download_updates():
    """SHA değişen dosyaları indir ve version.json'u güncelle."""
    try:
        remote_version = load_remote_version()
        if not remote_version:
            log_and_print("🚫 Güncelleme kontrolü başarısız oldu (remote_version alınamadı).")
            return False

        local_version = load_local_version()
        new_version = {"version": remote_version["version"], "files": local_version["files"].copy()}

        guncel_mi = True
        for file_name, remote_hash in remote_version["files"].items():
            local_hash = local_version["files"].get(file_name, "")

            if remote_hash != local_hash:
                guncel_mi = False
                log_and_print(f"📥 Güncellenmesi gereken dosya: {file_name}")

                if download_file_from_github(file_name):
                    new_file_hash = get_file_hash(file_name)
                    if new_file_hash:
                        new_version["files"][file_name] = new_file_hash
                        log_and_print(f"✅ {file_name} güncellendi. Yeni SHA-256: {new_file_hash}")

                        # Version.json'ı güncelle
                        with open(VERSION_FILE, "w", encoding="utf-8") as f:
                            json.dump(new_version, f, indent=4)
                            log_and_print(f"✅ version.json kaydedildi. Yeni SHA: {new_version}")
                    else:
                        log_and_print(f"❌ {file_name} indirildi ama SHA hesaplanamadı!")

                else:
                    log_and_print(f"❌ {file_name} indirilemedi!")

        if guncel_mi:
            log_and_print("✔️ Program zaten güncel, güncelleme yapılmadı.")
            return True
        else:
            log_and_print("✅ Güncelleme tamamlandı!")
            return False

    except Exception as e:
        log_and_print(f"⚠️ Güncelleme sırasında hata oluştu: {e}")
        return False
    