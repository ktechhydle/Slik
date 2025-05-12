import os
import subprocess
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
    QTabWidget)


class CommandRunner(QThread):
    outputReady = pyqtSignal(str)

    def __init__(self, command, terminal):
        super().__init__()

        self._command = command
        self._terminal = terminal
        self._process = None

    def run(self):
        try:
            self._process = subprocess.Popen(
                self._command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                cwd=self._terminal.cwd(),
            )

            for line in iter(self._process.stdout.readline, ''):
                if line:
                    self.outputReady.emit(line.rstrip())

            self._process.stdout.close()
            self._process.wait()

        except Exception as e:
            self.outputReady.emit(str(e))

    def quit(self):
        if self._process:
            self._process.kill()

        super().quit()


class OutputTextEdit(QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.textChanged.connect(self.updateSize)

    def updateSize(self):
        doc_height = self.document().size().height()
        margin = self.frameWidth() * 2 + self.contentsMargins().top() + self.contentsMargins().bottom()
        new_height = int(doc_height * self.fontMetrics().height() + margin)
        line = self.fontMetrics().height() + margin

        self.setFixedHeight(new_height + line)

    def scrollToTop(self):
        self.moveCursor(QTextCursor.MoveOperation.Start)
        self.ensureCursorVisible()


class Terminal(QWidget):
    def __init__(self, cwd: str, tab_view: QTabWidget, parent=None):
        super().__init__(parent)
        self.setObjectName('terminal')
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._cwd = cwd
        self.tab_view = tab_view
        self._current_input = None

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

        label = QLabel(f'{self._cwd}>', self)
        self._current_input = QLineEdit(self)
        self._current_input.returnPressed.connect(lambda: self.run)

        command_line.layout().addWidget(label)
        command_line.layout().addWidget(self._current_input)

        self._container.layout().insertWidget(self._container.layout().count() - 1, command_line)

        self._current_input.setFocus()

    def run(self, input=None):
        if input:
            self._current_input.setText(input)

        self._current_input.setReadOnly(True)
        text = self._current_input.text()

        if text.rstrip() == '':
            self.newPrompt()

            return

        output_widget = OutputTextEdit(self)

        # builtin commands
        if text.startswith('cd'):
            try:
                path = text[3:].strip()
                self.setCwd(os.path.abspath(path))

            except Exception as e:
                output_widget.setPlainText(str(e))

            self.newPrompt()

            return

        elif text.startswith('exit'):
            self.tab_view.removeTab(self.tab_view.indexOf(self))
            self.tab_view.newTerminal()

            return

        elif text.startswith(('clear', 'cls')):
            self.clear()

            return

        self._container.layout().insertWidget(self._container.layout().count() - 1, output_widget)

        self._command_runner = CommandRunner(text, self)
        self._command_runner.outputReady.connect(lambda line: output_widget.appendPlainText(line))
        self._command_runner.finished.connect(output_widget.scrollToTop)
        self._command_runner.finished.connect(self.newPrompt)
        self._command_runner.start()

    def quit(self):
        if self.hasCurrentProcess():
            self._command_runner.quit()

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

    def setCwd(self, cwd: str):
        self._cwd = cwd

    def cwd(self) -> str:
        return self._cwd

    def hasCurrentProcess(self) -> bool:
        return hasattr(self, '_command_runner') and self._command_runner.isRunning()
