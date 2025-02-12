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

def increment_version(version):
    """Mevcut versiyon numarasını artırır. (Örn: 1.0.0 → 1.0.1)"""
    parts = version.split(".")
    if len(parts) == 3:
        parts[2] = str(int(parts[2]) + 1)  # Son rakamı artır
    return ".".join(parts)

def update_version_json():
    """Tüm izlenen dosyaların SHA-256 hash'ini hesaplayarak version.json dosyasını günceller ve versiyonu artırır."""
    if not os.path.exists(version_file):
        print(f" Uyarı: {version_file} dosyası bulunamadı, yeni bir tane oluşturuluyor...")
        current_version = "1.0.0"  # Eğer dosya yoksa başlangıç versiyonu
        new_version_data = {"version": current_version, "files": {}}
    else:
        # Mevcut version.json dosyasını oku
        with open(version_file, "r") as f:
            try:
                new_version_data = json.load(f)
                current_version = new_version_data.get("version", "1.0.0")
            except json.JSONDecodeError:
                print(" Hata: version.json okunamadı, varsayılan versiyon kullanılacak.")
                current_version = "1.0.0"
                new_version_data = {"version": current_version, "files": {}}

    # Versiyon numarasını artır
    new_version_data["version"] = increment_version(current_version)

    # SHA hash'lerini güncelle
    for file in tracked_files:
        if os.path.exists(file):
            new_version_data["files"][file] = get_file_hash(file)
        else:
            print(f" Uyarı: {file} bulunamadı, version.json içine eklenmeyecek!")

    # Güncellenmiş version.json'ı kaydet
    with open(version_file, "w") as f:
        json.dump(new_version_data, f, indent=4)

    print(f"✅ version.json başarıyla güncellendi! Yeni versiyon: {new_version_data['version']}")

# SHA güncelleme işlemini başlat
if __name__ == "__main__":
    update_version_json()
