from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QSizePolicy, QGroupBox, QCheckBox, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from typing import List, Optional, Tuple
import os

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
    
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Results area avec coins arrondis
        self.results_area = QWidget()
        self.results_area.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                border: none;
            }
        """)
        
        # Layout for results
        self.results_layout = QVBoxLayout(self.results_area)
        self.results_layout.setContentsMargins(12, 12, 12, 12)
        self.results_layout.setSpacing(6)
        
        layout.addWidget(self.results_area)

    def clear(self):
        """Clear all results from the display."""
        for i in reversed(range(self.results_layout.count())): 
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def add_result(self, label, value):
        """Add a single result to the display."""
        result_label = QLabel(f"{label} {value}")
        result_label.setStyleSheet("""
            QLabel {
                color: #007bff;
                font-size: 14px;
                font-weight: 500;
                padding: 6px 8px;
                background-color: #f8f9fa;
                border: none;
                
            }
        """)
        self.results_layout.addWidget(result_label)

class ModernExportButton(QPushButton):
    """Un bouton d'export moderne avec style personnalisé et icône."""
    
    def __init__(self, text="Export", icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setup_icon(icon_path)
        self.setup_style()
    
    def setup_icon(self, icon_path):
        """Configure l'icône du bouton."""
        if icon_path:
            from PyQt6.QtGui import QIcon
            import os
            
            # Vérifier si le chemin existe
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                self.setIcon(icon)
                # Ajuster la taille de l'icône
                self.setIconSize(self.iconSize().scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            # Chemin par défaut pour l'icône export
            default_icon_path = r"C:\Users\Marika\Desktop\code stage été 2025\ProgrammeCalculeDeplacement\icons\export.ico"
            self.setup_icon(default_icon_path)
    
    def setup_style(self):
        """Configure le style moderne du bouton."""
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                color: white;
                font-size: 16px;
                font-weight: 500;
                padding: 6px 12px;
                padding-left: 8px;
                min-width: 70px;
                min-height: 28px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)

class ModernResultsPanel(QWidget):
    """A modern panel grouping results display and graphs with integrated export button."""
    def __init__(self):
        super().__init__()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Blue container panel avec coins arrondis
        self.blue_panel = QWidget()
        self.blue_panel.setStyleSheet("""
            QWidget {
                background-color: #007bff;
                border-radius: 16px;
                border: none;
            }
        """)
        
        # Layout for blue panel
        panel_layout = QVBoxLayout(self.blue_panel)
        panel_layout.setContentsMargins(16, 16, 16, 16)
        panel_layout.setSpacing(16)
        
        # Header with title and export button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        # Title
        title = QLabel("Results")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                font-family: "Segoe UI";
                margin: 0;
                padding: 0;
            }
        """)
        
        # Export button
        self.export_button = ModernExportButton("Export")
   
        
        # Add to header layout
        header_layout.addWidget(title)
        header_layout.addStretch()  # Push export button to the right
        header_layout.addWidget(self.export_button)
        
        panel_layout.addLayout(header_layout)
        
        # Content container
        self.content_container = QWidget()
        self.content_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)
        panel_layout.addWidget(self.content_container)
        
        main_layout.addWidget(self.blue_panel)

    def add_widget(self, widget):
        """Add a widget to the content container."""
        self.content_layout.addWidget(widget)
    
    def get_export_button(self):
        """Return the export button for signal connections."""
        return self.export_button