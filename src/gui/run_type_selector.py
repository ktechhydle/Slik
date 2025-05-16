from PyQt6.QtWidgets import QComboBox


class RunTypeSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._run_configs = {
            'Python [main]': 'PYTHONPATH+main.py',
            'Python [current]': 'PYTHONPATH+CURRENTFILEPY',
            'Rust [cargo]': 'cargo+run',
        }

        self.createOptions()

    def createOptions(self):
        self.clear()

        for display, value in self._run_configs.items():
            self.addItem(display, value)