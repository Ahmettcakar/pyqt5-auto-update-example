import requests
import os
import sys
import json
import hashlib

# GitHub Token ve Repo Bilgileri
GITHUB_TOKEN = "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"
REPO_OWNER = "Ahmettcakar"
REPO_NAME = "pyqt5-auto-update-example"
BRANCH = "main"

# GitHub API URL'leri
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/"
GITHUB_VERSION_URL = f"{RAW_BASE_URL}version.json"

headers = {"Authorization": f"token {GITHUB_TOKEN}"}


def get_base_dir():
    """PyInstaller ile .exe çalıştırıldığında doğru dizini bulur."""
    if getattr(sys, 'frozen', False):  # Eğer .exe olarak çalışıyorsa
        return os.path.dirname(sys.executable)  # .exe'nin olduğu klasör
    return os.path.dirname(os.path.abspath(__file__))  # Normal Python dizini


BASE_DIR = get_base_dir()
print("test guncel")
VERSION_FILE = os.path.join(BASE_DIR, "version.json")
LOG_FILE = os.path.join(BASE_DIR, "log.txt")


def log_and_print(message):
    """Mesajı hem ekrana yazdırır hem de log.txt dosyasına kaydeder."""
    print(message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception:
        # Log dosyasına yazılamadıysa programı durdurmayalım, pas geçiyoruz.
        pass


# Program çalışınca ilk olarak kritik yolları loglayalım
log_and_print(f"=== Uygulama Başladı ===")
log_and_print(f"BASE_DIR: {BASE_DIR}")
log_and_print(f"VERSION_FILE: {VERSION_FILE}")
log_and_print(f"LOG_FILE: {LOG_FILE}")


def get_file_hash(file_name):
    """Dosyanın SHA-256 hash'ini hesaplar ve doğru yoldan okur."""
    file_path = os.path.join(BASE_DIR, file_name)

    if not os.path.exists(file_path):
        log_and_print(f"[get_file_hash] Hata: {file_name} bulunamadı! Path: {file_path}")
        return None

    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sha256.update(chunk)
    calculated_hash = sha256.hexdigest()
    log_and_print(f"[get_file_hash] {file_name} için hesaplanan SHA-256: {calculated_hash}")
    return calculated_hash


def load_local_version():
    """Yerel version.json dosyasını oku."""
    try:
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            local_ver = json.load(f)
        log_and_print(f"[load_local_version] Yerel version.json başarıyla okundu: {json.dumps(local_ver, indent=2)}")
        return local_ver
    except FileNotFoundError:
        log_and_print("[load_local_version] Uyarı: Yerel version.json bulunamadı, varsayılan değerlere geçiliyor.")
        return {"version": "Bilinmiyor", "files": {}}
    except json.JSONDecodeError:
        log_and_print("[load_local_version] Hata: version.json bozuk veya JSON hatası var.")
        return {"version": "Bilinmiyor", "files": {}}


def load_remote_version():
    """GitHub’daki version.json dosyasını indir ve oku."""
    try:
        log_and_print(f"[load_remote_version] GET => {GITHUB_VERSION_URL}")
        response = requests.get(GITHUB_VERSION_URL, headers=headers)
        if response.status_code == 200:
            remote_ver = response.json()
            log_and_print(f"[load_remote_version] Uzak version.json başarıyla alındı:\n{json.dumps(remote_ver, indent=2)}")
            return remote_ver
        else:
            log_and_print(f"[load_remote_version] Hata! GitHub'daki version.json alınamadı. Status Code: {response.status_code}")
            return None
    except Exception as e:
        log_and_print(f"[load_remote_version] İndirme hatası (version.json): {str(e)}")
        return None


def download_updates():
    """Sadece SHA değişen dosyaları indir ve version.json'u güncelle."""
    try:
        log_and_print("[download_updates] Güncelleme kontrolü başlatıldı...")
        remote_version = load_remote_version()
        if not remote_version:
            log_and_print("[download_updates] Güncelleme kontrolü başarısız oldu (remote_version alınamadı).")
            return False

        local_version = load_local_version()

        # Yeni version sözlüğü (remote_version'un version alanını kullanıp, localdeki files'ı kopyalıyoruz)
        new_version = {
            "version": remote_version["version"],
            "files": local_version["files"].copy()
        }

        guncel_mi = True

        for file_name, remote_hash in remote_version["files"].items():
            local_hash = local_version["files"].get(file_name, "")
            log_and_print(f"[download_updates] Kontrol ediliyor: {file_name}")
            log_and_print(f"  - Local Hash: {local_hash}")
            log_and_print(f"  - Remote Hash: {remote_hash}")

            # Eğer SHA değerleri farklıysa veya dosya yoksa, güncelle
            if remote_hash != local_hash:
                guncel_mi = False
                download_url = f"{RAW_BASE_URL}{file_name}"
                log_and_print(f"[download_updates] => SHA farkı var veya dosya yok. İndiriliyor: {file_name}")
                log_and_print(f"  - Download URL: {download_url}")

                response = requests.get(download_url, headers=headers)
                if response.status_code == 200:
                    file_path = os.path.join(BASE_DIR, file_name)
                    log_and_print(f"  - Kaydedilecek Yol: {file_path}")
                    with open(file_path, "wb") as f:
                        f.write(response.content)

                    # Yeni dosyanın SHA hash'ini hesapla ve version.json'a ekle
                    new_file_hash = get_file_hash(file_name)
                    new_version["files"][file_name] = new_file_hash if new_file_hash else ""
                    log_and_print(f"[download_updates] {file_name} başarıyla güncellendi.")
                else:
                    log_and_print(f"[download_updates] Dosya indirilemedi: {file_name}, Hata kodu: {response.status_code}")

        if not guncel_mi:
            # Güncellenmiş version.json'ı kaydet
            with open(VERSION_FILE, "w", encoding="utf-8") as f:
                json.dump(new_version, f, indent=4)
            log_and_print("[download_updates] version.json güncellendi, yeni SHA değerleri kaydedildi.")
            log_and_print("[download_updates] Güncelleme işlemi tamamlandı. (return False)")
            return False
        else:
            log_and_print("[download_updates] Program zaten güncel, güncelleme yapılmadı. (return True)")
            return True

    except Exception as e:
        log_and_print(f"[download_updates] İndirme/güncelleme sırasında hata oluştu: {str(e)}")
        return False
