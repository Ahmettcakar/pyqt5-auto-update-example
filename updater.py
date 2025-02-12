import requests
import os
import json
import hashlib
# https://github.com/Ahmettcakar/pyqt5-auto-update-example

# GitHub Token ve Repo Bilgileri
# Buraya token'ınızı yapıştırın
GITHUB_TOKEN = "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"
# Repo bilgileri
REPO_OWNER = "Ahmettcakar"
REPO_NAME = "pyqt5-auto-update-example"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
# Token ile istek yapma
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
BRANCH = "main"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/"
GITHUB_VERSION_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/version.json"

def get_file_hash(file_path):
    """Dosyanın SHA-256 hash'ini hesaplar."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

# Örnek kullanım
print("main.py SHA:", get_file_hash("main.py"))
print("updater.py SHA:", get_file_hash("updater.py"))


def get_file_hash(file_path):
    """Dosyanın SHA-256 hash'ini hesaplar."""
    sha256 = hashlib.sha256()
    if not os.path.exists(file_path):
        return None  # Dosya yoksa None döndür
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def load_local_version():
    """Yerel version.json dosyasını oku."""
    try:
        with open("version.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"version": "Bilinmiyor", "files": {}}

def load_remote_version():
    """GitHub’daki version.json dosyasını indir ve oku."""
    try:
        response = requests.get(GITHUB_VERSION_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Hata! GitHub'daki version.json alınamadı. Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"İndirme hatası: {e}")
        return None

def download_updates():
    """Sadece SHA değişen dosyaları indir ve version.json'u güncelle."""
    try:
        remote_version = load_remote_version()
        if not remote_version:
            print("Güncelleme kontrolü başarısız oldu.")
            return
        
        local_version = load_local_version()
        new_version = {"version": remote_version["version"], "files": local_version["files"].copy()}  # Önceki bilgileri koru
        
        guncel_mi=True
        for file_name, remote_hash in remote_version["files"].items():
            local_hash = local_version["files"].get(file_name, "")

            # Eğer SHA değerleri farklıysa veya dosya yoksa, güncelle
            if remote_hash != local_hash:
                guncel_mi=False
                download_url = f"{RAW_BASE_URL}{file_name}"
                print(f"İndiriliyor: {file_name}")

                response = requests.get(download_url)
                if response.status_code == 200:
                    with open(file_name, "wb") as f:
                        f.write(response.content)

                    # Yeni dosyanın SHA hash'ini hesapla ve version.json'a ekle
                    new_version["files"][file_name] = get_file_hash(file_name)
                else:
                    print(f"Dosya indirilemedi: {file_name}, Hata kodu: {response.status_code}")
        if not guncel_mi: 
            # Güncellenmiş version.json'ı kaydet
            with open("version.json", "w") as f:
                json.dump(new_version, f, indent=4)
            
            return False
        else:
            return True
            

    except Exception as e:
        print(f"İndirme hatası: {e}") 