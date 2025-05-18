import os
import slik
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QApplication


class PythonPathSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        QApplication.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)

        self._python_paths = {
            'Python [system]': 'python'
        }

        self.createOptions()

    def createOptions(self):
        self.clear()

        for display, value in self._python_paths.items():
            self.addItem(display, value)

    def getPythonPath(self, path: str):
        self._python_paths.clear()

        python_path = slik.get_python_path(path)

        if os.path.exists(python_path): # we can add a virtual environment
            self._python_paths['Python [system]'] = 'python'
            self._python_paths['Python [venv]'] = python_path

        else:
            self._python_paths['Python [system]'] = python_path

        self.createOptions()

    def setPythonPaths(self, path: str):
        self._python_paths = path

        self.createOptions()

    def pythonPaths(self) -> dict[str, str]:
        return self._python_paths

    def pythonPath(self) -> str:
        return self.itemData(self.currentIndex())
