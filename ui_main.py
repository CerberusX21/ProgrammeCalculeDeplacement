from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, QTabWidget
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from pages.page_hydro import HydroPage
from pages.page_tassement import TassementPage
from style import APP_STYLE


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soil Analysis Tool")
        self.resize(1200, 500)
        self.setStyleSheet(APP_STYLE)

        self.master_layout = QVBoxLayout()
        self.master_layout.setSpacing(15)
        self.master_layout.setContentsMargins(40, 30, 40, 30)

        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()

        self.tabs = QTabWidget()

        # Instanciation des pages
        self.hydro_page = HydroPage()
        self.tassement_page = TassementPage()

        self.tabs.addTab(self.hydro_page, "Conductivité hydraulique")
        self.tabs.addTab(self.tassement_page, "Tassement")

        self.result_label = QLabel("Résultat :")
        self.result_label.setObjectName("ResultLabel")

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)

        self.calculate_button = QPushButton("Calculer")
        self.calculate_button.clicked.connect(self.calculate)

        self.button_row = QHBoxLayout()
        self.button_row.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.button_row.addWidget(self.reset_button)
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

    def calculate(self):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            self.hydro_page.calculate(self.result_label)
        elif current_tab == 1:
            self.tassement_page.calculate(self.result_label)

    def reset(self):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            self.hydro_page.reset()
            self.result_label.setText("Résultat :")
        elif current_tab == 1:
            pass

