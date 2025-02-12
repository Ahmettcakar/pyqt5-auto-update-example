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



def check_for_updates():
    """GitHub'daki dosyalarla yerel dosyaları karşılaştırır."""
    try:
        # Yerel sürüm bilgisini oku
        with open("version.json", "r") as f:
            local_version = json.load(f)

        # GitHub'dan dosya listesini al
        response = requests.get(GITHUB_API_URL, headers=headers)
        if response.status_code != 200:
            return False

        remote_files = response.json()
        update_available = False

        for file in remote_files:
            if file["name"] == "version.json":
                continue  # version.json'ı atla

            file_name = file["name"]
            remote_hash = file["sha"]
            local_hash = local_version["files"].get(file_name, "")

            if remote_hash != local_hash:
                print(f"{file_name} dosyası güncellenecek.")
                update_available = True

        return update_available

    except Exception as e:
        print(f"Hata: {e}")
        return False




def get_file_hash(file_path):
    """Dosyanın SHA-256 hash'ini hesaplar."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def download_updates():
    """Güncellenen dosyaları indir ve yerel version.json dosyasını güncelle."""
    try:
        response = requests.get(GITHUB_API_URL, headers=headers)
        if response.status_code != 200:
            print(
                f"Hata! GitHub API Yanıtı: {response.status_code} - {response.text}")
            return

        remote_files = response.json()

        # Yeni sürüm bilgisi için geçici bir sözlük
        new_version = {"version": "1.0.1", "files": {}}

        for file in remote_files:
            file_name = file.get("name")
            if file_name == "version.json":
                continue  # version.json'ı indirme, sadece güncelle

            # Doğru indirme URL'sini oluştur
            download_url = f"{RAW_BASE_URL}{file_name}"
            # Hangi dosyanın indirildiğini görmek için
            print(f"İndiriliyor: {download_url}")

            # Dosyayı indir
            response = requests.get(download_url)
            if response.status_code == 200:
                with open(file_name, "wb") as f:
                    f.write(response.content)

                # Yeni dosyanın SHA hash'ini hesapla ve version.json'a ekle
                new_version["files"][file_name] = get_file_hash(file_name)
            else:
                print(
                    f"Dosya indirilemedi: {file_name}, Hata kodu: {response.status_code}")

        # Güncellenmiş version.json'ı kaydet
        with open("version.json", "w") as f:
            json.dump(new_version, f, indent=4)

        print("Güncelleme tamamlandı!")

    except Exception as e:
        print(f"İndirme hatası: {e}")


def get_file_hash(file_path):
    """Dosyanın SHA-256 hash'ini hesaplar."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def load_local_version():
    """Mevcut version.json dosyasını oku."""
    try:
        with open("version.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"version": "Bilinmiyor", "files": {}}

def download_updates():
    """Güncellenen dosyaları indir ve yerel version.json dosyasını doğru şekilde güncelle."""
    try:
        response = requests.get(GITHUB_API_URL, headers=headers)
        if response.status_code != 200:
            print(f"Hata! GitHub API Yanıtı: {response.status_code} - {response.text}")
            return
        
        remote_files = response.json()
        
        # Mevcut version.json dosyasını oku
        local_version = load_local_version()
        new_version = {"version": "1.0.1", "files": local_version["files"].copy()}  # Önceki bilgileri koru
        
        for file in remote_files:
            file_name = file.get("name")
            if file_name == "version.json":
                continue  # version.json'ı indirme, sadece güncelle
            
            # Doğru indirme URL'sini oluştur
            download_url = f"{RAW_BASE_URL}{file_name}"
            print(f"İndiriliyor: {download_url}")

            # Dosyayı indir
            response = requests.get(download_url)
            if response.status_code == 200:
                with open(file_name, "wb") as f:
                    f.write(response.content)

                # Yeni dosyanın SHA hash'ini hesapla ve version.json'a ekle
                new_version["files"][file_name] = get_file_hash(file_name)
            else:
                print(f"Dosya indirilemedi: {file_name}, Hata kodu: {response.status_code}")

        # Güncellenmiş version.json'ı kaydet
        with open("version.json", "w") as f:
            json.dump(new_version, f, indent=4)
        
        print("Güncelleme tamamlandı!")

    except Exception as e:
        print(f"İndirme hatası: {e}")