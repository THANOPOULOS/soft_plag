from PySide6.QtCore import QThread, Signal
from core.analyzer import Analyzer


class AnalysisWorker(QThread):
#dymiourgia signals gia tin epikoinonia metaksi tou backround thread kai tou main window
    progress  = Signal(int, str)
    completed = Signal(object)
    error     = Signal(str)
#kaleitai apo to main_window.on_compare() otan o xristis patisei to "Compare" button. O worker trexei se background thread gia na min kanei freeze to UI
    def __init__(self, folder: str, language: str, parent=None):
        super().__init__(parent)
        self._folder   = folder
        self._language = language
#kaleitai automata apo ton Qt otan ekteleitai to worker.start()
    def run(self):
        try:
            analyzer = Analyzer(self._folder, self._language)
            result = analyzer.run(progress_cb=self._on_progress)
            self.progress.emit(100, "Done.")
            self.completed.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))
#pairnei to pososto kai to minima apo ton analyzer kai ta ekpempei os signal sto main window
    def _on_progress(self, pct: int, msg: str):
        self.progress.emit(int(pct), msg)
