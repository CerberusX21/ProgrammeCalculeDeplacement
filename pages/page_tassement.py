from PyQt6.QtWidgets import QWidget, QFormLayout

class TassementPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        layout.addRow("À venir", QWidget())
        self.setLayout(layout)

    def calculate(self, result_label):
        result_label.setText("Calcul de tassement non implémenté.")
