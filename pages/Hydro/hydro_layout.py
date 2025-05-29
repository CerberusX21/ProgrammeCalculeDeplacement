from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QLabel, QCheckBox, QWidget
)
from PyQt6.QtCore import Qt
from widgets.modern_widgets import ModernParameterWidget, ModernGroupBox

def init_unit_mappings(self):
    """Initialize the unit mappings that are common to both pages"""
    self.type_unit_mapping = {
        self.type_sol: {"clay%": ["%"], "wL": ["%"], "d50ff": ["mm"]},
        self.pores_sol: {"W": ["kg/kg"], "ρf": ["kg/m³", "g/cm³"], "ef*": ["Direct"]},
        self.compress_sol: {"σ′v": ["kPa"]},
        self.density_sol: {"Gs": ["-"]}
    }


def init_input_limits(self):
    """Initialize the input limits that are common to both pages"""
    self.input_limits = {
        self.type_sol_unit: {"%": (1, 100), "mm": (0.001, 0.1)},
        self.pores_sol_unit: {
            "kg/kg": (0, float('inf')), 
            "kg/m³": (900, 3000),
            "g/cm³": (0.9, 3), 
            "Direct": (0, float('inf'))
        },
        self.compress_sol_unit: {"kPa": (0, float('inf'))},
        self.density_sol_unit: {"-": (1, 4)}
    }


def assemble_hydro_layout(self):
    main_layout = QHBoxLayout()

    def make_headers():
        headers_layout = QGridLayout()
        headers_layout.addWidget(QLabel("<b>Parameter</b>"), 0, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.addWidget(QLabel("<b>Type</b>"), 0, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.addWidget(QLabel("<b>Unit</b>"), 0, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.addWidget(QLabel("<b>Value</b>"), 0, 3, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.setColumnStretch(0, 3)
        headers_layout.setColumnStretch(1, 2)
        headers_layout.setColumnStretch(2, 1)
        headers_layout.setColumnStretch(3, 2)
        return headers_layout

    def make_separator():
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #e2e8f0; height: 1px;")
        return sep

    # --- Parameters Panel (Left) ---
    parameters_widget = QWidget()
    parameters_layout = QVBoxLayout(parameters_widget)
    parameters_layout.setSpacing(12)
    parameters_layout.setContentsMargins(10, 10, 10, 10)

    # Soil Parameters Group
    soil_group = ModernGroupBox("Soil Parameters")
    soil_layout = QVBoxLayout()
    soil_layout.addLayout(make_headers())

    # Soil Type Parameter
    soil_layout.addWidget(make_separator())
    soil_layout.addWidget(ModernParameterWidget(
        "Soil Type Parameter",
        self.type_sol, self.type_sol_unit, self.type_sol_input
    ))

    # Pore-Ice Parameter
    soil_layout.addWidget(make_separator())
    soil_layout.addWidget(ModernParameterWidget(
        "Pore-Ice Parameter",
        self.pores_sol, self.pores_sol_unit, self.pores_input
    ))

    # Compression Parameter
    soil_layout.addWidget(make_separator())
    soil_layout.addWidget(ModernParameterWidget(
        "Soil Compression Parameter",
        self.compress_sol, self.compress_sol_unit, self.compress_input
    ))

    # Specific Gravity Parameter
    soil_layout.addWidget(make_separator())
    soil_layout.addWidget(ModernParameterWidget(
        "Specific gravity of solids",
        self.density_sol, self.density_sol_unit, self.density_input
    ))

    soil_group.setLayout(soil_layout)

    # Custom results checkbox
    self.use_custom_params_check = QCheckBox("Use custom results")
    custom_checkbox_widget = QWidget()
    custom_checkbox_layout = QHBoxLayout(custom_checkbox_widget)
    custom_checkbox_layout.setContentsMargins(0, 8, 0, 2)
    custom_checkbox_layout.setAlignment(self.use_custom_params_check, Qt.AlignmentFlag.AlignLeft)
    custom_checkbox_layout.addWidget(self.use_custom_params_check)
    custom_checkbox_widget.setMaximumWidth(600)

    # Add groups to layout
    parameters_layout.addWidget(soil_group)
    parameters_layout.addWidget(custom_checkbox_widget)

    # Buttons
    button_layout = QHBoxLayout()
    button_layout.setSpacing(10)
    button_layout.addStretch()
    button_layout.addWidget(self.reset_button)
    button_layout.addWidget(self.calculate_button)
    button_layout.addStretch()
    parameters_layout.addLayout(button_layout)

    # --- Results Panel (Right) ---
    results_panel = QWidget()
    results_panel.setObjectName("resultsPanel")
    results_layout_right = QVBoxLayout(results_panel)
    results_layout_right.setContentsMargins(10, 10, 10, 10)
    results_layout_right.setSpacing(10)

    results_title = QLabel("Hydraulic Results")
    results_title.setObjectName("resultsTitle")
    results_layout_right.addWidget(results_title)
    results_layout_right.addWidget(self.result_label)

    graph_title = QLabel("Hydraulic Conductivity Graph")
    graph_title.setObjectName("graphTitle")
    results_layout_right.addWidget(graph_title)
    results_layout_right.addWidget(self.graph_viewer)

    # --- Main layout ---
    main_layout.addWidget(parameters_widget, 1)
    main_layout.addWidget(results_panel, 1)
    self.setLayout(main_layout)