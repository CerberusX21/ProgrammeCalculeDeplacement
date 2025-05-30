from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import QSize
from pages.Hydro.page_hydro import HydroPage
from pages.tassement.page_tassement import TassementPage
from style import APP_STYLE

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Soil Analysis Tool")
        self.setMinimumSize(800, 700)  # Increased minimum height
        self.resize(1300, 800)  # Increased default height
        self.setStyleSheet(APP_STYLE)

        self.tabs = QTabWidget()
        self.hydro_page = HydroPage()
        self.tassement_page = TassementPage()
        self.tabs.addTab(self.hydro_page, "Hydraulic Conductivity")
        self.tabs.addTab(self.tassement_page, "Settlement")

        # Synchronisation entre les deux pages pour avoir les valeurs automatiquement 
        self.hydro_page.set_other_page(self.tassement_page)
        self.tassement_page.set_other_page(self.hydro_page)

        layout = QVBoxLayout()
        # Reduce margins for smaller screens
        layout.setContentsMargins(20, 15, 20, 15)
        layout.addWidget(self.tabs)
        self.setLayout(layout)
