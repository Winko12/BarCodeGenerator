# FILE: main.py
# PURPOSE: The entry point of our application.
# VERSION: 4.1 (Final)

import sys
from PyQt6.QtWidgets import QApplication
from ui_main_window import BarcodeApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BarcodeApp()
    window.show()
    sys.exit(app.exec())