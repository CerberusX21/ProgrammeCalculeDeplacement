from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QGroupBox
from PyQt6.QtCore import Qt

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


class ModernGroupBox(QGroupBox):
    def __init__(self, title, icon=""):
        super().__init__()
        self.setTitle(title)
        self.setObjectName("modernGroupBox")
