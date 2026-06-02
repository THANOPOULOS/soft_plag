from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel,
)
from PySide6.QtCore import Qt

SUPPORTED_LANGUAGES = ["C", "C++", "C#", "Java", "Python", "JavaScript"]
DEFAULT_LANGUAGE = "C" #xrisimopoihtai sto main_window


class LanguageDialog(QDialog):
#to connstructor pou kalite otan pataei o xristis to language button
    def __init__(self, current_language: str = DEFAULT_LANGUAGE, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Programming Language")
        self.setMinimumWidth(320)
        self.setModal(True)
        self._selected = current_language
        self._build_ui(current_language)
#dymiourgia visual layout
    def _build_ui(self, current: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)
#dymiourgia label kai styling tou
        lbl = QLabel("Choose the language to compare:")
        lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(lbl)
#dymiourgia list widget me ta languages kai styling tou
        self._list = QListWidget()
        self._list.setStyleSheet("""
            QListWidget { font-size: 13px; border: 1px solid #ccc; border-radius: 4px; }
            QListWidget::item { padding: 6px 10px; }
            QListWidget::item:selected { background: #1976d2; color: white; border-radius: 3px; }
        """)
        for lang in SUPPORTED_LANGUAGES:
            item = QListWidgetItem(lang)
            self._list.addItem(item)
            if lang == current:
                item.setSelected(True)
                self._list.setCurrentItem(item)
        self._list.itemDoubleClicked.connect(self._accept)
        layout.addWidget(self._list)
#dymiourgia row me ta buttons kai styling tou
        btn_row = QHBoxLayout()
        btn_row.addStretch()
#cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(90)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
#ok button
        ok_btn = QPushButton("OK")
        ok_btn.setFixedWidth(90)
        ok_btn.setDefault(True)
        ok_btn.setStyleSheet("background-color: #1976d2; color: white; font-weight: bold;")
        ok_btn.clicked.connect(self._accept)
        btn_row.addWidget(ok_btn)

        layout.addLayout(btn_row)
#kaleitai otan o xristis pataei ok
    def _accept(self):
        items = self._list.selectedItems()
        if items:
            self._selected = items[0].text()
        self.accept()
#language getter
    def get_selected_language(self) -> str:
        return self._selected
