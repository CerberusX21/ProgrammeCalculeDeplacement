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
    min-width: 75px;
    max-width: 75px;
    padding: 2px 4px;
    margin: 1px;
}
QComboBox[type="type"] {
    max-width: 200px;
    min-width: 200px;
}
QLineEdit {
    font-size: 12px;
    max-height: 20px;
    min-height: 20px;
    min-width: 75px;
    max-width: 75px;
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

/* Custom results specific styles */
QComboBox[custom="true"] {
    min-width: 200px;
    max-width: 200px;
}
QLineEdit[custom="true"] {
    min-width: 75px;
    max-width: 75px;
}
"""

def init_unit_mappings(self):
    """Initialize the unit mappings that are common to both pages"""
    self.type_unit_mapping = {
        self.type_sol: {"Clay percentage": ["%"], "Liquid limit": ["%"], "Fine fraction median diameter": ["mm"]},
        self.pores_sol: {"Thawed soil initial water content": ["kg/kg"], "Frozen buld density": ["kg/m³", "g/cm³"], "Frozen void ratio": ["Direct"]},
        self.compress_sol: {"Effective vertical stress": ["kPa"]},
        self.density_sol: {"Specific gravity of solids": ["-"]}
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
    main_layout.setContentsMargins(2, 4, 2, 4)

    # --- Parameters Panel (Left) ---
    parameters_widget = QWidget()
    parameters_layout = QVBoxLayout(parameters_widget)
    parameters_layout.setSpacing(4)
    parameters_layout.setContentsMargins(2, 4, 2, 4)

    # Set fixed width for parameters panel
    parameters_widget.setFixedWidth(450)  # Fixed width that accommodates all content

    # Parameters Group (without title)
    soil_group = ModernGroupBox("")
    soil_layout = QVBoxLayout()
    soil_layout.setSpacing(12)
    soil_layout.setContentsMargins(4, 8, 4, 8)

    # Helper function to create parameter section with label above widgets
    def add_parameter_section(layout, label, widget_type, widget_unit, widget_value):
        section = QVBoxLayout()
        section.setSpacing(4)
        section.setContentsMargins(2, 0, 2, 0)
        
        # Add main parameter label with transparent background
        label_widget = QLabel(label)
        label_widget.setProperty("class", "parameter-label")
        label_widget.setStyleSheet("background: transparent;")
        section.addWidget(label_widget)
        
        # Create grid layout for the widgets
        grid = QGridLayout()
        grid.setSpacing(4)
        grid.setContentsMargins(0, 0, 0, 0)
        
        # Add headers with transparent background
        type_header = QLabel("Type")
        value_header = QLabel("Value")
        unit_header = QLabel("Unit")
        
        for header in [type_header, value_header, unit_header]:
            header.setProperty("class", "column-header")
            header.setAlignment(Qt.AlignmentFlag.AlignLeft)
            header.setStyleSheet("background: transparent;")
        
        # Add headers to grid
        grid.addWidget(type_header, 0, 0)
        grid.addWidget(value_header, 0, 1)
        grid.addWidget(unit_header, 0, 2)
        
        # Add widgets to grid
        grid.addWidget(widget_type, 1, 0)
        grid.addWidget(widget_value, 1, 1)
        grid.addWidget(widget_unit, 1, 2)
        
        # Set column stretches for responsive layout
        grid.setColumnStretch(0, 4)  # Type column gets more space
        grid.setColumnStretch(1, 1)  # Value column
        grid.setColumnStretch(2, 1)  # Unit column
        
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
    custom_checkbox_layout.setContentsMargins(2, 4, 2, 4)
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

    # --- Results Panel (Right) ---
    results_panel = QWidget()
    results_panel.setObjectName("resultsPanel")
    results_layout_right = QVBoxLayout(results_panel)
    results_layout_right.setContentsMargins(2, 4, 2, 4)
    results_layout_right.setSpacing(4)

    results_layout_right.addWidget(self.results_display)
    results_layout_right.addWidget(self.graph_viewer)

    # Make results panel expand to fill available space
    results_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    # --- Main layout ---
    main_layout.addWidget(parameters_widget)
    main_layout.addWidget(results_panel, stretch=1)
    self.setLayout(main_layout)

def _setup_custom_results(self):
    # Create the custom results group
    self.results_group = ModernGroupBox("")  # Empty title for consistency
    results_layout = QVBoxLayout()
    results_layout.setSpacing(12)  # Match soil parameters spacing
    results_layout.setContentsMargins(4, 8, 4, 8)  # Match soil parameters margins

    # Create grid layout for all parameters
    grid = QGridLayout()
    grid.setSpacing(4)
    grid.setContentsMargins(0, 0, 0, 0)

    # Add headers
    type_header = QLabel("Type")
    unit_header = QLabel("Unit")
    value_header = QLabel("Value")
    
    for header in [type_header, unit_header, value_header]:
        header.setProperty("class", "column-header")
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
    
    # Add headers to grid
    grid.addWidget(type_header, 0, 0)
    grid.addWidget(unit_header, 0, 1)
    grid.addWidget(value_header, 0, 2)

    # Add separator line
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setStyleSheet("background-color: #e2e8f0; height: 1px;")
    grid.addWidget(separator, 1, 0, 1, 3)  # span across all columns

    row = 2  # Start after headers and separator

    # Helper function to add a parameter row
    def add_parameter_row(label, unit_widget, value_widget):
        type_label = QLabel(label)
        type_label.setProperty("class", "parameter-label")
        grid.addWidget(type_label, row, 0)
        grid.addWidget(unit_widget, row, 1)
        grid.addWidget(value_widget, row, 2)

    # Add the parameters
    if hasattr(self, 'result_EI_input'):
        add_parameter_row(
            "Initial thawed void ratio",
            self.result_EI_unit,
            self.result_EI_input
        )
        row += 1

    if hasattr(self, 'result_Cc_input'):
        add_parameter_row(
            "Thawed soil compression index",
            self.result_Cc_unit,
            self.result_Cc_input
        )
        row += 1

    if hasattr(self, 'result_Ck_input'):
        add_parameter_row(
            "Hydraulic conductivity index",
            self.result_Ck_unit,
            self.result_Ck_input
        )
        row += 1

    if hasattr(self, 'result_type_sol_choice'):
        add_parameter_row(
            "Ice content classification",
            self.result_type_sol_unit,
            self.result_type_sol_choice
        )
        row += 1

    # Set column stretches for responsive layout
    grid.setColumnStretch(0, 4)  # Type column gets more space
    grid.setColumnStretch(1, 1)  # Unit column
    grid.setColumnStretch(2, 1)  # Value column

    results_layout.addLayout(grid)
    self.results_group.setLayout(results_layout)
    self.results_group.setVisible(False)

    # Add to main layout
    main_layout = self.layout()
    if main_layout:
        left_widget = main_layout.itemAt(0).widget()
        if left_widget:
            left_layout = left_widget.layout()
            if left_layout:
                # Insert before the button layout (which is the last item)
                left_layout.insertWidget(left_layout.count() - 1, self.results_group)