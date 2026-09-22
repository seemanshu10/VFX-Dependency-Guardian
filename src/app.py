"""Main Application Initialization """

import sys
from PySide2.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def run():
    """Run The Application"""
    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()