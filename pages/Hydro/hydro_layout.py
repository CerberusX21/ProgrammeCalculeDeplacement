from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QLabel, QCheckBox, QWidget, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt
from widgets.modern_widgets import ModernParameterWidget, ModernGroupBox

# Add compact styling constants
COMPACT_STYLE = """
QLabel {
    font-size: 12px;
    padding: 1px;
    margin: 1px;
}
QLabel.column-header {
    font-size: 10px;
    color: #666666;
    font-weight: 400;
    padding: 0px;
    margin: 0px 0px 0px 0px;
}
QLabel.parameter-label {
    font-size: 14px;
    font-weight: bold;
    padding: 0px;
    margin: 0px;
}
QComboBox {
    font-size: 12px;
    max-height: 20px;
    min-height: 20px;
    max-width: 75px;
    min-width: 75px;
    padding: 2px 4px;
    margin: 1px;
}
QLineEdit {
    font-size: 12px;
    max-height: 20px;
    min-height: 20px;
    max-width: 75px;
    min-width: 75px;
    padding: 2px 4px;
    margin: 1px;
}
ModernGroupBox {
    font-size: 12px;
    padding: 8px;
    margin: 2px;
    border: 1px solid #007bff;
}
ModernGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0;
    margin: 0;
    color: transparent;
    background: transparent;
    border: none;
}
QCheckBox {
    font-size: 12px;
    padding: 2px;
    margin: 2px;
}
QPushButton {
    padding: 2px 8px;
    min-width: 70px;
    margin: 2px;
}
"""

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
    # Apply compact styling
    self.setStyleSheet(COMPACT_STYLE)
    
    main_layout = QHBoxLayout()
    main_layout.setSpacing(4)
    main_layout.setContentsMargins(4, 4, 4, 4)

    # --- Parameters Panel (Left) ---
    parameters_widget = QWidget()
    parameters_layout = QVBoxLayout(parameters_widget)
    parameters_layout.setSpacing(4)
    parameters_layout.setContentsMargins(4, 4, 4, 4)

    # Parameters Group (without title)
    soil_group = ModernGroupBox("")  # Empty title
    soil_layout = QVBoxLayout()
    soil_layout.setSpacing(12)  # Increased spacing between parameter sections
    soil_layout.setContentsMargins(8, 8, 8, 8)

    # Helper function to create parameter section with label above widgets
    def add_parameter_section(layout, label, widget_type, widget_unit, widget_value):
        section = QVBoxLayout()
        section.setSpacing(0)  # Remove spacing between elements within section
        
        # Add main parameter label
        label_widget = QLabel(label)
        label_widget.setProperty("class", "parameter-label")
        section.addWidget(label_widget)
        
        # Create grid layout for perfect alignment
        grid = QGridLayout()
        grid.setSpacing(2)  # Reduced spacing between elements
        grid.setContentsMargins(0, 0, 0, 0)
        
        # Add headers to grid
        type_header = QLabel("Type")
        value_header = QLabel("Value")
        unit_header = QLabel("Unit")
        
        # Set fixed widths for all components
        widget_width = 75
        for widget in [widget_type, widget_value, widget_unit]:
            widget.setFixedWidth(widget_width)
        
        for header in [type_header, value_header, unit_header]:
            header.setFixedWidth(widget_width)
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.setProperty("class", "column-header")
        
        # Add headers to first row
        grid.addWidget(type_header, 0, 0)
        grid.addWidget(value_header, 0, 1)
        grid.addWidget(unit_header, 0, 2)
        
        # Add widgets to second row, with reduced vertical spacing
        grid.addWidget(widget_type, 1, 0)
        grid.addWidget(widget_value, 1, 1)
        grid.addWidget(widget_unit, 1, 2)
        
        # Add stretch to maintain left alignment
        grid.setColumnStretch(3, 1)
        
        section.addLayout(grid)
        layout.addLayout(section)

    # Add parameters with consistent spacing
    add_parameter_section(soil_layout, "Soil Type Parameter", 
                        self.type_sol, self.type_sol_unit, self.type_sol_input)
    add_parameter_section(soil_layout, "Pore-Ice Parameter",
                        self.pores_sol, self.pores_sol_unit, self.pores_input)
    add_parameter_section(soil_layout, "Soil Compression Parameter",
                        self.compress_sol, self.compress_sol_unit, self.compress_input)
    add_parameter_section(soil_layout, "Specific gravity of solids",
                        self.density_sol, self.density_sol_unit, self.density_input)

    soil_group.setLayout(soil_layout)

    # Custom results checkbox with minimal spacing
    self.use_custom_params_check = QCheckBox("Use custom results")
    custom_checkbox_widget = QWidget()
    custom_checkbox_layout = QHBoxLayout(custom_checkbox_widget)
    custom_checkbox_layout.setContentsMargins(4, 4, 4, 4)
    custom_checkbox_layout.setSpacing(4)
    custom_checkbox_layout.addWidget(self.use_custom_params_check)
    custom_checkbox_layout.addStretch()

    # Add groups to layout with minimal spacing
    parameters_layout.addWidget(soil_group)
    parameters_layout.addWidget(custom_checkbox_widget)
    parameters_layout.addStretch()

    # Buttons with consistent sizing
    button_layout = QHBoxLayout()
    button_layout.setSpacing(8)
    button_layout.addStretch()
    self.reset_button.setFixedWidth(70)
    self.calculate_button.setFixedWidth(70)
    button_layout.addWidget(self.reset_button)
    button_layout.addWidget(self.calculate_button)
    button_layout.addStretch()
    parameters_layout.addLayout(button_layout)

    # Set fixed width for parameters panel to ensure consistency between pages
    parameters_widget.setFixedWidth(400)

    # --- Results Panel (Right) ---
    results_panel = QWidget()
    results_panel.setObjectName("resultsPanel")
    results_layout_right = QVBoxLayout(results_panel)
    results_layout_right.setContentsMargins(4, 4, 4, 4)
    results_layout_right.setSpacing(4)

    results_title = QLabel("Hydraulic Results")
    results_title.setObjectName("resultsTitle")
    results_layout_right.addWidget(results_title)
    results_layout_right.addWidget(self.result_label)

    graph_title = QLabel("Hydraulic Conductivity Graph")
    graph_title.setObjectName("graphTitle")
    results_layout_right.addWidget(graph_title)
    results_layout_right.addWidget(self.graph_viewer)

    # --- Main layout ---
    main_layout.addWidget(parameters_widget)
    main_layout.addWidget(results_panel)
    self.setLayout(main_layout)

    # Ensure the graph viewer expands to fill available space
    self.graph_viewer.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Expanding
    )