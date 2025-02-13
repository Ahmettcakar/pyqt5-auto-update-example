import requests
import os
import sys
import json
import hashlib
import logging

# LOG DOSYASI AYARI
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# GitHub Repo Bilgileri
GITHUB_TOKEN = "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"  # Özel token, repo private ise gerekli
REPO_OWNER = "Ahmettcakar"
REPO_NAME = "pyqt5-auto-update-example"
BRANCH = "main"

# GitHub API URL'leri
GITHUB_VERSION_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/version.json"

headers = {"Authorization": f"token {GITHUB_TOKEN}"}

print("test")
# LOG DOSYASI YOLUNU EXE'NİN BULUNDUĞU KLASÖRE AYARLA
def get_base_dir():
    """Çalışan dizini bulur (exe veya python ortamına göre)"""
    if getattr(sys, 'frozen', False):  # Eğer .exe olarak çalışıyorsa
        return os.path.dirname(sys.executable)  # .exe'nin olduğu klasör
    return os.path.dirname(os.path.abspath(__file__))  # Normal Python dizini

BASE_DIR = get_base_dir()
LOG_FILE = os.path.join(BASE_DIR, "app.log")  # Log dosyası exe'nin olduğu klasörde olacak

# LOGGING AYARI
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("🚀 Güncelleyici başlatıldı. Log dosyası oluşturuldu!")

VERSION_FILE = os.path.join(BASE_DIR, "version.json")


def get_file_hash(file_name):
    """Dosyanın SHA-256 hash'ini hesaplar ve log kaydı tutar."""
    file_path = os.path.join(BASE_DIR, file_name)

    if not os.path.exists(file_path):
        logging.warning(f"{file_name} bulunamadı!")
        return None

    try:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logging.error(f"{file_name} hash hesaplanırken hata oluştu: {e}")
        return None


def load_local_version():
    """Yerel version.json dosyasını oku ve log kaydı tut."""
    try:
        with open(VERSION_FILE, "r") as f:
            logging.info("Yerel version.json başarıyla okundu.")
            return json.load(f)
    except FileNotFoundError:
        logging.warning("Yerel version.json bulunamadı, varsayılan değerler kullanılacak.")
        return {"version": "Bilinmiyor", "files": {}}
    except json.JSONDecodeError:
        logging.error("Yerel version.json bozuk! JSON formatı hatalı.")
        return {"version": "Bilinmiyor", "files": {}}


def load_remote_version():
    """GitHub’daki version.json dosyasını indir ve oku."""
    try:
        response = requests.get(GITHUB_VERSION_URL, headers=headers)
        if response.status_code == 200:
            logging.info("GitHub'dan version.json başarıyla alındı.")
            return response.json()
        else:
            logging.error(f"GitHub'daki version.json alınamadı. Status Code: {response.status_code}")
            return None
    except Exception as e:
        logging.exception(f"İndirme hatası: {e}")
        return None


def download_updates():
    """SHA değişen dosyaları indir ve güncelle. Loglarla detaylı bilgi ver."""
    try:
        logging.info("🚀 Güncelleme kontrolü başlatıldı...")
        remote_version = load_remote_version()
        if not remote_version:
            logging.warning("❌ Güncelleme kontrolü başarısız oldu. (remote_version alınamadı!)")
            return False

        local_version = load_local_version()
        new_version = {"version": remote_version["version"], "files": local_version["files"].copy()}

        guncel_mi = True
        for file_name, remote_hash in remote_version["files"].items():
            local_hash = local_version["files"].get(file_name, "")

            if remote_hash != local_hash:
                guncel_mi = False
                download_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{file_name}"
                logging.info(f"🔄 Güncellenmesi gereken dosya tespit edildi: {file_name}")

                response = requests.get(download_url, headers=headers)
                if response.status_code == 200:
                    file_path = os.path.join(BASE_DIR, file_name)
                    with open(file_path, "wb") as f:
                        f.write(response.content)

                    new_version["files"][file_name] = get_file_hash(file_name)
                    logging.info(f"✅ {file_name} başarıyla güncellendi.")
                else:
                    logging.error(f"❌ {file_name} indirilemedi, HTTP Status: {response.status_code}")

            else:
                logging.info(f"🔍 {file_name} zaten güncel, güncellenmeyecek.")

        if not guncel_mi:
            with open(VERSION_FILE, "w") as f:
                json.dump(new_version, f, indent=4)
            logging.info("✅ version.json güncellendi ve yeni SHA-256 hash'ler kaydedildi.")
            return False
        else:
            logging.info("✔️ Program zaten güncel, güncelleme yapılmadı.")
            return True

    except Exception as e:
        logging.exception(f"❌ Güncelleme sırasında hata oluştu: {e}")
