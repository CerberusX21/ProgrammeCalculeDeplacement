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
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(4, 6, 4, 6)
        
        self.parameters_layout = QVBoxLayout()
        self.parameters_layout.setSpacing(4)
        self.layout.addLayout(self.parameters_layout)

        # Define the disabled style
        self.DISABLED_STYLE = """
            QLineEdit:disabled, QComboBox:disabled {
                background-color: #f0f0f0;
                color: #666666;
                border: 1px solid #cccccc;
            }
        """
    
    def add_result(self, label, unit_widget, value_widget):
        # Create grid layout
        grid = QGridLayout()
        grid.setSpacing(3)
        grid.setContentsMargins(2, 0, 2, 0)
        
        # Create checkbox
        checkbox = QCheckBox(label)
        
        # Apply styles
        value_widget.setStyleSheet(self.DISABLED_STYLE)
        unit_widget.setStyleSheet(self.DISABLED_STYLE)
        
        # Set initial state - disabled
        value_widget.setEnabled(False)
        unit_widget.setEnabled(False)
        
        # Connect checkbox to enable/disable widgets
        checkbox.stateChanged.connect(
            lambda state: self._toggle_widgets(state, [value_widget, unit_widget])
        )
        
        # Add widgets to grid
        grid.addWidget(checkbox, 0, 0)
        grid.addWidget(value_widget, 0, 1)
        grid.addWidget(unit_widget, 0, 2)
        
        # Set column stretches
        grid.setColumnStretch(0, 4)  # Checkbox
        grid.setColumnStretch(1, 2)  # Value
        grid.setColumnStretch(2, 1)  # Unit
        
        self.parameters_layout.addLayout(grid)
        return checkbox
    
    def _toggle_widgets(self, state, widgets):
        enabled = state == Qt.CheckState.Checked.value
        for widget in widgets:
            widget.setEnabled(enabled)

    def add_result_no_value(self, label, unit_widget):
        """Add a result row with only a unit selection (no value input)"""
        # Create grid layout
        grid = QGridLayout()
        grid.setSpacing(3)
        grid.setContentsMargins(2, 0, 2, 0)
        
        # Create checkbox
        checkbox = QCheckBox(label)
        
        # Apply styles
        unit_widget.setStyleSheet(self.DISABLED_STYLE)
        
        # Set initial state - disabled
        unit_widget.setEnabled(False)
        
        # Add widgets to grid
        grid.addWidget(checkbox, 0, 0)
        grid.addWidget(unit_widget, 0, 1)
        
        # Set column stretches
        grid.setColumnStretch(0, 4)  # Checkbox
        grid.setColumnStretch(1, 2)  # Unit
        
        self.parameters_layout.addLayout(grid)
        return checkbox

class ModernResultsDisplay(QWidget):
    """A modern-looking widget for displaying calculation results"""
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(4)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a frame for the results
        self.frame = QFrame()
        self.frame.setObjectName("resultsFrame")
        self.frame.setStyleSheet("""
            QFrame#resultsFrame {
                background-color: transparent;
                border: 1px solid #007bff;
                border-radius: 6px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                padding: 2px;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel[class="value"] {
                color: #007bff;
                font-weight: 600;
                font-size: 15px;
            }
            QLabel[class="unit"] {
                color: #6c757d;
                font-size: 13px;
            }
            QLabel[class="header"] {
                color: #ffffff;
                background-color: #007bff;
                font-weight: 600;
                padding: 3px 8px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-size: 12px;
                min-height: 20px;
                max-height: 20px;
            }
            QFrame[class="separator"] {
                background-color: #e9ecef;
                min-height: 1px;
                max-height: 1px;
            }
        """)
        
        # Create layout for the frame
        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setSpacing(2)
        self.frame_layout.setContentsMargins(0, 0, 0, 12)
        
        # Add header
        self.header = QLabel("Results")
        self.header.setProperty("class", "header")
        self.frame_layout.addWidget(self.header)
        
        # Add separator
        self.separator = QFrame()
        self.separator.setProperty("class", "separator")
        self.frame_layout.addWidget(self.separator)
        
        # Create container for results
        self.results_container = QWidget()
        container_layout = QVBoxLayout(self.results_container)
        container_layout.setContentsMargins(16, 4, 16, 0)
        container_layout.setSpacing(0)
        
        # Create grid for results
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setVerticalSpacing(1)
        container_layout.addLayout(self.grid)
        
        self.frame_layout.addWidget(self.results_container)
        
        # Add frame to main layout
        self.layout.addWidget(self.frame)
        
        # Keep track of current row
        self.current_row = 0
        
    def add_result(self, label: str, value: str, unit: str = ""):
        """Add a result row with label, value, and optional unit"""
        if not label:  # For simple text display without label
            text_widget = QLabel(value)
            text_widget.setProperty("class", "value")
            text_widget.setWordWrap(True)
            text_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_widget.setContentsMargins(0, 0, 0, 0)
            self.grid.addWidget(text_widget, self.current_row, 0, 1, 3)
        else:
            # Label
            label_widget = QLabel(f"{label}:")
            label_widget.setContentsMargins(0, 0, 0, 0)
            self.grid.addWidget(label_widget, self.current_row, 0)
            
            # Value
            value_widget = QLabel(value)
            value_widget.setProperty("class", "value")
            value_widget.setContentsMargins(0, 0, 0, 0)
            self.grid.addWidget(value_widget, self.current_row, 1)
            
            # Unit (if provided)
            if unit:
                unit_widget = QLabel(unit)
                unit_widget.setProperty("class", "unit")
                unit_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                unit_widget.setContentsMargins(0, 0, 0, 0)
                self.grid.addWidget(unit_widget, self.current_row, 2)
        
        self.current_row += 1
        
    def clear(self):
        """Clear all results"""
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.current_row = 0
