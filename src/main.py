# src/main.py
import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import QuMailWindow

def main():
    app = QApplication(sys.argv)
    window = QuMailWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

