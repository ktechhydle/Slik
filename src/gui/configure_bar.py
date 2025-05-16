from PyQt6.QtWidgets import QWidget, QHBoxLayout
from src.gui.run_type_selector import RunTypeSelector


class ConfigureBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('configureBar')
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)

        self.createUI()

    def createUI(self):
        self._run_type_selector = RunTypeSelector(self)

        self.layout().addWidget(self._run_type_selector)

    def runTypeSelector(self) -> RunTypeSelector:
        return self._run_type_selector