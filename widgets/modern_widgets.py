from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QSizePolicy, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt

class ModernGroupBox(QGroupBox):
    def __init__(self, title, icon=""):
        super().__init__()
        self.setTitle(title)
        self.setObjectName("modernGroupBox")

class ModernParameterWidget(QWidget):
    """Widget moderne pour les paramètres avec tableau structuré"""

    def __init__(self, param_name, param_widget, unit_widget, value_widget, help_text=""):
        super().__init__()
        self.setup_ui(param_name, param_widget, unit_widget, value_widget, help_text)

    def setup_ui(self, param_name, param_widget, unit_widget, value_widget, help_text):
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        name_label = QLabel(param_name)
        name_label.setObjectName("parameterName")
        if help_text:
            name_label.setToolTip(help_text)
        
        # Ajustement des widgets
        if param_widget:
            param_widget.setMinimumWidth(100)
            param_widget.setMaximumWidth(120)
        if unit_widget:
            unit_widget.setMinimumWidth(60)
            unit_widget.setMaximumWidth(80)
        if value_widget:
            value_widget.setMinimumWidth(80)
        
        # Organisation en colonnes
        layout.addWidget(name_label, 0, 0)
        if param_widget:
            layout.addWidget(param_widget, 0, 1)
        if unit_widget:
            layout.addWidget(unit_widget, 0, 2)
        if value_widget:
            layout.addWidget(value_widget, 0, 3)
        
        # Proportions des colonnes
        layout.setColumnStretch(0, 3)  # Nom du paramètre
        layout.setColumnStretch(1, 2)  # Paramètre
        layout.setColumnStretch(2, 1)  # Unité
        layout.setColumnStretch(3, 2)  # Valeur
        
        self.setLayout(layout)

class ModernSoilParameterSection(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(4, 4, 4, 4)
        
        # Headers
        headers = QGridLayout()
        type_header = QLabel("Type")
        unit_header = QLabel("Unit")
        value_header = QLabel("Value")
        
        # Style headers
        for header in [type_header, unit_header, value_header]:
            header.setProperty("class", "column-header")
            header.setAlignment(Qt.AlignmentFlag.AlignLeft)
            header.setStyleSheet("background: transparent;")
        
        headers.addWidget(type_header, 0, 0)
        headers.addWidget(unit_header, 0, 1)
        headers.addWidget(value_header, 0, 2)
        headers.setColumnStretch(0, 4)
        headers.setColumnStretch(1, 1)
        headers.setColumnStretch(2, 1)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e2e8f0; height: 1px;")
        
        self.layout.addLayout(headers)
        self.layout.addWidget(separator)
        
        # Parameters will be added using add_parameter()
        self.parameters_layout = QVBoxLayout()
        self.parameters_layout.setSpacing(6)
        self.layout.addLayout(self.parameters_layout)
    
    def add_parameter(self, label, type_widget, unit_widget, value_widget):
        row = QGridLayout()
        row.setSpacing(4)
        
        # Create and style the label
        label_widget = QLabel(label)
        label_widget.setProperty("class", "parameter-label")
        label_widget.setStyleSheet("background: transparent;")
        
        # Add widgets to row
        row.addWidget(label_widget, 0, 0)
        row.addWidget(type_widget, 0, 1)
        row.addWidget(unit_widget, 0, 2)
        row.addWidget(value_widget, 0, 3)
        
        # Set column stretches
        row.setColumnStretch(0, 4)  # Label
        row.setColumnStretch(1, 2)  # Type
        row.setColumnStretch(2, 1)  # Unit
        row.setColumnStretch(3, 2)  # Value
        
        self.parameters_layout.addLayout(row)

class ModernResultsSection(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8)  # Reduced from 12
        self.layout.setContentsMargins(4, 6, 4, 6)  # Reduced from 8
        
        # Parameters will be added using add_result()
        self.parameters_layout = QVBoxLayout()
        self.parameters_layout.setSpacing(4)  # Reduced from 6
        self.layout.addLayout(self.parameters_layout)
    
    def add_result(self, label, unit_widget, value_widget):
        # Create grid layout for the widgets
        grid = QGridLayout()
        grid.setSpacing(3)  # Reduced from 4
        grid.setContentsMargins(2, 0, 2, 0)
        
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
        
        # Create a checkbox for the type column
        type_checkbox = QCheckBox(label)
        type_checkbox.setStyleSheet("background: transparent;")
        type_checkbox.setChecked(False)  # Set unchecked by default
        
        # Connect checkbox to enable/disable the input fields
        type_checkbox.stateChanged.connect(
            lambda state: self._toggle_input_fields(state, [unit_widget, value_widget])
        )
        
        # Add widgets to grid
        grid.addWidget(type_checkbox, 1, 0)
        grid.addWidget(value_widget, 1, 1)
        grid.addWidget(unit_widget, 1, 2)
        
        # Set column stretches for responsive layout
        grid.setColumnStretch(0, 4)  # Type column gets more space
        grid.setColumnStretch(1, 1)  # Value column
        grid.setColumnStretch(2, 1)  # Unit column
        
        # Initialize widgets as disabled since checkbox is unchecked by default
        value_widget.setEnabled(False)
        unit_widget.setEnabled(False)
        
        self.parameters_layout.addLayout(grid)
    
    def _toggle_input_fields(self, state, widgets):
        """Enable or disable input fields based on checkbox state"""
        is_enabled = state == Qt.CheckState.Checked.value
        for widget in widgets:
            widget.setEnabled(is_enabled)
