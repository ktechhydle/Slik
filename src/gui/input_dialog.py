from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget, QLabel, QWidgetAction, QLineEdit
from src.gui.title_bar import TitleBar
from src.gui.message_dialog import MessageDialog


class InputDialog(MessageDialog):
    def __init__(self, title: str, message: str, standard_buttons: tuple, parent=None):
        super().__init__(title, message, standard_buttons, parent)

    def createUI(self):
        self._container = QWidget()
        self._container.setLayout(QVBoxLayout())

        self._title_bar = TitleBar(self)
        self._message_label = QLabel(self._message)
        self._message_label.setWordWrap(True)
        self._input = QLineEdit()
        self._input.setFixedHeight(30)

        self._container.layout().addWidget(self._title_bar)
        self._container.layout().addSpacing(20)
        self._container.layout().addWidget(self._message_label)
        self._container.layout().addWidget(self._input)
        self._container.layout().addStretch()

        action = QWidgetAction(self)
        action.setDefaultWidget(self._container)
        self.addAction(action)

    def value(self) -> str:
        return self._input.text()
