from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QLabel, QCheckBox, QWidget
)
from PyQt6.QtCore import Qt

from widgets.modern_widgets import ModernParameterWidget, ModernGroupBox

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
        "Clay content / Liquid limit / Fine fraction",
        self.type_sol, self.type_sol_unit, self.type_sol_input,
        "Options: Clay content (clay%), Liquid limit (wL), Fine fraction median diameter (d50ff)"
    ))

    # Pore-Ice Parameter
    soil_layout.addWidget(make_separator())
    soil_layout.addWidget(ModernParameterWidget(
        "Water content / Frozen density / Frozen void ratio",
        self.pores_sol, self.pores_sol_unit, self.pores_input,
        "Initial water content (W), Frozen bulk density (ρf), Frozen void ratio (ef*)"
    ))

    # Compression Parameter
    soil_layout.addWidget(make_separator())
    soil_layout.addWidget(ModernParameterWidget(
        "Effective vertical stress",
        self.compress_sol, self.compress_sol_unit, self.compress_input,
        "Effective vertical stress (σ'v)"
    ))

    # Specific Gravity Parameter
    soil_layout.addWidget(make_separator())
    soil_layout.addWidget(ModernParameterWidget(
        "Specific gravity",
        self.density_sol, self.density_sol_unit, self.density_input,
        "Specific gravity of soil solids"
    ))

    soil_group.setLayout(soil_layout)

    # Custom results checkbox
    self.use_custom_params_check = QCheckBox("Use custom results")
    self.use_custom_params_check.stateChanged.connect(self._toggle_custom_params)
    custom_checkbox_widget = QWidget()
    custom_checkbox_layout = QHBoxLayout(custom_checkbox_widget)
    custom_checkbox_layout.setContentsMargins(0, 8, 0, 2)
    custom_checkbox_layout.setAlignment(self.use_custom_params_check, Qt.AlignmentFlag.AlignLeft)
    custom_checkbox_layout.addWidget(self.use_custom_params_check)
    custom_checkbox_widget.setMaximumWidth(600)

    # Results group (for ei*, Cc*, Ck*)
    results_group = ModernGroupBox("Indices and Ratios")
    results_layout = QVBoxLayout()
    results_layout.addLayout(make_headers())
    results_layout.addWidget(make_separator())

    # ei*
    results_layout.addWidget(ModernParameterWidget(
        "Initial thawed void ratio",
        self.result_EI_type, self.result_EI_unit, self.result_EI_input,
        "Initial thawed void ratio (ei*)"
    ))

    # Cc*
    results_layout.addWidget(make_separator())
    results_layout.addWidget(ModernParameterWidget(
        "Thawed soil compression index",
        self.result_Cc_type, self.result_Cc_unit, self.result_Cc_input,
        "Thawed soil compression index (Cc*)"
    ))

    # Ck*
    results_layout.addWidget(make_separator())
    results_layout.addWidget(ModernParameterWidget(
        "Hydraulic conductivity index",
        self.result_Ck_type, self.result_Ck_unit, self.result_Ck_input,
        "Hydraulic conductivity index (Ck*)"
    ))

    results_group.setLayout(results_layout)
    results_group.setVisible(False)  # Hidden by default

    # Add groups to layout
    parameters_layout.addWidget(soil_group)
    parameters_layout.addWidget(custom_checkbox_widget)
    parameters_layout.addWidget(results_group)

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

    # Store for access in other methods
    self.results_group = results_group