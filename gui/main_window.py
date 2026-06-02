import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressDialog,
    QMessageBox, QStatusBar, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from gui.language_dialog import LanguageDialog, DEFAULT_LANGUAGE
from gui.results_panel import ResultsPanel
from gui.worker_thread import AnalysisWorker
from core.analyzer import scan_folder, scan_folder_with_zips


_STYLE = """
QMainWindow { background: #f5f5f5; }
QWidget#toolbar {
    background: #1565c0;
    border-bottom: 2px solid #0d47a1;
}
QPushButton#toolbar_btn {
    background: rgba(255,255,255,0.15);
    color: white;
    font-size: 13px;
    font-weight: bold;
    border: 2px solid rgba(255,255,255,0.4);
    border-radius: 6px;
    padding: 8px 18px;
    min-width: 120px;
}
QPushButton#toolbar_btn:hover {
    background: rgba(255,255,255,0.28);
    border-color: white;
}
QPushButton#toolbar_btn:pressed {
    background: rgba(0,0,0,0.15);
}
QPushButton#compare_btn {
    background: #43a047;
    color: white;
    font-size: 14px;
    font-weight: bold;
    border: none;
    border-radius: 6px;
    padding: 8px 26px;
    min-width: 130px;
}
QPushButton#compare_btn:hover { background: #388e3c; }
QPushButton#compare_btn:pressed { background: #2e7d32; }
QPushButton#compare_btn:disabled { background: #888; }
QLabel#status_lbl { color: rgba(255,255,255,0.85); font-size: 11px; }
QLabel#title_lbl {
    color: white;
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 1px;
}
QStatusBar { background: #e8eaf6; color: #333; font-size: 11px; }
"""


class MainWindow(QMainWindow):
#constructor pou trehei otan arhizei to app
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SoftPlag — Software Plagiarism Detector")
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(_STYLE)

        self._selected_folder   = ""
        self._selected_language = DEFAULT_LANGUAGE
        self._worker            = None
        self._progress_dlg      = None

        self._build_ui()
#dymiourgia tou UI me vasi ta widgets kai ta layouts 
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self._build_toolbar())

        self._results_panel = ResultsPanel()
        self._results_panel.hide()
        main_layout.addWidget(self._results_panel, 1)

        self._welcome = self._build_welcome()
        main_layout.addWidget(self._welcome, 1)

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("Ready  —  Select a folder and language, then click Compare.")
#dymiourgia tou toolbar me ta buttons kai to status label
    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("toolbar")
        bar.setFixedHeight(66)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        title = QLabel("⚡ SoftPlag")
        title.setObjectName("title_lbl")
        layout.addWidget(title)

        layout.addSpacing(24)

        self._folder_btn = QPushButton("📁  Select Folder")
        self._folder_btn.setObjectName("toolbar_btn")
        self._folder_btn.setToolTip("Choose a folder containing source files to compare")
        self._folder_btn.clicked.connect(self.on_select_folder)
        layout.addWidget(self._folder_btn)

        self._lang_btn = QPushButton(f"🔤  Language: {self._selected_language}")
        self._lang_btn.setObjectName("toolbar_btn")
        self._lang_btn.setToolTip("Choose programming language for comparison")
        self._lang_btn.clicked.connect(self.on_select_language)
        layout.addWidget(self._lang_btn)

        self._compare_btn = QPushButton("▶  Compare")
        self._compare_btn.setObjectName("compare_btn")
        self._compare_btn.setToolTip("Run plagiarism detection on selected folder")
        self._compare_btn.clicked.connect(self.on_compare)
        layout.addWidget(self._compare_btn)

        layout.addStretch()

        self._status_lbl = QLabel("No folder selected")
        self._status_lbl.setObjectName("status_lbl")
        layout.addWidget(self._status_lbl)

        return bar
#dymiourgia tou welcome screen me to icon, title, description kai steps
    def _build_welcome(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: white;")
        vl = QVBoxLayout(w)
        vl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel("🔍")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 72px;")
        vl.addWidget(icon_lbl)

        h1 = QLabel("Software Plagiarism Detector")
        h1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h1.setStyleSheet("font-size: 26px; font-weight: bold; color: #1565c0; margin-top: 12px;")
        vl.addWidget(h1)

        sub = QLabel(
            "Detects variable renaming · function reordering · comment injection · partial copying\n"
            "Supports: C · C++ · C# · Java · Python · JavaScript"
        )
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("font-size: 13px; color: #555; margin-top: 8px; line-height: 1.6;")
        vl.addWidget(sub)

        steps = QLabel(
            "\n1.  Click  📁 Select Folder  — choose a directory containing source files\n"
            "2.  Click  🔤 Language  — pick the programming language to compare\n"
            "3.  Click  ▶ Compare  — run the analysis and view results"
        )
        steps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        steps.setStyleSheet(
            "font-size: 12px; color: #333; margin-top: 24px; "
            "background: #e8f5e9; border-radius: 8px; padding: 18px 30px;"
        )
        vl.addWidget(steps)

        return w
#handler pou trehei otan o xristis patisei to "Select Folder" button
    def on_select_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Source Folder", self._selected_folder or "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
        if not folder:
            return
        self._selected_folder = folder
        self._refresh_folder_status()
#method pou kanei update to status label kai to folder button
    def _refresh_folder_status(self):
        if not self._selected_folder:
            self._status_lbl.setText("No folder selected")
            return
        n = scan_folder_with_zips(self._selected_folder, self._selected_language)
        short_path = self._selected_folder
        if len(short_path) > 50:
            short_path = "…" + short_path[-47:]
        self._folder_btn.setText(f"📁  {os.path.basename(self._selected_folder)}")
        self._status_lbl.setText(f"{short_path}  [{n} {self._selected_language} file(s)]")
        self._status_bar.showMessage(
            f"Folder: {self._selected_folder}  —  Found {n} {self._selected_language} file(s) (including zip contents)"
        )
#kaleitai otan o xristis patisei to "Language" button, anoigei to dialog gia na epileksei glwssa kai kanei update to button kai to status
    def on_select_language(self):
        dlg = LanguageDialog(self._selected_language, self)
        if dlg.exec() == QMessageBox.DialogCode.Accepted:
            self._selected_language = dlg.get_selected_language()
            self._lang_btn.setText(f"🔤  Language: {self._selected_language}")
            self._refresh_folder_status()
#kaleitai otan o xristis patisei to "Compare" button
    def on_compare(self):
        if not self._selected_folder:
            QMessageBox.warning(self, "No Folder", "Please select a folder first.")
            return

        files = scan_folder_with_zips(self._selected_folder, self._selected_language)
        if files < 2:
            QMessageBox.warning(
                self, "Too Few Files",
                f"Found only {files} {self._selected_language} file(s) in the selected folder.\n"
                "At least 2 files are required for comparison.",
            )
            return

        self._compare_btn.setEnabled(False)
        self._progress_dlg = QProgressDialog(
            "Starting analysis…", "Cancel", 0, 100, self
        )
        self._progress_dlg.setWindowTitle("Comparing Files…")
        self._progress_dlg.setWindowModality(Qt.WindowModality.WindowModal)
        self._progress_dlg.setMinimumDuration(0)
        self._progress_dlg.setValue(0)
        self._progress_dlg.show()

        self._worker = AnalysisWorker(self._selected_folder, self._selected_language, self)
        self._worker.progress.connect(self._on_progress)
        self._worker.completed.connect(self._on_analysis_complete)
        self._worker.error.connect(self._on_analysis_error)
        self._worker.start()
#kaleitai automata otan kapoio backroun thread steillei shm progress, otan ginetai tokenization, pairwise comparison, kai alla steps
    def _on_progress(self, pct: int, msg: str):
        if self._progress_dlg:
            self._progress_dlg.setValue(pct)
            self._progress_dlg.setLabelText(msg)
            if self._progress_dlg.wasCanceled():
                self._worker.terminate()
                self._progress_dlg = None
                self._compare_btn.setEnabled(True)
                self._status_bar.showMessage("Analysis cancelled.")
#kaleitai otan to background thread teleiwsei me epitixia, krataei to apotelesma kai kanei update to UI gia na deixei ta apotelesmata
    def _on_analysis_complete(self, result):
        if self._progress_dlg:
            self._progress_dlg.close()
            self._progress_dlg = None
        self._compare_btn.setEnabled(True)
        self._welcome.hide()
        self._results_panel.show()
        self._results_panel.display(result)
        n_pairs = len(result.pair_results)
        high = sum(1 for p in result.pair_results if p.combined >= 0.70)
        self._status_bar.showMessage(
            f"Analysis complete  —  {len(result.files)} files, {n_pairs} pairs compared, "
            f"{high} high-risk pair(s) found."
        )
#kaleitai otan to background thread teleiwsei me error, krataei to minima lathous kai kanei update sto UI 
    def _on_analysis_error(self, message: str):
        if self._progress_dlg:
            self._progress_dlg.close()
            self._progress_dlg = None
        self._compare_btn.setEnabled(True)
        QMessageBox.critical(self, "Analysis Error", f"An error occurred:\n\n{message}")
        self._status_bar.showMessage("Analysis failed.")
