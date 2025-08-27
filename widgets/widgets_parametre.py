from PyQt6.QtWidgets import QHBoxLayout, QWidget, QSizePolicy
from PyQt6.QtCore import Qt

def parametre(widget1, widget2, widget3):
    """Crée une ligne horizontale avec trois widgets (1:1:3 en étirement)."""
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(10)
    row.addWidget(widget1, 1)
    row.addWidget(widget2, 1)
    row.addWidget(widget3, 3)
    container = QWidget()
    container.setLayout(row)
    return container

def parametre_result_inter(widget1, widget2):
    """Crée une ligne centrée avec un libellé et un champ de valeur fixe."""
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(10)
    row.addStretch(1)
    row.addWidget(widget1)
    row.addStretch(1)
    row.addWidget(widget2)
    row.setStretch(0, 1)
    row.setStretch(1, 0)
    row.setStretch(2, 1)
    row.setStretch(3, 2)
    widget2.setSizePolicy(QSizePolicy.Policy.Fixed, widget2.sizePolicy().verticalPolicy())
    container = QWidget()
    container.setLayout(row)
    return container
