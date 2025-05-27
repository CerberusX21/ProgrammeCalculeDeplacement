APP_STYLE = """
    QWidget {
    background-color: #f9f9f9;
    color: #212529;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

    QLabel {
        font-weight: 500;
        color: #333;
        padding: 5px;
        font-family: "Segoe UI";
    }

    QLineEdit {
        background-color: #ffffff;
        color: #212529;
        border: 1px solid #ced4da;
        border-radius: 6px;
        padding: 6px 10px;  
        min-width: 150px;   
        margin: 0px;
        min-height: 20px;
    }

    QComboBox {
        background-color: #ffffff;
        color: #212529;
        border: 1px solid #ced4da;
        border-radius: 6px;
        padding: 6px 10px;  
        min-width: 150px;
        min-height: 20px;
        max-width: 150px;
    }

    QLineEdit:focus, QComboBox:focus {
        border: 1px solid #0d6efd;
        background-color: #ffffff;
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 24px;
        border-left: 1px solid #ced4da;
        background-color: #f1f1f1;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
    }

    QComboBox::down-arrow {
        width: 12px;
        height: 12px;
        image: url(":/qt-project.org/styles/commonstyle/images/arrowdown-16.png");
        margin-right: 6px;
    }

    QPushButton {
        background-color: #0d6efd;
        color: white;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 6px;
        font-size: 14px;
    }

    QPushButton:hover {
        background-color: #0b5ed7;
    }

    QPushButton:pressed {
        background-color: #0a58ca;
    }

    QLabel#ResultLabel {
        background-color: #ffffff;
        border: 1px solid #0d6efd;
        border-radius: 6px;
        padding: 12px;
        font-size: 16px;
        color: #0d6efd;
        min-height: 60px;
        max-height: 70px;
        qproperty-alignment: 'AlignLeft';
    }

    QCheckBox {
        font-size: 14px;
        color: #212529;
        padding: 4px;
    }

    QCheckBox::indicator {
        width: 20px;
        height: 20px;
        border: 2px solid #0d6efd;
        border-radius: 4px;
        background-color: #ffffff;
    }

    QCheckBox::indicator:checked {
        background-color: #0d6efd;
        border-color: #0b5ed7;
    }

    QCheckBox::indicator:unchecked {
        background-color: #ffffff;
        border-color: #ced4da;
    }

    QCheckBox::indicator:pressed {
        background-color: #0a58ca;
    }

    QCheckBox::indicator:hover {
        border-color: #0d6efd;
    }

    /* Styles pour le QTabWidget */
    QTabWidget::pane {
        border: 1px solid #e2e6ea;
        border-radius: 12px;
        background-color: white;
        margin-top: -1px;
    }

    QTabBar::tab {
        background-color: transparent;
        color: #495057;
        font-weight: 500;
        font-size: 16px;
        padding: 12px 24px 12px 12px;
        margin-right: 6px;
        border: none;
        border-bottom: 3px solid transparent;
    }

    QTabBar::tab:selected {
        color: #0d6efd;
        font-weight: 600;
        border-bottom: 3px solid #0d6efd;
    }

    QTabBar::tab:hover {
        color: #0b5ed7;
        background-color: rgba(13, 110, 253, 0.1);
    }

    #parameterLabel {
        color: #333;
        font-size: 18px;
        font-family: "Segoe UI";
        padding: 4px;
    }
   
"""
