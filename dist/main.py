import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from updater import  download_updates
import logging
# LOGGING AYARI
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_current_version():
    """version.json dosyasından mevcut sürümü okur."""
    try:
        with open("version.json", "r") as f:
            version_data = json.load(f)
        return version_data.get("version", "Bilinmeyen Sürüm")
    except FileNotFoundError:
        logging.error("version.json bulunamadı.")
        return "Version Dosyası Yok"
    except json.JSONDecodeError:
        logging.error("version.json hatalı JSON formatında.")
        return "Hatalı JSON Formatı"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Güncelleme Örneği")
        self.setGeometry(100, 100, 300, 200)
        
        # Mevcut sürümü  oku 
        self.current_version = get_current_version()
        # Widget'lar
        self.label = QLabel(f"Mevcut Sürüm: {self.current_version}", self)
        self.label2 = QLabel("Deneme", self)
        
        self.update_btn = QPushButton("Güncelle", self)
        self.update_btn.clicked.connect(self.update_app)
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.label2)
        
        layout.addWidget(self.update_btn)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def restart_program():
        """Programı yeniden başlatır."""
        python = sys.executable
        logging.info("Program yeniden başlatılıyor.")
        os.execl(python, python, *sys.argv)

    def update_app(self):
        logging.info("Güncelleme butonuna basıldı.")
        if not download_updates():
            self.label2.setText("Güncelleme tamamlandı! Yeniden başlatın.")
            self.current_version = get_current_version()
            self.label.setText(f"Mevcut Sürüm: {self.current_version}")
            self.restart_program()
        else:
            self.label2.setText("Program zaten güncel")

    
if __name__ == "__main__":
    logging.info("Uygulama başlatılıyor.")
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.exception(f"Program çalışırken hata oluştu: {e}")