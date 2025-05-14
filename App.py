from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QLabel, QPushButton, QMessageBox, QSpacerItem, QSizePolicy, QFormLayout, QGroupBox, QCheckBox, QSlider, QTabWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys

from FormulaClay import FormulaClay
from FormulaD50ff import FormulaD50ff
from FormulaLiquid import FormulaLiquid

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soil Analysis Tool")
        self.resize(1200, 500)

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
                qproperty-alignment: 'AlignLeft';
            }
        """)

        self.master_layout = QVBoxLayout()
        self.master_layout.setSpacing(15)
        self.master_layout.setContentsMargins(40, 30, 40, 30)

        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()

        self.tabs = QTabWidget()

        self.hydraulique_tab = QWidget()
        hydraulique_form = QFormLayout()

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

        hydraulique_form.addRow("Type de sol :", self._wrap(self.type_sol_input, self.type_sol))
        hydraulique_form.addRow("Type de pores :", self._wrap(self.pores_input, self.pores_sol))
        hydraulique_form.addRow("Compression :", self._wrap(self.compress_input, self.compress_sol))
        hydraulique_form.addRow("Type Gs :", self.density_input)

        self.hydraulique_tab.setLayout(hydraulique_form)

        self.tassement_tab = QWidget()
        tassement_form = QFormLayout()
        self.tassement_tab.setLayout(tassement_form)

        self.tabs.addTab(self.hydraulique_tab, "Conductivité hydraulique")
        self.tabs.addTab(self.tassement_tab, "Tassement")

        self.result_label = QLabel("Résultat :")
        self.result_label.setObjectName("ResultLabel")

        self.calculate_button = QPushButton("Calculer")
        self.calculate_button.clicked.connect(self.calculate)

        self.button_row = QHBoxLayout()
        self.button_row.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.button_row.addWidget(self.calculate_button)
        self.button_row.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.col1.addWidget(self.tabs)
        self.col1.addLayout(self.button_row)
        self.col1.addWidget(self.result_label)

        self.col2.addWidget(self.canvas)

        row_layout = QHBoxLayout()
        row_layout.addLayout(self.col1, 30)
        row_layout.addLayout(self.col2, 70)

        self.master_layout.addLayout(row_layout)
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
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            self.calculate_hydraulique()
        elif current_tab == 1:
            self.calculate_tassement()

    def calculate_tassement(self):
        QMessageBox.information(self, "Non implémenté", "Le calcul de tassement n’est pas encore implémenté.")

    def calculate_hydraulique(self):
        try:
            data = {
                'type_sol': float(self.type_sol_input.text()),
                'pores_sol': float(self.pores_input.text()),
                'compress_sol': float(self.compress_input.text()),
                'density_sol': float(self.density_input.text()),
                'water': self.pores_sol.currentText() == "W",
                'type': self.type_sol.currentText()
            }
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer des valeurs numériques valides.")
            return

        formulas = {
            "clay%": FormulaClay(),
            "wL": FormulaLiquid(),
            "d50ff": FormulaD50ff()
        }

        formula = formulas.get(data['type'])

        try:
            result = formula.calculate(
                data['type_sol'], data['pores_sol'],
                data['compress_sol'], data['density_sol'],
                data['water']
            )
            self.result_label.setText(f"Résultat :  {result}")
        except ValueError as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur de calcul de formula non valide.\n {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    window = Window()
    window.show()
    sys.exit(app.exec())
