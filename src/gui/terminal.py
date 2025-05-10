import os
import subprocess
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit


class CommandRunner(QThread):
    outputReady = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self._command = command

    def run(self):
        try:
            process = subprocess.Popen(self._command, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True, bufsize=1)

            for line in iter(process.stdout.readline, ''):
                if line:
                    self.outputReady.emit(line.rstrip())

            process.stdout.close()
            process.wait()

        except Exception as e:
            self.outputReady.emit(str(e))


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

        output_widget = QPlainTextEdit(self)
        output_widget.setReadOnly(True)
        output_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        output_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container.layout().insertWidget(self._container.layout().count() - 1, output_widget)

        # builtin commands
        if text.startswith('cd'):
            try:
                path = text[3:].strip()
                os.chdir(os.path.abspath(path))
                output_widget.setPlainText(f'changed working dir to {path}')

            except Exception as e:
                output_widget.setPlainText(str(e))

            self.newPrompt()

            return

        elif text.startswith(('clear', 'cls')):
            self.clear()

            return

        self._command_runner = CommandRunner(text)
        self._command_runner.outputReady.connect(lambda line: output_widget.appendPlainText(line))
        self._command_runner.finished.connect(self.newPrompt)
        self._command_runner.start()

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
