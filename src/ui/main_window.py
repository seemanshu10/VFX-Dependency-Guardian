"""Main Entry Point For UI"""
from pathlib import Path

from PySide2 import QtWidgets
from PySide2.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QRadioButton, QComboBox, QSplitter, QLineEdit, QTableWidget, QTableWidgetItem)
from PySide2.QtCore import Qt, Slot
from src.constants import (APP_TITLE, WINDOW_HEIGHT, WINDOW_WIDTH, ASSET_TYPE,
                           MODE_ASSETS, MODE_SHOTS, MODE_LABELS)

STYLE_FILE = Path(__file__).parent / "styles" / "main_window.qss"

class MainWindow(QMainWindow):
    """Main Apllication window interfaces"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        #set window Size and Properties 
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.assets = [
                        ("character_A", "Character", "FAILED", 3),
                        ("character_B", "Character", "OK", 0),
                        ("prop_car", "Prop", "OUTDATED", 1),
                        ("environment_01", "Environment", "OK", 0),
                        ("vehicle_ship", "Vehicle", "FAILED", 2),
                        ("set_building", "Set", "OUTDATED", 1),
                        ("tree_grp", "Vegetation", "OK", 0),
                        ("fx_smoke", "FX", "INVALID", 1),
                    ]
        # Create Central Widget and Layout 
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.create_header()
        self.populate_table()
        self.apply_style()

    def create_header(self):
        # create menu BAr
        # menubar = self.menuBar()
        # # file Menu 
        # file_menu = menubar.addAction("File")

        layout_main = QVBoxLayout(self.central_widget)

        main_title = QLabel("Dependency Validator")
        main_title.setObjectName("pageTitle")
        subtitle = QLabel("Validate published assets and shots against the approved registry.")
        subtitle.setObjectName("pageSubtitle")

        layout_main.addWidget(main_title)
        layout_main.addWidget(subtitle)

        frame = QFrame()
        frame.setObjectName("tabFrame")
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        self.asset_btn = QPushButton(" Assets ")
        self.shots_btn = QPushButton(" Shots ")
        self.asset_btn.setObjectName("modeTab")
        self.shots_btn.setObjectName("modeTab")
        self.asset_btn.setProperty("active", True)

        self.asset_btn.clicked.connect(lambda: self.switch_mode(self.asset_btn, self.shots_btn))
        self.shots_btn.clicked.connect(lambda: self.switch_mode(self.shots_btn, self.asset_btn))

        frame_layout.addWidget(self.asset_btn)
        frame_layout.addWidget(self.shots_btn)
        frame_layout.addStretch()

        layout_main.addWidget(frame)

        validation_frame = QFrame()
        validation_frame.setObjectName("filterPanel")

        validation_layout = QHBoxLayout(validation_frame)
        validation_layout.setContentsMargins(18, 14, 18, 14)
        validation_layout.setSpacing(16)

        #scope 
        validation_scope_main_box = QVBoxLayout()
        scope_label = QLabel("Validation Scope")
        scope_label.setObjectName("fieldLabel")

        radio_box = QHBoxLayout()
        self.all_radio = QRadioButton("All Assets")
        self.selected_radio = QRadioButton("Selected Assets")
        self.single_radio = QRadioButton("Single Asset")

        validation_scope_main_box.addWidget(scope_label)
        radio_box.addWidget(self.all_radio)
        radio_box.addWidget(self.selected_radio)
        radio_box.addWidget(self.single_radio)
        validation_scope_main_box.addLayout(radio_box)

        validation_layout.addLayout(validation_scope_main_box, 0)
        validation_layout.addWidget(self.line_creation(QFrame.VLine))

        # adding Comboboxes 
        self.project_type_layout, self.project_type_combobox = self.combobox_build("Project", ["Demo_project", "New_Project"])
        validation_layout.addLayout(self.project_type_layout, 1)

        self.asset_type_layout, self.asset_type_combobox = self.combobox_build("Asset Type", ASSET_TYPE)
        # keep the label so its text can change with the mode
        self.asset_type_label = self.asset_type_layout.itemAt(0).widget()
        validation_layout.addLayout(self.asset_type_layout, 1)
        
        validation_layout.addWidget(self.line_creation(QFrame.VLine))
        run_btn = QPushButton("▶  Generate Validation Report")
        run_btn.setObjectName("runButton")
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

        main_area_splitter.setStretchFactor(0, 3)
        main_area_splitter.setStretchFactor(1, 2)

        return main_area_splitter

    def create_results_panel(self):
        frame_results = QFrame()
        frame_results.setObjectName("panel")
        frame_layout = QVBoxLayout(frame_results)
        
        frame_layout.setContentsMargins(14, 14, 14, 14)
        frame_layout.setSpacing(10)

        # validation Results 
        top_layout = QHBoxLayout()

        validate_title = QLabel("Validation Results")
        validate_title.setObjectName("panelTitle")
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
        self.details_header_labels = ["", "ASSET", "TYPE", "STATUS", "ISSUES"]
        self.details_table_widget.setHorizontalHeaderLabels(self.details_header_labels)
        self.details_table_widget.setColumnWidth(10, 42)
        self.details_table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.details_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.details_table_widget.setSortingEnabled(True)

        header = self.details_table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

        # hide Qt's sort arrow (set after setSortingEnabled, which turns it on)
        # and show the sort direction as text in the header label instead
        header.setSortIndicatorShown(False)
        header.sortIndicatorChanged.connect(self.update_sort_arrow)

        frame_layout.addLayout(top_layout)
        frame_layout.addWidget(self.details_table_widget, 1)

        # signals Call 
        self.details_table_widget.itemSelectionChanged.connect(self.update_details)

        return frame_results

    #-------------------------------------------------------------------------
    #  Details
    # ------------------------------------------------------------------------

    def create_details_panel(self):
        frame = QFrame()
        frame.setObjectName("detailsPanel")

        details_main_layout = QVBoxLayout(frame)
        details_main_layout.setContentsMargins(16, 16, 16, 16)
        details_main_layout.setSpacing(10)

        header = QtWidgets.QHBoxLayout()
        
        self.detail_icon = QtWidgets.QLabel("⬡")
        self.detail_icon.setFixedWidth(36)
        self.detail_icon.setObjectName("detailIcon")
        self.detail_name = QtWidgets.QLabel()
        self.detail_name.setObjectName("detailTitle")
        self.detail_status = QtWidgets.QLabel("●  ")
        self.detail_status.setObjectName("failedBadge")

        header.addWidget(self.detail_icon)
        header.addWidget(self.detail_name)
        header.addStretch()
        header.addWidget(self.detail_status)
        self.asset_type_text = "Character"
        # self.project_type_combobox = "Demo Project"
        self.info = QtWidgets.QLabel()
        self.info.setObjectName("detailInfo")

        details_main_layout.addLayout(header)
        details_main_layout.addWidget(self.info)
        detail_line = self.line_creation(QFrame.HLine)
        detail_line.setObjectName("detailLine")
        details_main_layout.addWidget(detail_line)

        dependency_detail_label = QLabel("Dependency Details")
        dependency_detail_label.setObjectName("subTitle")
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

    @Slot()
    def update_details(self):
        project_name = self.project_type_combobox.currentText()
        # print(project_name)
        selected_asset = self.details_table_widget.selectedItems()
        if not selected_asset:
            return

        row = self.details_table_widget.currentRow()
        asset_name = self.details_table_widget.item(row, 1).text()
        asset_type = self.details_table_widget.item(row, 2).text()
        asset_status = self.details_table_widget.item(row, 3).text()
        self.detail_name.setText(asset_name)
        self.populate_updates_details_info(asset_name,project_name, asset_type)
        self.detail_status.setText("●  " + asset_status)

        self.set_details_report_for_asset(project_name, asset_name)

    def set_details_report_for_asset(self, project_name, asset):
        if asset == "character_A":
            deps = [
                ("model", "v002", "v008", "OUTDATED"),
                ("rig", "v001", "v004", "OUTDATED"),
                ("texture", "v005", "v005", "OK"),
                ("groom", "-", "v002", "MISSING"),
            ]

            report = (
                "asset:    character_A\n"
                f"project:  {project_name}\n"
                "status:   FAILED\n\n"
                "components:\n\n"
                " - model:\n"
                "     current:  v002\n"
                "     expected: v008\n"
                "     status:   OUTDATED\n"
                "     message:  Using older version. Update required.\n\n"
                " - rig:\n"
                "     current:  v001\n"
                "     expected: v004\n"
                "     status:   OUTDATED\n"
                "     message:  Using older version. Update required."
            )
        else:
            deps = [
                ("model", "v005", "v005", "OK"),
                ("rig", "v003", "v003", "OK"),
                ("texture", "v008", "v008", "OK"),
            ]
            report = (
                f"asset:    {asset}\n"
                f"project:  {project_name}\n"
                "status:   OK\n\n"
                "All registered dependencies match the approved versions."
            ).format(asset)

        self.dependency_table_widget.setRowCount(0)

        for component, current, expected, status in deps:
            row = self.dependency_table_widget.rowCount()
            self.dependency_table_widget.insertRow(row)

            self.dependency_table_widget.setItem(row, 0, QTableWidgetItem(component))
            self.dependency_table_widget.setItem(row, 1, QTableWidgetItem(current))
            self.dependency_table_widget.setItem(row, 2, QTableWidgetItem(expected))
            
            status_item = QTableWidgetItem("* " + status)
            self.dependency_table_widget.setItem(row, 3, status_item)

        self.report.setPlainText(report)

    def combobox_build(self, label_text, values):
        box = QVBoxLayout()
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")

        combo = QComboBox()
        combo.addItems(values)
        combo.setMinimumHeight(36)

        box.addWidget(label)
        box.addWidget(combo)

        return box, combo

    def create_summary(self):
        frame = QFrame()
        frame.setObjectName("summaryFrame")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 10, 18, 10)
        validation_label = QLabel("Validation Summary")
        validation_label.setObjectName("panelTitle")
        layout.addWidget(validation_label) 
        values = [
            ("✓", "124", "OK", "ok"),
            ("●", "18", "OUTDATED", "outdated"),
            ("×", "7", "MISSING", "missing"),
            ("●", "2", "INVALID", "invalid"),
        ]

        for i, (icon, number, label, state) in enumerate(values):
            item = QWidget()
            item.setObjectName("summaryItem")
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(4)

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

            item_layout.addStretch()
            item_layout.addWidget(icon_label)
            item_layout.addLayout(text_box)
            item_layout.addStretch()

            layout.addWidget(item, 1)

            if i < len(values) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.VLine)
                line.setObjectName("summaryLine")
                layout.addWidget(line)

        return frame

    def line_creation(self, line_type):
            line = QFrame()
            line.setFrameShape(line_type)
            line.setObjectName("verticalLine")
            return line

    def populate_table(self):
        self.details_table_widget.setRowCount(0)
        
        for asset_name, asset_Type, status, issues in self.assets:

            row = self.details_table_widget.rowCount()
            self.details_table_widget.insertRow(row)
            self.details_table_widget.setRowHeight(row, 30)
            
            check_box = QTableWidgetItem()
            check_box.setCheckState(Qt.Unchecked)
            self.details_table_widget.setItem(row, 0, check_box)

            asset_name_item = QTableWidgetItem(asset_name)
            asset_type_item = QTableWidgetItem(asset_Type)
            asset_status_item = QTableWidgetItem(status)
            asset_issues_item = QTableWidgetItem(str(issues))

            self.details_table_widget.setItem(row , 1 ,asset_name_item)
            self.details_table_widget.setItem(row , 2 ,asset_type_item)
            self.details_table_widget.setItem(row , 3 ,asset_status_item)
            self.details_table_widget.setItem(row , 4 ,asset_issues_item)

    def populate_updates_details_info(self, asset_name, project_name, asset_type_text):

        self.info.setText(
                    f"Type:  {asset_type_text}\n"
                    f"Project:  {project_name}\n"
                    f"Path:  /assets/{asset_type_text}/{asset_name}"
                )

    @Slot(int, Qt.SortOrder)
    def update_sort_arrow(self, column, order):
        arrow = " ▲" if order == Qt.AscendingOrder else " ▼"
        labels = list(self.details_header_labels)
        # column can be out of range before the user has sorted anything
        if 0 <= column < len(labels) and labels[column]:
            labels[column] += arrow
        self.details_table_widget.setHorizontalHeaderLabels(labels)

    def switch_mode(self, active, inactive):
        active.setProperty("active", True)
        inactive.setProperty("active", False)

        # re-polish so the [active="true"] selector is re-evaluated
        for btn in (active, inactive):
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        mode = MODE_SHOTS if active is self.shots_btn else MODE_ASSETS
        self.set_mode_labels(mode)

    def set_mode_labels(self, mode):
        """Update all mode-dependent text. Edit MODE_LABELS in constants.py to change it."""
        labels = MODE_LABELS[mode]

        self.all_radio.setText(labels["all_radio"])
        self.selected_radio.setText(labels["selected_radio"])
        self.single_radio.setText(labels["single_radio"])
        self.asset_type_label.setText(labels["type_filter"])
        self.search_box.setPlaceholderText(labels["search"])

        # re-apply through update_sort_arrow so the ▲/▼ stays on the sorted column
        self.details_header_labels = list(labels["table_headers"])
        header = self.details_table_widget.horizontalHeader()
        self.update_sort_arrow(header.sortIndicatorSection(), header.sortIndicatorOrder())

    # ------------------------------------------------------------------------
    #  Styling
    # ------------------------------------------------------------------------

    def apply_style(self):
        """Load the window stylesheet from the external QSS file."""
        if not STYLE_FILE.exists():
            print(f"Stylesheet not found: {STYLE_FILE}")
            return
        self.setStyleSheet(STYLE_FILE.read_text(encoding="utf-8"))
