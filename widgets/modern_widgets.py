from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QSizePolicy, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt
from typing import List, Optional, Tuple

class ModernGroupBox(QGroupBox):
    """A modern styled group box with optional icon."""
    def __init__(self, title: str = "", icon: str = ""):
        super().__init__()
        self.setTitle(title)
        self.setObjectName("modernGroupBox")

class ModernParameterWidget(QWidget):
    """A modern widget for displaying parameters in a structured table format."""
    
    COLUMN_STRETCHES = {
        "name": 3,    # Parameter name column
        "param": 2,   # Parameter column
        "unit": 1,    # Unit column
        "value": 2    # Value column
    }
    
    def __init__(self, param_name: str, param_widget: Optional[QWidget] = None, 
                 unit_widget: Optional[QWidget] = None, value_widget: Optional[QWidget] = None, 
                 help_text: str = ""):
        super().__init__()
        self.setup_ui(param_name, param_widget, unit_widget, value_widget, help_text)

    def setup_ui(self, param_name: str, param_widget: Optional[QWidget], 
                 unit_widget: Optional[QWidget], value_widget: Optional[QWidget], 
                 help_text: str) -> None:
        """Set up the UI layout with proper spacing and sizing."""
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Create and configure name label
        name_label = QLabel(param_name)
        name_label.setObjectName("parameterName")
        if help_text:
            name_label.setToolTip(help_text)
        
        # Set widget dimensions
        self._configure_widget_sizes(param_widget, unit_widget, value_widget)
        
        # Add widgets to layout
        layout.addWidget(name_label, 0, 0)
        widgets = [(param_widget, 1), (unit_widget, 2), (value_widget, 3)]
        for widget, col in widgets:
            if widget:
                layout.addWidget(widget, 0, col)
        
        # Set column stretches
        for col, stretch in self.COLUMN_STRETCHES.items():
            layout.setColumnStretch(list(self.COLUMN_STRETCHES.keys()).index(col), stretch)
        
        self.setLayout(layout)

    def _configure_widget_sizes(self, param_widget: Optional[QWidget], 
                              unit_widget: Optional[QWidget], 
                              value_widget: Optional[QWidget]) -> None:
        """Configure the sizes of the widgets."""
        if param_widget:
            param_widget.setMinimumWidth(100)
            param_widget.setMaximumWidth(120)
        if unit_widget:
            unit_widget.setMinimumWidth(60)
            unit_widget.setMaximumWidth(80)
        if value_widget:
            value_widget.setMinimumWidth(80)

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
    """A modern section for displaying results with optional checkboxes."""
    
    DISABLED_STYLE = """
        QLineEdit:disabled, QComboBox:disabled {
            background-color: #f0f0f0;
            color: #666666;
            border: 1px solid #cccccc;
        }
    """
    
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI layout."""
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(4, 6, 4, 6)
        
        self.parameters_layout = QVBoxLayout()
        self.parameters_layout.setSpacing(4)
        self.layout.addLayout(self.parameters_layout)

    def add_result(self, label: str, unit_widget: QWidget, value_widget: QWidget) -> QCheckBox:
        """Add a result row with label, unit, and value widgets."""
        grid = self._create_result_grid()
        checkbox = self._create_result_checkbox(label, [unit_widget, value_widget])
        
        self._add_widgets_to_grid(grid, checkbox, unit_widget, value_widget)
        self.parameters_layout.addLayout(grid)
        return checkbox

    def add_result_no_value(self, label: str, unit_widget: QWidget) -> QCheckBox:
        """Add a result row with only a unit selection."""
        grid = self._create_result_grid()
        checkbox = self._create_result_checkbox(label, [unit_widget])
        
        grid.addWidget(checkbox, 0, 0)
        grid.addWidget(unit_widget, 0, 1)
        
        grid.setColumnStretch(0, 4)  # Checkbox
        grid.setColumnStretch(1, 2)  # Unit
        
        self.parameters_layout.addLayout(grid)
        return checkbox

    def _create_result_grid(self) -> QGridLayout:
        """Create a grid layout for results with proper spacing."""
        grid = QGridLayout()
        grid.setSpacing(3)
        grid.setContentsMargins(2, 0, 2, 0)
        return grid

    def _create_result_checkbox(self, label: str, widgets: List[QWidget]) -> QCheckBox:
        """Create a checkbox that controls the enabled state of widgets."""
        checkbox = QCheckBox(label)
        for widget in widgets:
            widget.setStyleSheet(self.DISABLED_STYLE)
            widget.setEnabled(False)
        checkbox.stateChanged.connect(
            lambda state: self._toggle_widgets(state, widgets)
        )
        return checkbox

    def _add_widgets_to_grid(self, grid: QGridLayout, checkbox: QCheckBox, 
                            unit_widget: QWidget, value_widget: QWidget) -> None:
        """Add widgets to the grid with proper stretching."""
        grid.addWidget(checkbox, 0, 0)
        grid.addWidget(value_widget, 0, 1)
        grid.addWidget(unit_widget, 0, 2)
        
        grid.setColumnStretch(0, 4)  # Checkbox
        grid.setColumnStretch(1, 2)  # Value
        grid.setColumnStretch(2, 1)  # Unit

    def _toggle_widgets(self, state: int, widgets: List[QWidget]) -> None:
        """Toggle the enabled state of widgets based on checkbox state."""
        enabled = state == Qt.CheckState.Checked.value
        for widget in widgets:
            widget.setEnabled(enabled)

class ModernResultsDisplay(QWidget):
    """A modern widget for displaying calculation results."""
    
    STYLES = {
        "frame": """
            QFrame#resultsFrame {
                background-color: transparent;
                border: 1px solid #007bff;
                border-radius: 6px;
            }
        """,
        "label": """
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                padding: 2px;
                font-family: "Segoe UI", Arial, sans-serif;
            }
        """,
        "value": """
            QLabel[class="value"] {
                color: #007bff;
                font-weight: 600;
                font-size: 15px;
            }
        """,
        "unit": """
            QLabel[class="unit"] {
                color: #6c757d;
                font-size: 13px;
            }
        """,
        "header": """
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
        """,
        "separator": """
            QFrame[class="separator"] {
                background-color: #e9ecef;
                min-height: 1px;
                max-height: 1px;
            }
        """
    }
    
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(4)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self._create_frame()
        self._create_header()
        self._create_separator()
        self._create_results_container()
        
        self.current_row = 0

    def _create_frame(self) -> None:
        """Create the main frame for results."""
        self.frame = QFrame()
        self.frame.setObjectName("resultsFrame")
        self.frame.setStyleSheet("\n".join(self.STYLES.values()))
        
        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setSpacing(2)
        self.frame_layout.setContentsMargins(0, 0, 0, 12)
        
        self.layout.addWidget(self.frame)

    def _create_header(self) -> None:
        """Create the header section."""
        self.header = QLabel("Results")
        self.header.setProperty("class", "header")
        self.frame_layout.addWidget(self.header)

    def _create_separator(self) -> None:
        """Create the separator line."""
        self.separator = QFrame()
        self.separator.setProperty("class", "separator")
        self.frame_layout.addWidget(self.separator)

    def _create_results_container(self) -> None:
        """Create the container for results."""
        self.results_container = QWidget()
        container_layout = QVBoxLayout(self.results_container)
        container_layout.setContentsMargins(16, 4, 16, 0)
        container_layout.setSpacing(0)
        
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setVerticalSpacing(1)
        container_layout.addLayout(self.grid)
        
        self.frame_layout.addWidget(self.results_container)

    def add_result(self, label: str, value: str, unit: str = "") -> None:
        """Add a result row with optional label and unit."""
        if not label:
            self._add_simple_result(value)
        else:
            self._add_detailed_result(label, value, unit)
        self.current_row += 1

    def _add_simple_result(self, value: str) -> None:
        """Add a simple text result centered in the row."""
        text_widget = QLabel(value)
        text_widget.setProperty("class", "value")
        text_widget.setWordWrap(True)
        text_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_widget.setContentsMargins(0, 0, 0, 0)
        self.grid.addWidget(text_widget, self.current_row, 0, 1, 3)

    def _add_detailed_result(self, label: str, value: str, unit: str) -> None:
        """Add a detailed result row with label, value, and optional unit."""
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

    def clear(self) -> None:
        """Clear all results from the display."""
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.current_row = 0
