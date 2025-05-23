from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from pages.Hydro.page_hydro import HydroPage
from pages.tassement.page_tassement import TassementPage
from style import APP_STYLE

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soil Analysis Tool")
        self.resize(1300, 700)
        self.setStyleSheet(APP_STYLE)

        self.tabs = QTabWidget()
        self.tabs.addTab(HydroPage(), "Hydraulic Conductivity")
        self.tabs.addTab(TassementPage(), "Settlement")

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.addWidget(self.tabs)
        self.setLayout(layout)
