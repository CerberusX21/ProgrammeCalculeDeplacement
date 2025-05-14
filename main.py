from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
import sys
from ui_main import Window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    window = Window()
    window.show()
    sys.exit(app.exec())
