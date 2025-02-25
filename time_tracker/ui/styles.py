DARK_THEME = """
QMainWindow {
    background-color: #2b2b2b;
}
QWidget {
    color: #ffffff;
    font-family: 'Segoe UI', Arial;
}
QPushButton {
    background-color: #0d47a1;
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1565c0;
}
QPushButton:disabled {
    background-color: #666666;
}
QTableWidget {
    background-color: #1e1e1e;
    border: 1px solid #333333;
    gridline-color: #333333;
}
QTableWidget::item {
    padding: 5px;
}
QHeaderView::section {
    background-color: #0d47a1;
    color: white;
    padding: 5px;
    border: 1px solid #333333;
}
QLabel {
    color: #ffffff;
    font-size: 12px;
}
QLabel#titleLabel {
    font-size: 24px;
    color: #1565c0;
    font-weight: bold;
}
QLabel#authorLabel {
    font-size: 14px;
    color: #90caf9;
    font-style: italic;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
}
QWidget {
    color: #000000;
    font-family: 'Segoe UI', Arial;
}
QPushButton {
    background-color: #1976d2;
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1565c0;
}
QPushButton:disabled {
    background-color: #bbbbbb;
}
QTableWidget {
    background-color: white;
    border: 1px solid #dddddd;
    gridline-color: #dddddd;
}
QTableWidget::item {
    padding: 5px;
}
QHeaderView::section {
    background-color: #1976d2;
    color: white;
    padding: 5px;
    border: 1px solid #dddddd;
}
QLabel {
    color: #000000;
    font-size: 12px;
}
QLabel#titleLabel {
    font-size: 24px;
    color: #1976d2;
    font-weight: bold;
}
QLabel#authorLabel {
    font-size: 14px;
    color: #1565c0;
    font-style: italic;
}
""" 