from PySide6.QtCore import QThread, Signal
from core.analyzer import Analyzer


class AnalysisWorker(QThread):
    progress  = Signal(int, str)
    completed = Signal(object)
    error     = Signal(str)

    def __init__(self, folder: str, language: str, parent=None):
        super().__init__(parent)
        self._folder   = folder
        self._language = language

    def run(self):
        try:
            analyzer = Analyzer(self._folder, self._language)
            result = analyzer.run(progress_cb=self._on_progress)
            self.progress.emit(100, "Done.")
            self.completed.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))

    def _on_progress(self, pct: int, msg: str):
        self.progress.emit(int(pct), msg)
