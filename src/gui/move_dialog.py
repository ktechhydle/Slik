import os
from PyQt6.QtCore import QSize, QTimer, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFileDialog, QPushButton, QVBoxLayout, QWidget, QLabel, QWidgetAction, QLineEdit
from src.gui.title_bar import TitleBar
from src.gui.message_dialog import MessageDialog


class Input(QLineEdit):
    def showEvent(self, event):
        super().showEvent(event)

        QTimer.singleShot(0, self.setFocus)


class MoveDialog(MessageDialog):
    def __init__(self, title: str, message: str, standard_buttons: tuple, parent=None):
        super().__init__(title, message, standard_buttons, parent)

        #self.setTargetSize(QSize())

    def createUI(self):
        self._container = QWidget()
        self._container.setLayout(QVBoxLayout())

        self._title_bar = TitleBar(self)
        self._message_label = QLabel(self._message)
        self._message_label.setWordWrap(True)
        change_dir_btn = QPushButton(QIcon('resources/icons/ui/folder_icon.svg'), '', self)
        change_dir_btn.setFixedSize(25, 25)
        change_dir_btn.clicked.connect(self.changeDir)
        self._input = Input()
        self._input.setFixedHeight(30)

        self._container.layout().addWidget(self._title_bar)
        self._container.layout().addSpacing(20)
        self._container.layout().addWidget(self._message_label)
        self._container.layout().addWidget(change_dir_btn)
        self._container.layout().addWidget(self._input)
        self._container.layout().addStretch()

        action = QWidgetAction(self)
        action.setDefaultWidget(self._container)
        self.addAction(action)

    def changeDir(self):
        path = QFileDialog.getExistingDirectory(self, 'Choose Directory')

        if path:
            path = os.path.abspath(path).replace('\\', '/')
            self._input.setText(path)

    def value(self) -> str:
        return self._input.text()

    def input(self) -> Input:
        return self._input
