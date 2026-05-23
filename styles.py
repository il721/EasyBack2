
# Centralized styles for EasyBack2 based on DESIGN.md from EasyBack project

GLOBAL_STYLE = """
QMainWindow {
    background-color: rgb(30, 30, 30);
}

QWidget {
    background-color: rgb(30, 30, 30);
    color: rgb(230, 230, 230);
    font-family: 'Lexend Light', 'Segoe UI', sans-serif;
    font-size: 14pt;
}

QGroupBox {
    border: 2px solid #2B79C2;
    border-radius: 15px;
    margin-top: 20px;
    font-weight: bold;
    padding: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 20px;
    padding: 0 5px 0 5px;
}

QPushButton {
    background-color: rgba(60, 60, 60, 80);
    border: 2px solid #2B79C2;
    border-radius: 10px;
    padding: 8px 15px;
    color: rgb(230, 230, 230);
}

QPushButton:hover {
    background-color: rgba(30, 30, 30, 180);
    border: 2px solid #ffffff;
}

QPushButton:pressed {
    background-color: #2B79C2;
    color: white;
}

QTableWidget {
    background-color: rgb(40, 40, 40);
    border: 1px solid #2B79C2;
    border-radius: 5px;
    gridline-color: rgb(60, 60, 60);
    color: rgb(230, 230, 230);
}

QHeaderView::section {
    background-color: rgb(50, 50, 50);
    color: rgb(230, 230, 230);
    padding: 5px;
    border: 1px solid #2B79C2;
}

QLineEdit {
    background-color: rgb(45, 45, 45);
    border: 2px solid #2B79C2;
    border-radius: 5px;
    padding: 5px;
    color: rgb(230, 230, 230);
}

QProgressBar {
    border: 2px solid #2B79C2;
    border-radius: 5px;
    text-align: center;
    background-color: rgb(45, 45, 45);
}

QProgressBar::chunk {
    background-color: #2B79C2;
    width: 20px;
}

QLabel {
    color: rgb(230, 230, 230);
}
"""

START_BUTTON_STYLE = """
QPushButton {
    background-color: #2B79C2;
    color: white;
    font-weight: bold;
    font-size: 18pt;
    border-radius: 15px;
    padding: 15px;
}
QPushButton:hover {
    background-color: #3586d1;
}
"""

STATUS_LABEL_STYLE = "color: #2B79C2; font-weight: bold; font-size: 14pt;"
