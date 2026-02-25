from PySide6.QtWidgets import QApplication, QLabel, QWidget
import sys

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Тест PySide6")
window.setGeometry(100, 100, 300, 200)

label = QLabel("Все работает! 🎉", window)
label.move(100, 80)

window.show()
sys.exit(app.exec())