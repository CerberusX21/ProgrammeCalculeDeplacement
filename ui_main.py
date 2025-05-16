from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpacerItem,
    QSizePolicy, QTabWidget
)
from pages.page_hydro import HydroPage
from pages.page_tassement import TassementPage
from pages.graph_viewer.graph_viewer import GraphViewer
from style import APP_STYLE


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.graph_data = None

        self.setWindowTitle("Soil Analysis Tool")
        self.resize(1300, 700)
        self.setStyleSheet(APP_STYLE)

        self._init_ui()
        self._setup_layouts()
        self._connect_signals()

    def _init_ui(self):
        self.tabs = QTabWidget()
        self.hydro_page = HydroPage()
        self.tassement_page = TassementPage()

        self.tabs.addTab(self.hydro_page, "Hydraulic Conductivity")
        self.tabs.addTab(self.tassement_page, "Settlement")

        self.result_label = QLabel("Result:")
        self.result_label.setObjectName("ResultLabel")

        self.reset_button = QPushButton("Reset")
        self.calculate_button = QPushButton("Calculate")

        self.graph_viewer = GraphViewer()
        self.graph_viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _setup_layouts(self):
        self.master_layout = QVBoxLayout()
        self.master_layout.setSpacing(15)
        self.master_layout.setContentsMargins(40, 30, 40, 30)

        col1 = QVBoxLayout()
        col1.addWidget(self.tabs)
        col1.addLayout(self._create_button_row())
        col1.addWidget(self.result_label)

        col2 = QVBoxLayout()
        col2.addWidget(self.graph_viewer)

        row_layout = QHBoxLayout()
        row_layout.addLayout(col1, 20)
        row_layout.addLayout(col2, 80)

        self.master_layout.addLayout(row_layout)
        self.setLayout(self.master_layout)

    def _create_button_row(self):
        button_row = QHBoxLayout()
        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        button_row.addSpacerItem(spacer)
        button_row.addWidget(self.reset_button)
        button_row.addWidget(self.calculate_button)
        button_row.addSpacerItem(spacer)

        return button_row

    def _connect_signals(self):
        self.reset_button.clicked.connect(self.reset)
        self.calculate_button.clicked.connect(self.calculate)

    def calculate(self):
        current_index = self.tabs.currentIndex()
        if current_index == 0:
            self.graph_data = self.hydro_page.calculate(self.result_label)
            if self.graph_data:
                self.graph_viewer.set_graph_data(self.graph_data)
        elif current_index == 1:
            self.tassement_page.calculate(self.result_label)

    def reset(self):
        current_index = self.tabs.currentIndex()
        if current_index == 0:
            self.hydro_page.reset()
            self.result_label.setText("Result:")
        elif current_index == 1:
            pass
