import os
import subprocess
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit


class Terminal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('terminal')
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.createUI()
        self.newPrompt()

    def createUI(self):
        self._scroller = QScrollArea(self)
        self._scroller.setWidgetResizable(True)

        self._container = QWidget(self)
        self._container.setLayout(QVBoxLayout())
        self._container.layout().addStretch()

        self._scroller.setWidget(self._container)
        self.layout().addWidget(self._scroller)

    def newPrompt(self):
        command_line = QWidget()
        command_line.setFixedHeight(30)
        command_line.setLayout(QHBoxLayout())
        command_line.layout().setContentsMargins(0, 0, 0, 0)

        label = QLabel(f'{os.getcwd()}>', self)
        prompt_input = QLineEdit(self)
        prompt_input.returnPressed.connect(lambda: self.run(prompt_input))

        command_line.layout().addWidget(label)
        command_line.layout().addWidget(prompt_input)

        self._container.layout().insertWidget(self._container.layout().count() - 1, command_line)

        prompt_input.setFocus()

    def run(self, prompt_input: QLineEdit):
        prompt_input.setReadOnly(True)
        text = prompt_input.text()

        if text.rstrip() == '':
            self.newPrompt()

            return

        output = ''

        # change the working dir
        if text.startswith('cd'):
            try:
                path = text[3:].strip()
                os.chdir(os.path.abspath(path))
                output = f'changed working dir to {path}'

            except Exception as e:
                output = str(e)

        # clear the terminal
        elif text.startswith(('clear', 'cls')):
            self.clear()

            return

        # execute the shell command
        else:
            try:
                result = subprocess.run(text, shell=True, capture_output=True, text=True)
                output = result.stdout + result.stderr

            except Exception as e:
                output = str(e)

        output_widget = QPlainTextEdit(self)
        output_widget.setPlainText(output)
        output_widget.setReadOnly(True)
        output_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        output_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container.layout().insertWidget(self._container.layout().count() - 1, output_widget)

        self.newPrompt()

    def clear(self):
        layout = self._container.layout()
        count = layout.count()

        # skip the last item (stretch)
        for i in reversed(range(count - 1)):
            item = layout.takeAt(i)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        self.newPrompt()
