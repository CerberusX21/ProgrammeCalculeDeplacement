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

        self.tabs.currentChanged.connect(self.on_tab_changed)

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
        row_layout.addLayout(col1, 40)
        row_layout.addLayout(col2, 60)

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

        if current_index == 0:  # Onglet Conductivité Hydraulique
            self.graph_data = self.hydro_page.calculate(self.result_label)
            self.graph_viewer.set_is_tassement(False)
            self.graph_viewer.set_ei_value(None)

        elif current_index == 1:  # Onglet Tassement
            self.graph_data = self.tassement_page.calculate(self.result_label)
            self.graph_viewer.set_is_tassement(True)
            if self.graph_data:
                self.graph_viewer.set_ei_value(self.graph_data.get("ei_star"))

        if self.graph_data:
            self.graph_viewer.set_graph_data(self.graph_data)

    def reset(self):
        current_index = self.tabs.currentIndex()
        if current_index == 0:
            self.hydro_page.reset()
        elif current_index == 1:
            self.tassement_page.reset()
        self.graph_viewer.clear_graph()
        self.result_label.setText("Result:")

    def on_tab_changed(self, index):
        self.graph_viewer.clear_graph()
        self.graph_viewer.checkbox_stress.blockSignals(True)
        self.graph_viewer.checkbox_conductivity.blockSignals(True)

        if index == 0:
            self.graph_viewer.set_is_tassement(False)
            self.graph_viewer.checkbox_stress.setEnabled(True)
            self.graph_viewer.checkbox_stress.setChecked(True)
            self.graph_viewer.checkbox_conductivity.setEnabled(True)
            self.graph_viewer.checkbox_conductivity.setChecked(True)
            self.graph_viewer.set_ei_value(None)

        elif index == 1:
            self.graph_viewer.set_is_tassement(True)
            self.graph_viewer.checkbox_stress.setEnabled(True)
            self.graph_viewer.checkbox_stress.setChecked(True)
            self.graph_viewer.checkbox_conductivity.setChecked(False)
            self.graph_viewer.checkbox_conductivity.setEnabled(False)

        self.graph_viewer.checkbox_stress.blockSignals(False)
        self.graph_viewer.checkbox_conductivity.blockSignals(False)

        if self.graph_data:
            self.graph_viewer.set_graph_data(self.graph_data)