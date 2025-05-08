from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QLabel, QPushButton, QMessageBox, QSpacerItem, QSizePolicy, QFormLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import sys

import FormulaClay
from FormulaClay import FormulaClay

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soil Analysis Tool")
        self.resize(700, 450)

        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                color: #212529;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-weight: 600;
                color: #333;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 6px 30px 6px 10px;
                min-width: 120px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0d6efd;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border-left: 1px solid #ced4da;
                background-color: #f1f1f1;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                image: url(":/qt-project.org/styles/commonstyle/images/arrowdown-16.png");
                margin-right: 6px;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a58ca;
            }
            QLabel#ResultLabel {
                background-color: #ffffff;
                border: 1px solid #0d6efd;
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
                color: #0d6efd;
                min-height: 40px;
                max-height: 40px;
                qproperty-alignment: 'AlignCenter';
            }
        """)

        self.master_layout = QVBoxLayout()
        self.master_layout.setSpacing(15)
        self.master_layout.setContentsMargins(40, 30, 40, 30)

        self.result_label = QLabel("Résultat : ")
        self.result_label.setObjectName("ResultLabel")

        self.type_sol_input = QLineEdit()
        self.type_sol_input.setPlaceholderText("Valeur...")
        self.type_sol = QComboBox()
        self.type_sol.addItems(["clay%", "wL", "d50ff"])

        self.pores_input = QLineEdit()
        self.pores_input.setPlaceholderText("Valeur...")
        self.pores_sol = QComboBox()
        self.pores_sol.addItems(["W", "ρf"])

        self.compress_input = QLineEdit()
        self.compress_input.setPlaceholderText("Valeur...")
        self.compress_sol = QComboBox()
        self.compress_sol.addItems(["σ′v"])

        self.density_input = QLineEdit()
        self.density_input.setPlaceholderText("Valeur...")

        self.calculate_button = QPushButton("Calculer")
        self.calculate_button.clicked.connect(self.calculate)
        self.calculate_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Use a QFormLayout to align all fields
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        form_layout.addRow("Parametre de type de sol:", self._wrap(self.type_sol_input, self.type_sol))
        form_layout.addRow("Parametre de type de pores:", self._wrap(self.pores_input, self.pores_sol))
        form_layout.addRow("Parametre de compress:", self._wrap(self.compress_input, self.compress_sol))
        form_layout.addRow("Parametre de type Gs:", self.density_input)

        # Button centered
        button_row = QHBoxLayout()
        button_row.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        button_row.addWidget(self.calculate_button)
        button_row.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.master_layout.addLayout(form_layout)
        self.master_layout.addLayout(button_row)
        self.master_layout.addSpacing(10)
        self.master_layout.addWidget(self.result_label)

        self.setLayout(self.master_layout)

    def _wrap(self, widget1, widget2):
        row = QHBoxLayout()
        row.addWidget(widget1)
        row.addWidget(widget2)
        row.setStretch(0, 1)
        row.setStretch(1, 1)
        container = QWidget()
        container.setLayout(row)
        return container

    def calculate(self):
        formula = FormulaClay()
        try:
            type_sol_data = float(self.type_sol_input.text())
            pores_sol_data = float(self.pores_input.text())
            compress_sol_data = float(self.compress_input.text())
            density_sol_data = float(self.density_input.text())
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer des valeurs numériques valides.")
            return
        if self.type_sol.currentText() == "clay%" and self.pores_sol.currentText() == "W" and self.compress_sol.currentText() == "σ′v":
            result = formula.calculate_clay_eau(type_sol_data, pores_sol_data, compress_sol_data, density_sol_data)
            self.result_label.setText(f"Résultat :  {result}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    window = Window()
    window.show()
    sys.exit(app.exec())
