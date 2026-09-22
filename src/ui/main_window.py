"""Main Entry Point For UI"""

from PySide2.QtWidgets import QMainWindow, QWidget
from src.constants import APP_TITLE, WINDOW_HEIGHT, WINDOW_WIDTH

class MainWindow(QMainWindow):
    """Main Apllication window interfaces"""

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        #set window Size and Properties 
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Create Central Widget and Layout 
        central_widget = QWidget()
        self.setCentralWidget(central_widget)