import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from PySide6.QtWidgets import (
    QTabWidget, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QTextEdit, QLabel, QHBoxLayout, QFrame,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg, NavigationToolbar2QT,
)

from core.similarity import RISK_HIGH, RISK_MEDIUM, risk_label
from visualizations import heatmap, distribution, clustering


class ResultsPanel(QTabWidget):
#kyrio container me ola ta tabs pou ginontai inherit apo to QTabWidget, gia na exoume ta 4 tabs me ta diafora visualizations kai details
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabPosition(QTabWidget.TabPosition.North)
        self.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #ddd; border-radius: 4px; }
            QTabBar::tab { padding: 8px 18px; font-size: 12px; }
            QTabBar::tab:selected { background: #1976d2; color: white; border-radius: 3px 3px 0 0; }
        """)

        self._dist_tab   = _ChartTab()
        self._heat_tab   = _ChartTab()
        self._clust_tab  = _ChartTab()
        self._detail_tab = _DetailsTab()

        self.addTab(self._dist_tab,   "📊  Distribution")
        self.addTab(self._heat_tab,   "🌡  Heatmap")
        self.addTab(self._clust_tab,  "🔗  Clustering")
        self.addTab(self._detail_tab, "📋  Details")
#kaleitai apo tin main_window._on_analysis_complete() kai otan telionei to analysis
    def display(self, result):
        self._dist_tab.render(distribution.render_figure(result))
        self._heat_tab.render(heatmap.render_figure(result))
        self._clust_tab.render(clustering.render_figure(result))
        self._detail_tab.populate(result)

#reusable widget pou kanei hold ena matplotlib chart 
class _ChartTab(QWidget):
#kanei setup ena vertical layout
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._canvas  = None
        self._toolbar = None
#antikatastash paliou chart me neo chart, kathos kai tou toolbar
    def render(self, figure):
        if self._toolbar:
            self._layout.removeWidget(self._toolbar)
            self._toolbar.deleteLater()
            self._toolbar = None
        if self._canvas:
            plt.close(self._canvas.figure)
            self._layout.removeWidget(self._canvas)
            self._canvas.deleteLater()
            self._canvas = None

        self._canvas  = FigureCanvasQTAgg(figure)
        self._toolbar = NavigationToolbar2QT(self._canvas, self)
        self._layout.addWidget(self._toolbar)
        self._layout.addWidget(self._canvas)
        self._canvas.draw()

#emfanizei enan pinaka me ola ta scores apta file pair kai otan kanoume double click se ena row, emfanizei ena dialog me to diff twn duo arxeiwn sauto to row
class _DetailsTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        self._info = QLabel()
        self._info.setStyleSheet("font-size: 11px; color: #555; padding: 4px;")
        layout.addWidget(self._info)

        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(
            ["File A", "File B", "Jaccard", "LCS", "Winnowing", "Combined", "Risk"]
        )
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for col in range(2, 7):
            self._table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.setStyleSheet("font-size: 12px;")
        self._table.cellDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self._table)

        self._pairs = []
#kaleitai apo to ResultsPanel.display() gia na gemisei ton pinaka me ta apotelesmata
    def populate(self, result):
        self._pairs = result.pair_results
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(self._pairs))

        high = sum(1 for p in self._pairs if p.combined >= RISK_HIGH)
        med  = sum(1 for p in self._pairs if RISK_MEDIUM <= p.combined < RISK_HIGH)
        self._info.setText(
            f"Total pairs: {len(self._pairs)}   |   "
            f"High risk: {high}   Medium risk: {med}   "
            f"Low risk: {len(self._pairs) - high - med}"
        )
#ypologismos tou risk label gia kathe pair result , coloring tou row analoga me to risk level, kai gemisma tou pinaka me ta apotelesmata
        _risk_colors = {"High": "#ffcdd2", "Medium": "#fff9c4", "Low": "#c8e6c9"}

        for row, pr in enumerate(self._pairs):
            label = risk_label(pr.combined)
            color = QColor(_risk_colors[label])

            items = [
                pr.file_a, pr.file_b,
                f"{pr.jaccard:.3f}", f"{pr.lcs:.3f}",
                f"{pr.winnowing:.3f}", f"{pr.combined:.3f}",
                label,
            ]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter if col > 1
                    else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                if col == 6:
                    item.setBackground(color)
                    item.setFont(QFont("", -1, QFont.Weight.Bold))
                self._table.setItem(row, col, item)

        self._table.setSortingEnabled(True)
#kaleitai otan kanoume double click se ena cell tou pinaka
    def _on_double_click(self, row, _col):
        if row >= len(self._pairs):
            return
        pr = self._pairs[row]
        dlg = _DiffDialog(pr, self)
        dlg.show()

#emfanizei ena floating window to opoio deihnei to source code ton dio arheiwn pou sygkrinontai se ena pair result, mazi me ta scores kai to risk level gia auto to pair
class _DiffDialog(QWidget):

    def __init__(self, pair_result, parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle(f"Compare: {pair_result.file_a}  ↔  {pair_result.file_b}")
        self.resize(1100, 700)
        layout = QVBoxLayout(self)

        info = QLabel(
            f"  Jaccard: {pair_result.jaccard:.3f}   "
            f"LCS: {pair_result.lcs:.3f}   "
            f"Winnowing: {pair_result.winnowing:.3f}   "
            f"Combined: {pair_result.combined:.3f}   "
            f"Risk: {risk_label(pair_result.combined)}"
        )
        info.setStyleSheet("font-size: 12px; font-weight: bold; padding: 6px; background: #f5f5f5;")
        layout.addWidget(info)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        for title, source in [(pair_result.file_a, pair_result.source_a),
                               (pair_result.file_b, pair_result.source_b)]:
            frame = QFrame()
            vl = QVBoxLayout(frame)
            vl.setContentsMargins(2, 2, 2, 2)
            lbl = QLabel(f"  {title}")
            lbl.setStyleSheet("font-weight: bold; background: #e3f2fd; padding: 4px; font-size: 11px;")
            vl.addWidget(lbl)
            editor = QTextEdit()
            editor.setReadOnly(True)
            editor.setFont(QFont("Consolas", 10))
            editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
            editor.setPlainText(source if source else "[Source not available]")
            vl.addWidget(editor)
            splitter.addWidget(frame)

        layout.addWidget(splitter)
