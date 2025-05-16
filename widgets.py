from PyQt6.QtWidgets import QHBoxLayout, QWidget

def parametre(widget1, widget2, widget3):
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(10)
    row.addWidget(widget1, 1)
    row.addWidget(widget2, 1)
    row.addWidget(widget3, 3)
    container = QWidget()
    container.setLayout(row)
    return container

def parametre_result_inter(checkbox, line_edit):
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(10)
    row.addStretch(1)
    row.addWidget(checkbox)
    row.addStretch(1)
    row.addWidget(line_edit)
    row.setStretch(0, 1)
    row.setStretch(1, 0)
    row.setStretch(2, 1)
    row.setStretch(3, 2)
    container = QWidget()
    container.setLayout(row)
    return container
