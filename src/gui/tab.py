from src.imports import *
from src.editor.editor import Editor


class Tab(QWidget):
    def __init__(self, file_name: str, tab_view, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._file_name = file_name
        self.tab_view = tab_view

        self.createUI()

    def createUI(self):
        container = QWidget(self)
        container.setLayout(QHBoxLayout())
        container.layout().setContentsMargins(0, 0, 0, 0)

        self._editor = Editor(self._file_name, self)

        if os.path.exists(self._file_name):
            self._editor.setText(slik.read(self._file_name))

        container.layout().addWidget(self._editor)
        self.layout().addWidget(container)

    def updateEditor(self):
        self._editor.setFileName(self._file_name)

    def save(self):
        slik.write(self._file_name, self._editor.text())

    def setFileName(self, name: str):
        self._file_name = name

        self.tab_view.setTabText(self.tab_view.indexOf(self), os.path.basename(name))
        self.updateEditor()

    def filename(self) -> str:
        return self._file_name

    def filetype(self) -> int:
        return self._file_type

    def editor(self) -> Editor:
        return self._editor
