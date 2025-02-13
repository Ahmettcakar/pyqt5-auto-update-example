import sys
import subprocess
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

# updater.py içindeki download_updates fonksiyonunu içe aktar
from updater import download_updates

def get_current_version():
    """Yerel version.json dosyasından sürüm oku."""
    try:
        with open("version.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("version", "Bilinmiyor")
    except:
        return "Version Dosyası Yok"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Güncelleme Örneği")
        self.setGeometry(100, 100, 300, 200)

        self.current_version_label = QLabel(f"Mevcut Sürüm: {get_current_version()}")
        self.status_label = QLabel("")
        self.update_button = QPushButton("Güncelle")

        self.update_button.clicked.connect(self.update_app)

        layout = QVBoxLayout()
        layout.addWidget(self.current_version_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.update_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_app(self):
        # download_updates False dönerse güncelleme yapıldı demektir.
        updated = not download_updates()  
        # (Çünkü fonksiyon True dönerse "zaten güncel" anlamına geliyor, 
        #  False dönerse "dosya indirdim, güncelledim" anlamına geliyor.)

        if updated:
            self.status_label.setText("Güncelleme yapıldı, uygulama yeniden başlatılıyor...")
            # Yeni main.exe süreci başlat
            subprocess.Popen(["main.exe"])
            # Mevcut uygulamayı kapat
            sys.exit(0)
        else:
            self.status_label.setText("Uygulama zaten güncel!")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
