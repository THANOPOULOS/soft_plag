import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

from gui.main_window import MainWindow


def _apply_palette(app: QApplication):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor("#f5f5f5"))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor("#212121"))
    palette.setColor(QPalette.ColorRole.Base,            QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#f0f4ff"))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#fffde7"))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor("#212121"))
    palette.setColor(QPalette.ColorRole.Text,            QColor("#212121"))
    palette.setColor(QPalette.ColorRole.Button,          QColor("#e3e8f5"))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#212121"))
    palette.setColor(QPalette.ColorRole.BrightText,      QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Link,            QColor("#1976d2"))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor("#1976d2"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SoftPlag")
    app.setOrganizationName("SoftPlag")
    _apply_palette(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
