import slik
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QSplitter, QVBoxLayout
from src.editor.editor import Editor
from src.editor.html_viewer import HtmlViewer


class Tab(QWidget):
    def __init__(self, file_name: str, tab_view, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._file_name = file_name
        self.tab_view = tab_view

        self.createUI()
        self.updateUI()

    def createUI(self):
        self._splitter = QSplitter(self)
        self._splitter.setHandleWidth(2)
        self._splitter.setOrientation(Qt.Orientation.Horizontal)

        self._editor = Editor(self._file_name, self)

        if os.path.exists(self._file_name):
            self._editor.setText(slik.read(self._file_name))

        self._splitter.addWidget(self._editor)
        self.layout().addWidget(self._splitter)

    def updateUI(self):
        if self.basename().endswith(('.md', '.html', '.svg')):
            viewer = HtmlViewer(self)
            viewer.setMarkdown(self._editor.text())
            self._editor.textChanged.connect(lambda: viewer.setMarkdown(self._editor.text()))

            self._splitter.addWidget(viewer)

        else:
            # remove the markdown viewer (if existent)
            for i in range(self._splitter.count()):
                widget = self._splitter.widget(i)

                if isinstance(widget, HtmlViewer):
                    widget.close()
                    del widget

        self._editor.setFileName(self._file_name)

    def save(self):
        slik.write(self._file_name, self._editor.text())

    def setFileName(self, name: str):
        self._file_name = name

        self.tab_view.setTabText(self.tab_view.indexOf(self), os.path.basename(name))
        self.updateUI()

    def filename(self) -> str:
        return self._file_name

    def basename(self) -> str:
        return os.path.basename(self._file_name)

    def editor(self) -> Editor:
        return self._editor
