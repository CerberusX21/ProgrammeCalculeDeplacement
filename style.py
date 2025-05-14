APP_STYLE = """
    QWidget {
        background-color: #f9f9f9;
        color: #212529;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
    }
    QLabel {
        font-weight: 600;
        color: #333;
    }
    QLineEdit, QComboBox {
        background-color: #ffffff;
        color: #212529;
        border: 1px solid #ced4da;
        border-radius: 6px;
        padding: 6px 30px 6px 10px;
        min-width: 120px;
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
        min-height: 40px;
        max-height: 40px;
        qproperty-alignment: 'AlignLeft';
    }
"""
