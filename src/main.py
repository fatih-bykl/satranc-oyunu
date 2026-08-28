#!/usr/bin/env python3
"""
Linux Yapay Zeka Destekli Satranç Oyunu
Ana Giriş Noktası (Entry Point)
"""
import sys
import os

# Proje kök dizinini sys.path'e ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
from PyQt6.QtCore import Qt

from src.ui.main_window import MainWindow

DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'DejaVu Sans', 'Liberation Sans', sans-serif;
}

QToolBar {
    background-color: #252526;
    border-bottom: 1px solid #333333;
    padding: 6px;
    spacing: 8px;
}

QPushButton {
    background-color: #333333;
    color: #ffffff;
    border: 1px solid #474747;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #404040;
    border-color: #555555;
}

QPushButton:pressed {
    background-color: #252526;
}

QComboBox {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 5px 10px;
    min-height: 24px;
}

QComboBox:hover {
    border-color: #666666;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #ffffff;
    selection-background-color: #3e5f8a;
    border: 1px solid #444444;
}

QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
    background-color: #252526;
    color: #ffffff;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 6px;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #007acc;
}

QGroupBox {
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    margin-top: 14px;
    font-weight: bold;
    padding-top: 14px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
    color: #81c784;
}

QListWidget {
    background-color: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 4px;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
}

QListWidget::item:selected {
    background-color: #375375;
    color: #ffffff;
}

QStatusBar {
    background-color: #1a1a1a;
    color: #888888;
    border-top: 1px solid #2d2d2d;
}
"""

import traceback

def exception_hook(exctype, value, tb):
    print("Beklenmeyen Hata:", exctype, value)
    traceback.print_tb(tb)
    sys.__excepthook__(exctype, value, tb)

def main():
    sys.excepthook = exception_hook

    # Yüksek DPI ekran ölçeklendirmesini aktifleştir
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Satranç Oyunu")
    app.setApplicationVersion("1.0.0")
    
    icon_path = os.path.join(project_root, "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    app.setStyleSheet(DARK_STYLESHEET)

    # Ana Pencereyi Başlat
    window = MainWindow(project_root)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
