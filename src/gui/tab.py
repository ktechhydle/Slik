import slik
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QSplitter, QVBoxLayout, QTabWidget
from src.editor.editor import Editor
from src.editor.html_viewer import HtmlViewer


class Tab(QWidget):
    def __init__(self, file_name: str, tab_view: QTabWidget, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._file_name = file_name
        self.tab_view = tab_view
        self._saved = True

        self.createUI()
        self.updateUI()

    def createUI(self):
        self._splitter = QSplitter(self)
        self._splitter.setHandleWidth(2)
        self._splitter.setOrientation(Qt.Orientation.Horizontal)

        self._editor = Editor(self._file_name, self)
        self._editor.textChanged.connect(self.setUnsaved)

        if os.path.exists(self._file_name):
            self._editor.setText(slik.read(self._file_name))

        self._splitter.addWidget(self._editor)
        self.layout().addWidget(self._splitter)

    def updateUI(self):
        # remove the html viewer (if existent)
        for i in range(self._splitter.count()):
            widget = self._splitter.widget(i)

            if isinstance(widget, HtmlViewer):
                widget.deleteLater()

        file_ext = os.path.splitext(self.basename())[1]

        if file_ext in ('.md', '.html', '.svg'):
            self._viewer = HtmlViewer(self.tab_view.projectDir(), self)

            if file_ext in ('.md', '.svg'):
                # needs custom properties
                self._viewer.setHtml(slik.read('resources/html/markdown_template.html'))
                self._viewer.setMarkdown(self._editor.text())
                self._editor.textChanged.connect(lambda: self._viewer.setMarkdown(self._editor.text()))

            else:
                # plain html doc, just read it
                self._viewer.setHtml(self._editor.text())
                self._editor.textChanged.connect(lambda: self._viewer.setHtml(self._editor.text()))

            self._splitter.addWidget(self._viewer)

        self._editor.setFileName(self._file_name)

    def save(self):
        slik.write(self._file_name, self._editor.text())

        self.setSaved()

    def setSaved(self):
        self._saved = True
        self.tab_view.setTabIcon(self.tab_view.indexOf(self), QIcon(''))

    def setUnsaved(self):
        if self._editor.text() != slik.read(self._file_name):
            self._saved = False
            self.tab_view.setTabIcon(self.tab_view.indexOf(self), QIcon('resources/icons/ui/unsaved_icon.svg'))

            return

        self.setSaved()

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
