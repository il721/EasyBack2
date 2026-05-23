import sys
import shutil
import os
import threading
import json
from datetime import datetime
from styles import GLOBAL_STYLE, START_BUTTON_STYLE, STATUS_LABEL_STYLE
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFileDialog, QMessageBox, QProgressBar, QGroupBox, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QObject


class BackupWorkerSignals(QObject):
    progress = pyqtSignal(int)
    status = pyqtSignal(str, str)  # message, color
    finished = pyqtSignal(bool, str)  # success, message


class BackupApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Backup Tool (Qt)")
        self.resize(900, 650)

        self.sources = []  # List of dictionaries: {"source": path, "dest": path}

        self.setStyleSheet(GLOBAL_STYLE)
        self.setup_ui()
        self.signals = BackupWorkerSignals()
        self.signals.progress.connect(self.update_progress)
        self.signals.status.connect(self.update_status)
        self.signals.finished.connect(self.backup_finished)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Section for selecting sources and their destinations
        group_top = QGroupBox("Backup List (Source -> Destination)")
        layout_top = QVBoxLayout(group_top)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Source", "Destination"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout_top.addWidget(self.table)

        main_layout.addWidget(group_top)

        # Buttons for list management
        btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton("Add File")
        self.btn_add_file.clicked.connect(self.add_file)
        btn_layout.addWidget(self.btn_add_file)

        self.btn_add_folder = QPushButton("Add Folder")
        self.btn_add_folder.clicked.connect(self.add_folder)
        btn_layout.addWidget(self.btn_add_folder)

        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.btn_delete)

        btn_layout.addStretch()

        self.btn_save = QPushButton("Save List")
        self.btn_save.clicked.connect(self.save_list)
        btn_layout.addWidget(self.btn_save)

        self.btn_load = QPushButton("Load List")
        self.btn_load.clicked.connect(self.load_list)
        btn_layout.addWidget(self.btn_load)

        main_layout.addLayout(btn_layout)

        # Section for editing the destination path for selected items
        group_edit = QGroupBox("Set Destination for Selected")
        layout_edit = QHBoxLayout(group_edit)

        self.edit_dest_input = QLineEdit()
        self.edit_dest_input.setPlaceholderText("Enter or browse for destination...")
        layout_edit.addWidget(self.edit_dest_input)

        self.btn_browse_edit = QPushButton("Browse")
        self.btn_browse_edit.clicked.connect(self.browse_edit_dest)
        layout_edit.addWidget(self.btn_browse_edit)

        self.btn_apply = QPushButton("Apply to Selected")
        self.btn_apply.clicked.connect(self.apply_dest_to_selected)
        layout_edit.addWidget(self.btn_apply)

        main_layout.addWidget(group_edit)

        # Section for selecting the default destination
        group_mid = QGroupBox("Default Destination (for new items)")
        layout_mid = QHBoxLayout(group_mid)

        self.default_dest_input = QLineEdit()
        self.default_dest_input.setPlaceholderText("New items will use this path by default...")
        layout_mid.addWidget(self.default_dest_input)

        self.btn_browse_default = QPushButton("Browse")
        self.btn_browse_default.clicked.connect(self.browse_default_dest)
        layout_mid.addWidget(self.btn_browse_default)

        main_layout.addWidget(group_mid)

        # Start button and status
        self.btn_start = QPushButton("START BACKUP")
        self.btn_start.setStyleSheet(START_BUTTON_STYLE)
        self.btn_start.clicked.connect(self.start_backup_thread)
        main_layout.addWidget(self.btn_start)

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(STATUS_LABEL_STYLE)
        main_layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        main_layout.addWidget(self.progress)

    def add_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        for f in files:
            dest = self.default_dest_input.text()
            item = {"source": f, "dest": dest}
            self.sources.append(item)
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(f))
            self.table.setItem(row, 1, QTableWidgetItem(dest))

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            dest = self.default_dest_input.text()
            item = {"source": folder, "dest": dest}
            self.sources.append(item)
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(folder))
            self.table.setItem(row, 1, QTableWidgetItem(dest))

    def remove_selected(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return

        # Collect all unique row indices
        rows_to_delete = set()
        for r in selected_ranges:
            for row in range(r.topRow(), r.bottomRow() + 1):
                rows_to_delete.add(row)

        sorted_rows = sorted(list(rows_to_delete), reverse=True)
        for row in sorted_rows:
            self.sources.pop(row)
            self.table.removeRow(row)

    def browse_default_dest(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Default Backup Folder")
        if folder:
            self.default_dest_input.setText(folder)

    def browse_edit_dest(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.edit_dest_input.setText(folder)

    def apply_dest_to_selected(self):
        selected_ranges = self.table.selectedRanges()
        new_dest = self.edit_dest_input.text()
        if not selected_ranges:
            QMessageBox.warning(self, "Attention", "Select items in the list!")
            return
        if not new_dest:
            QMessageBox.warning(self, "Attention", "Enter or select a destination path!")
            return

        rows_to_update = set()
        for r in selected_ranges:
            for row in range(r.topRow(), r.bottomRow() + 1):
                rows_to_update.add(row)

        for row in rows_to_update:
            self.sources[row]["dest"] = new_dest
            self.table.setItem(row, 1, QTableWidgetItem(new_dest))

    def save_list(self):
        if not self.sources:
            QMessageBox.warning(self, "Attention", "The list is empty!")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save List As", "",
                                                   "JSON files (*.json);;All files (*.*)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.sources, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Success", "List saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save list: {e}")

    def load_list(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load List", "",
                                                   "JSON files (*.json);;All files (*.*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_sources = json.load(f)

                self.sources = []
                self.table.setRowCount(0)

                missing_paths = []
                for item in loaded_sources:
                    source = item.get("source")
                    dest = item.get("dest", "")
                    if os.path.exists(source):
                        self.sources.append({"source": source, "dest": dest})
                        row = self.table.rowCount()
                        self.table.insertRow(row)
                        self.table.setItem(row, 0, QTableWidgetItem(source))
                        self.table.setItem(row, 1, QTableWidgetItem(dest))
                    else:
                        missing_paths.append(source)

                if missing_paths:
                    QMessageBox.warning(self, "Attention",
                                        f"Some source paths were not found and were skipped:\n" + "\n".join(
                                            missing_paths[:5]))
                else:
                    QMessageBox.information(self, "Success", "List loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load list: {e}")

    def update_progress(self, value):
        self.progress.setValue(value)

    def update_status(self, text, color):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def backup_finished(self, success, message):
        self.btn_start.setEnabled(True)
        self.progress.setValue(0 if not success else 100)
        if success:
            QMessageBox.information(self, "Done", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def start_backup_thread(self):
        if not self.sources:
            QMessageBox.warning(self, "Attention", "Add at least one file or folder!")
            return

        for item in self.sources:
            if not item["dest"]:
                QMessageBox.warning(self, "Attention",
                                    f"Specify destination path for: {item['source']}")
                return

        self.btn_start.setEnabled(False)
        self.progress.setValue(0)
        threading.Thread(target=self.perform_backup, daemon=True).start()

    def perform_backup(self):
        try:
            total = len(self.sources)

            for i, item in enumerate(self.sources):
                try:
                    path = item["source"]
                    dest = item["dest"]
                    name = os.path.basename(path)

                    self.signals.status.emit(f"Copying: {name}", "#2B79C2")
                    self.signals.progress.emit(int((i / total) * 100))

                    os.makedirs(dest, exist_ok=True)
                    target_path = os.path.join(dest, name)

                    if os.path.isdir(path):
                        shutil.copytree(path, target_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(path, target_path)
                except Exception as item_error:
                    print(f"Failed to copy {path}: {item_error}")
                    continue

            self.signals.progress.emit(100)
            self.signals.status.emit("Backup completed successfully!", "#4CAF50")
            self.signals.finished.emit(True,
                                       "All files have been successfully copied to the specified paths.")

        except Exception as e:
            self.signals.status.emit("Error!", "#F44336")
            self.signals.finished.emit(False, f"A failure occurred: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackupApp()
    window.show()
    sys.exit(app.exec())
