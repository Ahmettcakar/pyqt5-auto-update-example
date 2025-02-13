import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from updater import  download_updates

def get_current_version():
    """version.json dosyasından mevcut sürümü okur."""
    try:
        with open("version.json", "r") as f:
            version_data = json.load(f)
        return version_data.get("version", "Bilinmeyen Sürüm")
    except FileNotFoundError:
        return "Version Dosyası Yok"
    except json.JSONDecodeError:
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
        self.label2 = QLabel("232 ", self)
        
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

    def update_app(self):
        if not download_updates():
            self.label2.setText("Güncelleme tamamlandı! Yeniden başlatın.")
            self.current_version = get_current_version()
            self.label.setText(f"Mevcut Sürüm: {self.current_version}")
        else:
            self.label2.setText("Program zaten güncel")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()