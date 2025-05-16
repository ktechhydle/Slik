from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QComboBox, QApplication


class RunTypeSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        QApplication.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)

        self._run_configs = {
            'Python [main]': ('resources/icons/logos/python_icon.svg', 'PYTHONPATH+main.py'),
            'Python [current]': ('resources/icons/logos/python_icon.svg', 'PYTHONPATH+CURRENTFILEPY'),
            'Rust [cargo]': ('resources/icons/logos/rust_icon.svg', 'cargo+run'),
        }

        self.createOptions()

    def createOptions(self):
        self.clear()

        for display, (icon, value) in self._run_configs.items():
            def make_icon(path):
                pixmap = QPixmap(path)
                icon = QIcon()
                icon.addPixmap(pixmap, QIcon.Mode.Normal)
                icon.addPixmap(pixmap, QIcon.Mode.Selected)

                return icon

            self.addItem(make_icon(icon), display, value)
