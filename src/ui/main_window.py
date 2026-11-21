"""Main Entry Point For UI"""
from datetime import datetime
from pathlib import Path

from PySide6 import QtWidgets
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QRadioButton, QComboBox, QSplitter, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, Slot, QSize

from src.constants import (APP_TITLE, WINDOW_HEIGHT, WINDOW_WIDTH,
                           MODE_ASSETS, MODE_SHOTS, MODE_LABELS,
                           STATUS_TOOLTIPS, SUMMARY_TOOLTIPS)
import qtawesome
from src.data_loader import load_json, json_file_find_path, get_all_folder_list, get_project_folder, get_shot_files
from collections import Counter

from src.validator import RESULT_OK, RESULT_OUTDATED, RESULT_MISSING, RESULT_INVALID
from src.report import (asset_summaries, shot_summaries, build_asset_report,
                        build_shot_report, build_export_text)

STYLE_FILE = Path(__file__).parent / "styles" / "main_window.qss"

class StatusItem(QTableWidgetItem):
    """Text-less item under a status badge. Holds the status in UserRole and sorts by it."""
    def __lt__(self, other):
        return (self.data(Qt.ItemDataRole.UserRole) or "") < (other.data(Qt.ItemDataRole.UserRole) or "")

class MainWindow(QMainWindow):
    """Main Apllication window interfaces"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        #set window Size and Properties 
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # set before create_header: the filter combo and table read it
        self.current_mode = MODE_ASSETS

        # Create Central Widget and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.create_header()
        # style first: the status badges measure their size from the QSS when the table fills
        self.apply_style()
        self.populate_table()
        self.set_mode_tooltips(self.current_mode)

    def create_header(self):
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
        self.asset_btn.setToolTip("Check published assets (characters, props, sets...).\n"
                                  "Shows whether each asset is built on the newest versions of its parts.")
        self.shots_btn.setToolTip("Check shots.\n"
                                  "Shows whether each shot uses the newest published version of every asset in it.")

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
        scope_label.setToolTip("Choose which items the report should cover.")

        radio_box = QHBoxLayout()
        self.all_radio = QRadioButton("All Assets")
        self.selected_radio = QRadioButton("Selected Assets")

        self.all_radio.setChecked(True)
        validation_scope_main_box.addWidget(scope_label)
        radio_box.addWidget(self.all_radio)
        radio_box.addWidget(self.selected_radio)
        validation_scope_main_box.addLayout(radio_box)

        validation_layout.addLayout(validation_scope_main_box, 0)
        validation_layout.addWidget(self.line_creation(QFrame.Shape.VLine))

        # adding Comboboxes 
        self.project_type_layout, self.project_name_combobox, _ = self.combobox_build("Project", get_all_folder_list())
        self.project_name_combobox.setToolTip("Choose the project to check.\n"
                                              "The table below reloads with that project's items.")
        validation_layout.addLayout(self.project_type_layout, 1)

        # keep the label so its text can change with the mode
        self.asset_type_layout, self.asset_type_combobox, self.asset_type_label = self.combobox_build("Asset Type", self.get_asset_types())
        validation_layout.addLayout(self.asset_type_layout, 1)
        
        validation_layout.addWidget(self.line_creation(QFrame.Shape.VLine))
        self.run_btn = QPushButton("Generate Validation Report")
        self.run_btn.setIcon(qtawesome.icon('mdi.export', color = 'black'))
        self.run_btn.setObjectName("runButton")
        self.run_btn.setToolTip("Create a report listing everything that is out of date or broken\n"
                           "for the items chosen in Validation Scope.")
        validation_layout.addWidget(self.run_btn)
        self.run_btn.setMinimumWidth(174)
        self.run_btn.setMinimumHeight(44)
        layout_main.addWidget(validation_frame)

        layout_main.addWidget(self.create_summary())
        layout_main.addWidget(self.create_main_area(), 1)

        layout_main.addStretch()

        # connected last: the handler touches the table and details panel built above
        self.project_name_combobox.currentTextChanged.connect(self.on_project_changed)
        self.asset_type_combobox.currentTextChanged.connect(self.on_asset_type_changed)
        self.run_btn.clicked.connect(self.detail_report_for_export)

    # ------------------------------------------------------------------------
    #  Results
    # ------------------------------------------------------------------------

    def create_main_area(self):
        main_area_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_area_splitter.addWidget(self.create_validation_results_panel())
        main_area_splitter.addWidget(self.create_details_panel())

        main_area_splitter.setStretchFactor(0, 3)
        main_area_splitter.setStretchFactor(1, 2)

        return main_area_splitter

    def create_validation_results_panel(self):
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
        self.details_table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.details_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.details_table_widget.setSortingEnabled(True)

        header = self.details_table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        # Sort indicator 
        header.setSortIndicatorShown(False)
        # header.sortIndicatorChanged.connect(self.update_sort_arrow)

        frame_layout.addLayout(top_layout)
        frame_layout.addWidget(self.details_table_widget, 1)

        # search bar call 
        self.search_box.textChanged.connect(self.apply_search_filter)
        
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
        self.detail_status.setObjectName("statusBadge")
        self.detail_name.setToolTip("The item you clicked in the table.")

        header.addWidget(self.detail_icon)
        header.addWidget(self.detail_name)
        header.addStretch()
        header.addWidget(self.detail_status)
        self.info = QtWidgets.QLabel()
        self.info.setObjectName("detailInfo")

        details_main_layout.addLayout(header)
        details_main_layout.addWidget(self.info)
        detail_line = self.line_creation(QFrame.Shape.HLine)
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
        self.dependency_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        self.dependency_table_widget.horizontalHeader().setSectionResizeMode(
                0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            )
        self.dependency_table_widget.horizontalHeader().setSectionResizeMode(
                1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            )
        self.dependency_table_widget.horizontalHeader().setSectionResizeMode(
                2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            )
        self.dependency_table_widget.horizontalHeader().setSectionResizeMode(
                3, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            )
        self.dependency_table_widget.verticalHeader().setDefaultSectionSize(44)

        details_main_layout.addWidget(self.dependency_table_widget)
        report_title = QtWidgets.QLabel("Detailed Report")
        report_title.setObjectName("subTitle")
        details_main_layout.addWidget(report_title)

        self.report = QtWidgets.QPlainTextEdit()
        self.report.setReadOnly(True)
        self.report.setObjectName("reportBox")
        self.report.setToolTip("A plain-text summary of the problems found for this item.\n"
                               "You can select and copy it.")
        details_main_layout.addWidget(self.report, 1)
        return frame

    @Slot()
    def update_details(self) -> None:
        project_name = self.project_name_combobox.currentText()
        selected_asset = self.details_table_widget.selectedItems()
        if not selected_asset:
            return

        row = self.details_table_widget.currentRow()
        name_item = self.details_table_widget.item(row, MODE_LABELS[self.current_mode]["name_col"])
        if name_item is None:
            return
        # asset id or shot file, stored by populate_table
        row_key = name_item.data(Qt.ItemDataRole.UserRole)

        report = self.build_report(project_name, row_key)
        self.detail_name.setText(name_item.text())
        self.set_detail_status(report.status)
        self.show_report(report)

    def build_report(self, project_name, row_key):
        """ItemReport for one row of the results table, in the current mode."""
        if self.current_mode == MODE_SHOTS:
            return build_shot_report(project_name, row_key)
        return build_asset_report(project_name, row_key)

    def show_report(self, report):
        """Fill the details panel (info, dependency table, text report) from an ItemReport."""
        self.info.setText("\n".join(f"{label}:  {value}" for label, value in report.info.items()))

        self.dependency_table_widget.setRowCount(0)
        for component, current, expected, status in report.rows:
            row = self.dependency_table_widget.rowCount()
            self.dependency_table_widget.insertRow(row)

            self.dependency_table_widget.setItem(row, 0, QTableWidgetItem(component))
            self.dependency_table_widget.setItem(row, 1, QTableWidgetItem(current))
            self.dependency_table_widget.setItem(row, 2, QTableWidgetItem(expected))
            self.set_status_badge(self.dependency_table_widget, row, 3, status)

        self.report.setPlainText(report.text)

    def combobox_build(self, label_text, values):
        box = QVBoxLayout()
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")

        combo = QComboBox()
        combo.addItems(values)
        combo.setMinimumHeight(36)

        box.addWidget(label)
        box.addWidget(combo)

        return box, combo, label

    def set_status_badge(self, table, row, column, status):
        # a table item can't draw a box, so the cell holds a QLabel styled like detail_status
        badge = QLabel("●  " + status)
        badge.setObjectName("depStatusBadge")
        badge.setProperty("status", status)  # picks the colour variant in the QSS
        badge.setToolTip(STATUS_TOOLTIPS.get(status, ""))

        # wrapper keeps the badge sized to its text instead of stretching over the cell
        cell = QWidget()
        cell.setObjectName("statusCell")
        layout = QHBoxLayout(cell)
        # no margins: the item padding below already lines the badge up with the other columns' text
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addStretch()

        table.setCellWidget(row, column, cell)

        # ResizeToContents only measures items, not cell widgets: an empty item carrying
        
        cell.ensurePolished()
        size_item = StatusItem()
        size_item.setData(Qt.ItemDataRole.UserRole, status)
        size_item.setSizeHint(cell.sizeHint() + QSize(2 * 8, 0))
        table.setItem(row, column, size_item)

    def set_detail_status(self, status):
        self.detail_status.setText("●  " + status)
        self.detail_status.setProperty("status", status)
        self.detail_status.setToolTip(STATUS_TOOLTIPS.get(status, ""))
        # re-polish so the [status="..."] selector is re-evaluated
        self.detail_status.style().unpolish(self.detail_status)
        self.detail_status.style().polish(self.detail_status)

    def create_summary(self):
        frame = QFrame()
        frame.setObjectName("summaryFrame")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 10, 18, 10)
        validation_label = QLabel("Validation Summary")
        validation_label.setObjectName("panelTitle")
        validation_label.setToolTip("Totals for the rows shown in the table below.\n"
                                    "Each part checked counts once, so OUTDATED + MISSING + INVALID\n"
                                    "adds up to the ISSUES column.")
        layout.addWidget(validation_label) 
        # (icon, colour, result counted, style/tooltip key); numbers are filled by update_summary
        values = [
            ("mdi.check-circle",  "#23d47b", RESULT_OK,       "ok"),
            ("mdi.clock-alert",   "#ff4f56", RESULT_OUTDATED, "outdated"),
            ("mdi.close-circle",  "#ffad22", RESULT_MISSING,  "missing"),
            ("mdi.alert-octagon", "#7c9fc4", RESULT_INVALID,  "invalid"),
        ]
        # result -> its number label, so update_summary can change the count
        self.summary_numbers = {}

        for i, (icon_name, color, label, state) in enumerate(values):
            item = QWidget()
            item.setObjectName("summaryItem")
            item.setToolTip(SUMMARY_TOOLTIPS[state])
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(4)

            icon_label = QLabel()
            icon_label.setObjectName("summaryIcon_" + state)
            icon_label.setPixmap(qtawesome.icon(icon_name, color=color).pixmap(24, 24))

            number_label = QLabel("0")
            number_label.setObjectName("summaryNumber")
            self.summary_numbers[label] = number_label

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
                line.setFrameShape(QFrame.Shape.VLine)
                line.setObjectName("summaryLine")
                layout.addWidget(line)

        return frame

    def update_summary(self, counts):
        """Show how many checks ended in each result. counts: {result: number}."""
        for result, number_label in self.summary_numbers.items():
            number_label.setText(str(counts.get(result, 0)))

    def line_creation(self, line_type):
            line = QFrame()
            line.setFrameShape(line_type)
            line.setObjectName("verticalLine")
            return line

    @Slot(str)
    def on_project_changed(self, project_name):

        self.refresh_type_filter()
        self.populate_table()
        self.clear_details()

    @Slot(str)
    def on_asset_type_changed(self, asset_type):
        self.populate_table()
        self.clear_details()

    def refresh_type_filter(self):
        """Fill the filter combo with asset types or sequences, depending on the mode."""
        if self.current_mode == MODE_SHOTS:
            values = self.get_sequences()
        else:
            values = self.get_asset_types()

        self.asset_type_combobox.blockSignals(True)
        self.asset_type_combobox.clear()
        self.asset_type_combobox.addItems(values)
        self.asset_type_combobox.blockSignals(False)

    def clear_details(self):
        # the old selection belonged to the previous project
        self.detail_name.setText("")
        self.set_detail_status("")
        self.info.setText("")
        self.dependency_table_widget.setRowCount(0)
        self.report.clear()

    def populate_table(self):
        self.details_table_widget.setRowCount(0)
        # with sorting on, Qt re-sorts after every setItem and the row index goes stale
        self.details_table_widget.setSortingEnabled(False)
        project_name = self.project_name_combobox.currentText()
        selected_type = self.asset_type_combobox.currentText()

        # one ItemSummary per row: group is the asset type or the sequence
        if self.current_mode == MODE_SHOTS:
            summaries = shot_summaries(project_name)
        else:
            summaries = asset_summaries(project_name)

        # summary totals cover only the rows that pass the filter, i.e. what the table shows
        summary_counts = Counter()

        for summary in summaries:
            if selected_type != "All" and summary.group != selected_type:
                continue
            summary_counts.update(summary.counts)

            row = self.details_table_widget.rowCount()
            self.details_table_widget.insertRow(row)
            # status badge (21) + the QSS item padding (8 top + 8 bottom) + grid line, with a little spare
            self.details_table_widget.setRowHeight(row, 40)
            
            check_box = QTableWidgetItem()
            check_box.setCheckState(Qt.CheckState.Unchecked)
            self.details_table_widget.setItem(row, 0, check_box)

            asset_name_item = QTableWidgetItem(summary.name)
            # remember the shot file / asset id, so the details panel can load it
            asset_name_item.setData(Qt.ItemDataRole.UserRole, summary.key)
            asset_type_item = QTableWidgetItem(summary.group)
            # int, not str, so the column sorts 2 < 10
            asset_issues_item = QTableWidgetItem()
            asset_issues_item.setData(Qt.ItemDataRole.DisplayRole, summary.issues)
            asset_issues_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            cols = MODE_LABELS[self.current_mode]
            self.details_table_widget.setItem(row , cols["name_col"] ,asset_name_item)
            self.details_table_widget.setItem(row , cols["type_col"] ,asset_type_item)
            self.set_status_badge(self.details_table_widget, row, 3, summary.status)
            self.details_table_widget.setItem(row , 4 ,asset_issues_item)

        self.details_table_widget.setSortingEnabled(True)
        self.update_summary(summary_counts)
        # keep the current search applied after the table is rebuilt
        self.apply_search_filter(self.search_box.text())

    @Slot()
    def apply_search_filter(self, text):
        """Hide rows whose name/type text doesn't contain the search text (case-insensitive)."""
        search_text = text.strip().lower()
        asset_table_rows = self.details_table_widget
        for row in range(asset_table_rows.rowCount()):
            if not search_text:
                asset_table_rows.setRowHidden(row, False)
                continue
            match = False
            for col in range(asset_table_rows.columnCount()):
                item = asset_table_rows.item(row, col)
                if item is not None and search_text in str(item.text()).lower():
                    match = True
                    break
            asset_table_rows.setRowHidden(row, not match)

    @Slot(int, Qt.SortOrder)
    def update_sort_arrow(self, column, order):
        arrow = " ▲" if order == Qt.SortOrder.AscendingOrder else " ▼"
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
        self.current_mode = mode
        self.set_mode_labels(mode)

        # signals are blocked while the combo refills, so refresh the table here
        self.refresh_type_filter()
        self.populate_table()
        self.clear_details()

    def set_mode_labels(self, mode):
        """Update all mode-dependent text. Edit MODE_LABELS in constants.py to change it."""
        labels = MODE_LABELS[mode]

        self.all_radio.setText(labels["all_radio"])
        self.selected_radio.setText(labels["selected_radio"])
        self.asset_type_label.setText(labels["type_filter"])
        self.search_box.setPlaceholderText(labels["search"])
        self.set_mode_tooltips(mode)

        self.details_header_labels = list(labels["table_headers"])
        header = self.details_table_widget.horizontalHeader()
        self.update_sort_arrow(header.sortIndicatorSection(), header.sortIndicatorOrder())

    def set_mode_tooltips(self, mode):
        """Hover text for widgets whose meaning changes with the mode. Text is in MODE_LABELS."""
        tips = MODE_LABELS[mode]["tooltips"]

        self.all_radio.setToolTip(tips["all_radio"])
        self.selected_radio.setToolTip(tips["selected_radio"])
        self.asset_type_combobox.setToolTip(tips["type_filter"])
        self.search_box.setToolTip(tips["search"])
        self.details_table_widget.setToolTip(tips["table"])
        self.dependency_table_widget.setToolTip(tips["dependency_table"])

        # header items survive setHorizontalHeaderLabels, so setting them here is enough
        for table, key in ((self.details_table_widget, "headers"),
                           (self.dependency_table_widget, "dependency_headers")):
            for column, tip in enumerate(tips[key]):
                header_item = table.horizontalHeaderItem(column)
                if header_item is not None:
                    header_item.setToolTip(tip)

    def get_asset_types(self):
        project_name = self.project_name_combobox.currentText()
        registry_data = load_json(json_file_find_path("registry", get_project_folder(project_name)))
        all_asset_type = []
        for asset_id, asset_type in registry_data["assets"].items():
            asset_type = registry_data["assets"][asset_id]["type"]

            all_asset_type.append(asset_type)

        return ["All"] + sorted(set(all_asset_type))

    def get_sequences(self):
        project_name = self.project_name_combobox.currentText()
        all_sequences = []
        # read the "sequence" field, not the filename: naming conventions differ per studio
        for shot_file in get_shot_files(project_name):
            shot_data = load_json(shot_file)
            all_sequences.append(shot_data["sequence"])

        # "All" added after sorting so it is always first
        return ["All"] + sorted(set(all_sequences))

    # ------------------------------------------------------------------------
    #  detail report 
    # ------------------------------------------------------------------------
    @Slot()
    def detail_report_for_export(self):
        """Export the detailed report for the rows chosen in Validation Scope to a .txt file."""
        project_name = self.project_name_combobox.currentText()
        table = self.details_table_widget
        cols = MODE_LABELS[self.current_mode]
        visible_rows = [row for row in range(table.rowCount()) if not table.isRowHidden(row)]

        if self.all_radio.isChecked():
            rows = visible_rows
        else:
            # ticked checkboxes first; fall back to the highlighted rows
            rows = [row for row in visible_rows
                    if (item := table.item(row, 0)) is not None
                    and item.checkState() == Qt.CheckState.Checked]
            if not rows:
                rows = sorted({index.row() for index in table.selectionModel().selectedRows()})

        if not rows:
            QMessageBox.information(self, "Validation Report",
                                    "Nothing to export. Tick or select at least one row.")
            return

        reports = []
        for row in rows:
            name_item = table.item(row, cols["name_col"])
            if name_item is None:
                continue
            reports.append(self.build_report(project_name, name_item.data(Qt.ItemDataRole.UserRole)))

        mode_name = "shots" if self.current_mode == MODE_SHOTS else "assets"
        scope = "all" if self.all_radio.isChecked() else "selected"
        text = build_export_text(project_name, mode_name, scope, reports)

        default_name = f"{project_name}_{mode_name}_validation_{datetime.now():%Y%m%d_%H%M%S}.txt"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Validation Report",
                                                   str(Path.home() / default_name),
                                                   "Text files (*.txt)")
        if not file_path:
            return

        try:
            Path(file_path).write_text(text, encoding="utf-8")
        except OSError as error:
            QMessageBox.warning(self, "Validation Report", f"Could not save the report:\n{error}")
            return

        QMessageBox.information(self, "Validation Report",
                                f"Report for {len(reports)} items saved to:\n{file_path}")

    # ------------------------------------------------------------------------
    #  Styling
    # ------------------------------------------------------------------------

    def apply_style(self):
        """Load the window stylesheet from the external QSS file."""
        if not STYLE_FILE.exists():
            print(f"Stylesheet not found: {STYLE_FILE}")
            return
        self.setStyleSheet(STYLE_FILE.read_text(encoding="utf-8"))
