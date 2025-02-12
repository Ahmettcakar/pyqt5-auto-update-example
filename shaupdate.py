import hashlib
import json
import os

# Güncellenecek dosyalar
tracked_files = ["main.py", "updater.py"]
version_file = "version.json"

def get_file_hash(file_path):
    """Dosyanın SHA-256 hash'ini hesaplar."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def update_version_json():
    """Tüm izlenen dosyaların SHA-256 hash'ini hesaplayarak version.json dosyasını günceller."""
    if not os.path.exists(version_file):
        print(f"⚠️ Uyarı: {version_file} dosyası bulunamadı, yeni bir tane oluşturuluyor...")

    new_version_data = {
        "version": "1.0.0",  # Versiyonu buradan değiştirebilirsin
        "files": {}
    }

    for file in tracked_files:
        if os.path.exists(file):
            new_version_data["files"][file] = get_file_hash(file)
        else:
            print(f"⚠️ Uyarı: {file} bulunamadı, version.json içine eklenmeyecek!")

    # Güncellenmiş version.json'ı kaydet
    with open(version_file, "w") as f:
        json.dump(new_version_data, f, indent=4)

    print("✅ version.json başarıyla güncellendi!")

# SHA güncelleme işlemini başlat
if __name__ == "__main__":
    update_version_json()