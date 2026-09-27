"""Main Entry Point For UI"""

from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QRadioButton
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
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.create_header()

    def create_header(self):
        # create menu BAr
        # menubar = self.menuBar()
        # # file Menu 
        # file_menu = menubar.addAction("File")

        layout_main = QVBoxLayout(self.central_widget)

        main_title = QLabel("Dependency Validator")
        subtitle = QLabel("Validate published assets and shots against the approved registry.")

        layout_main.addWidget(main_title)
        layout_main.addWidget(subtitle)

        frame = QFrame()
        frame_layout = QHBoxLayout(frame)

        self.asset_btn = QPushButton(" Assets ")
        self.shots_btn = QPushButton(" Shots ")

        frame_layout.addWidget(self.asset_btn)
        frame_layout.addWidget(self.shots_btn)

        layout_main.addWidget(frame)
        layout_main.addStretch()

        validation_frame = QFrame()

        validation_layout = QHBoxLayout(validation_frame)
        # validation_layout.setContentsMargins(18, 14, 18, 14)
        # validation_layout.setSpacing(16)

        #scope 
        validation_scope_main_box = QVBoxLayout()
        scope_label = QLabel("Validation Scope")
        
        radio_box = QHBoxLayout()
        self.all_radio = QRadioButton("All Assets")
        self.selected_radio = QRadioButton("Selected Assets")
        self.single_radio = QRadioButton("Single Asset")

        validation_scope_main_box.addWidget(scope_label)
        radio_box.addWidget(self.all_radio)
        radio_box.addWidget(self.selected_radio)
        radio_box.addWidget(self.single_radio)
        validation_scope_main_box.addLayout(radio_box)

        validation_layout.addLayout(validation_scope_main_box, 2)
        validation_layout.addWidget(self.vertical_line())

        # adding Comboboxes 
        validation_layout.addLayout(self.combobox_build)

        layout_main.addWidget(validation_frame)

    def vertical_line(self):
            line = QFrame()
            line.setFrameShape(QFrame.VLine)
            line.setObjectName("verticalLine")
            return line


                


