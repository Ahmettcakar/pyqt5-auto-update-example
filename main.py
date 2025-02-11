import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

from updater import check_for_updates, download_updates

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Güncelleme Örneği")
        self.setGeometry(100, 100, 300, 200)
        
        # Widget'lar
        self.label = QLabel("Mevcut Sürüm: 1.0.0", self)
        self.update_btn = QPushButton("Güncelle", self)
        self.update_btn.clicked.connect(self.update_app)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.update_btn)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_app(self):
        if check_for_updates():
            download_updates()
            self.label.setText("Güncelleme tamamlandı! Yeniden başlatın.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())