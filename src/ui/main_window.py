"""Main Entry Point For UI"""
from PySide2 import QtWidgets
from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QRadioButton, QComboBox, QSplitter, QLineEdit, QTableWidget
from PySide2.QtCore import Qt
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
        

        validation_frame = QFrame()

        validation_layout = QHBoxLayout(validation_frame)
        validation_layout.setContentsMargins(18, 14, 18, 14)
        validation_layout.setSpacing(16)

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

        validation_layout.addLayout(validation_scope_main_box, 10)
        validation_layout.addWidget(self.line_creation(QFrame.VLine))

        # adding Comboboxes 
        validation_layout.addLayout(self.combobox_build("Project", ["Demo_project"]))
        validation_layout.addLayout(self.combobox_build("Asset Type",  ["All", "Character", "Prop", "Environment", "FX"]))
        run_btn = QPushButton("▶   Run Validation")
        validation_layout.addWidget(run_btn)
        run_btn.setMinimumWidth(174)
        run_btn.setMinimumHeight(44)
        layout_main.addWidget(validation_frame)

        layout_main.addWidget(self.create_summary())
        layout_main.addWidget(self.create_main_area(), 1)

        layout_main.addStretch()

    # ------------------------------------------------------------------------
    #  Results
    # ------------------------------------------------------------------------

    def create_main_area(self):
        main_area_splitter = QSplitter(Qt.Horizontal)
        main_area_splitter.addWidget(self.create_results_panel())
        main_area_splitter.addWidget(self.create_details_panel())
        # main_area_splitter.addWidget(QPushButton("Run"))

        main_area_splitter.setStretchFactor(0, 2)
        main_area_splitter.setStretchFactor(1, 1.5)

        return main_area_splitter

    def create_results_panel(self):
        frame_results = QFrame()
        frame_layout = QVBoxLayout(frame_results)
        
        frame_layout.setContentsMargins(14, 14, 14, 14)
        frame_layout.setSpacing(10)

        # validation Results 
        top_layout = QHBoxLayout()

        validate_title = QLabel("Validation Results")
        top_layout.addWidget(validate_title)
        top_layout.addStretch()

        # Search box Creation 
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("⌕  Search assets...")
        top_layout.addWidget(self.search_box)
        self.search_box.setFixedWidth(225)

        # list Table Widgets 
        self.details_table_widget = QTableWidget()
        self.details_table_widget.setColumnCount(5)
        self.details_table_widget.setHorizontalHeaderLabels(
            ["", "ASSET", "TYPE", "STATUS", "ISSUES"]
        )
        self.details_table_widget.setColumnWidth(10, 42)

        header = self.details_table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        
        frame_layout.addLayout(top_layout)
        frame_layout.addWidget(self.details_table_widget, 1)

        return frame_results

    # ------------------------------------------------------------------------
    #  Details
    # ------------------------------------------------------------------------

    def create_details_panel(self):
        frame = QFrame()

        details_main_layout = QVBoxLayout(frame)
        details_main_layout.setContentsMargins(16, 16, 16, 16)
        details_main_layout.setSpacing(10)

        header = QtWidgets.QHBoxLayout()
        
        self.detail_icon = QtWidgets.QLabel("⬡")
        self.detail_icon.setFixedWidth(36)
        self.detail_name = QtWidgets.QLabel("character_A")
        self.detail_status = QtWidgets.QLabel("●  FAILED")

        header.addWidget(self.detail_icon)
        header.addWidget(self.detail_name)
        header.addStretch()
        header.addWidget(self.detail_status)

        info = QtWidgets.QLabel(
                    "Type:  Character\n"
                    "Project:  demo_project\n"
                    "Path:  /assets/characters/character_A"
                )
        
        details_main_layout.addLayout(header)
        details_main_layout.addWidget(info)

        details_main_layout.addWidget(self.line_creation(QFrame.HLine))

        dependency_detail_label = QLabel("Dependency Details")
        details_main_layout.addWidget(dependency_detail_label)

        self.dependency_table_widget = QTableWidget()
        self.dependency_table_widget.setColumnCount(4)
        self.dependency_table_widget.setHorizontalHeaderLabels(
                    ["COMPONENT", "CURRENT", "EXPECTED", "STATUS"]
                )
        self.dependency_table_widget.setShowGrid(True)
        self.dependency_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.dependency_table_widget.horizontalHeader().setSectionResizeMode(
                0, QtWidgets.QHeaderView.Stretch
            )
        self.dependency_table_widget.horizontalHeader().setSectionResizeMode(
                1, QtWidgets.QHeaderView.ResizeToContents
            )
        self.dependency_table_widget.horizontalHeader().setSectionResizeMode(
                2, QtWidgets.QHeaderView.ResizeToContents
            )
        self.dependency_table_widget.horizontalHeader().setSectionResizeMode(
                3, QtWidgets.QHeaderView.ResizeToContents
            )

        details_main_layout.addWidget(self.dependency_table_widget)
        report_title = QtWidgets.QLabel("Detailed Report")
        report_title.setObjectName("subTitle")
        details_main_layout.addWidget(report_title)

        self.report = QtWidgets.QPlainTextEdit()
        self.report.setReadOnly(True)
        self.report.setObjectName("reportBox")
        details_main_layout.addWidget(self.report, 1)
        
        return frame

    def combobox_build(self, label_text, values):
        box = QVBoxLayout()
        label = QLabel(label_text)

        combo = QComboBox()
        combo.addItems(values)

        box.addWidget(label)
        box.addWidget(combo)

        return box

    def create_summary(self):
        frame = QFrame()

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 10, 18, 10)
        validation_label = QLabel("Validation Summary")
        layout.addWidget(validation_label) 
        values = [
            ("✓", "124", "OK", "ok"),
            ("●", "18", "OUTDATED", "outdated"),
            ("×", "7", "MISSING", "missing"),
            ("●", "2", "INVALID", "invalid"),
        ]

        for i, (icon, number, label, state) in enumerate(values):
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(0, 0, 0, 0)

            icon_label = QLabel(icon)
            icon_label.setObjectName("summaryIcon_" + state)

            number_label = QLabel(number)
            number_label.setObjectName("summaryNumber")

            text = QLabel(label)
            text.setObjectName("summaryLabel")

            text_box = QVBoxLayout()
            text_box.setSpacing(0)
            text_box.addWidget(number_label)
            text_box.addWidget(text)

            item_layout.addWidget(icon_label)
            item_layout.addLayout(text_box)

            layout.addWidget(item, 1)

            if i < len(values) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.VLine)
                layout.addWidget(line)

        return frame

    def line_creation(self, line_type):
            line = QFrame()
            line.setFrameShape(line_type)
            line.setObjectName("verticalLine")
            return line


                


