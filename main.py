from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
import sys
from ui_main import Window

if __name__ == '__main__':
    """Point d'entrée de l'application.

    - Crée l'application Qt
    - Applique une police par défaut pour une interface homogène
    - Instancie et affiche la fenêtre principale `Window`
    - Lance la boucle d'événements
    """
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    window = Window()
    window.show()
    sys.exit(app.exec())
