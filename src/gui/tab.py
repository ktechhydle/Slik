import slik
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QSplitter, QVBoxLayout
from src.editor.editor import Editor
from src.editor.markdown_viewer import MarkdownViewer


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
        self.container = QSplitter(self)
        self.container.setHandleWidth(3)
        self.container.setOrientation(Qt.Orientation.Horizontal)

        self._editor = Editor(self._file_name, self)

        if os.path.exists(self._file_name):
            self._editor.setText(slik.read(self._file_name))

        self.container.addWidget(self._editor)
        self.layout().addWidget(self.container)

    def updateUI(self):
        if self.basename().endswith('.md'):
            # add a markdown viewer
            viewer = MarkdownViewer(self)
            viewer.setMarkdown(self._editor.text())
            self._editor.textChanged.connect(lambda: viewer.setMarkdown(self._editor.text()))

            self.container.addWidget(viewer)

        else:
            # remove the markdown viewer (if existent)
            for i in range(self.container.count()):
                widget = self.container.widget(i)

                if isinstance(widget, MarkdownViewer):
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

    def filetype(self) -> int:
        return self._file_type

    def editor(self) -> Editor:
        return self._editor
