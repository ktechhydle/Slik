import os
import slik
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QComboBox, QApplication, QWidget, QHBoxLayout


class RunTypeSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._run_configs = {
            'Python [main]': ('resources/icons/logos/python_icon.svg', 'PYTHONPATH+MAINPY'),
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

    def setRunConfigs(self, config: dict[str, tuple[str, str]]):
        self._run_configs = config

        self.createOptions()

    def runConfigs(self) -> dict[str, tuple[str, str]]:
        return self._run_configs

    def runConfig(self) -> str:
        return self.itemData(self.currentIndex())


class PythonPathSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        QApplication.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)

        self._project_dir = ''
        self._python_paths = {
            'Python [system]': 'python'
        }

        self.createOptions()

    def createOptions(self):
        self.clear()

        for display, value in self._python_paths.items():
            self.addItem(display, value)

    def updatePythonPaths(self):
        self._python_paths.clear()
        self._python_paths['Python [system]'] = 'python'

        python_path = slik.get_python_path(self._project_dir)

        if os.path.exists(python_path): # we can add a virtual environment
            self._python_paths['Python [venv]'] = python_path

        self.createOptions()

    def setPythonPaths(self, path: str):
        self._python_paths = path

        self.createOptions()

    def setProjectDir(self, path: str):
        if path != self._project_dir:
            self._project_dir = path

            self.updatePythonPaths()

    def pythonPaths(self) -> dict[str, str]:
        return self._python_paths

    def pythonPath(self) -> str:
        return self.itemData(self.currentIndex())

    def projectDir(self) -> str:
        return self._project_dir


class ConfigureBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('configureBar')
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)

        self.createUI()

    def createUI(self):
        self._run_type_selector = RunTypeSelector(self)
        self._python_path_selector = PythonPathSelector(self)

        self.layout().addWidget(self._run_type_selector)
        self.layout().addWidget(self._python_path_selector)

    def runTypeSelector(self) -> RunTypeSelector:
        return self._run_type_selector

    def pythonPathSelector(self) -> PythonPathSelector:
        return self._python_path_selector