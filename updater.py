import requests
import os
import json
import hashlib

# GitHub Repo Bilgileri
REPO_OWNER = "Ahmettcakar"
REPO_NAME = "pyqt5-auto-update-example"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/"

def get_file_hash(file_path):
    """Dosyanın SHA-256 hash'ini hesaplar."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def check_for_updates():
    """GitHub'daki dosyalarla yerel dosyaları karşılaştırır."""
    try:
        # Yerel sürüm bilgisini oku
        with open("version.json", "r") as f:
            local_version = json.load(f)
        
        # GitHub'dan dosya listesini al
        response = requests.get(GITHUB_API_URL)
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

def download_updates():
    """Değişen dosyaları indir ve yerel sürümü güncelle."""
    try:
        response = requests.get(GITHUB_API_URL)
        remote_files = response.json()
        
        # Yeni sürüm bilgisi için geçici bir sözlük
        new_version = {"version": "", "files": {}}
        
        for file in remote_files:
            file_name = file["name"]
            download_url = file["download_url"]
            
            # Dosyayı indir
            response = requests.get(download_url)
            with open(file_name, "wb") as f:
                f.write(response.content)
            
            # Hash'i hesapla ve sürüm bilgisine ekle
            new_version["files"][file_name] = file["sha"]
        
        # Yeni sürümü kaydet
        new_version["version"] = "1.0.1"  # GitHub'daki yeni sürüm
        with open("version.json", "w") as f:
            json.dump(new_version, f, indent=4)
        
        print("Güncelleme başarılı!")

    except Exception as e:
        print(f"İndirme hatası: {e}")