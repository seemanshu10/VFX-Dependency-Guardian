"""Main Entry Point For UI"""

from PySide2.QtWidgets import QMainWindow, QWidget
from src.constants import APP_TITLE

class MainWindow(QMainWindow):
    """Main Apllication window interfaces"""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(APP_TITLE)