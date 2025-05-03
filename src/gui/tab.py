from src.imports import *
from src.editor.editor import Editor


class Tab(QWidget):
    FileTypePython = 0
    FileTypeRust = 1
    FileTypeHtml = 2
    FileTypeCSS = 3
    FileTypeMarkdown = 4
    FileTypePlainText = 5

    def __init__(self, file_name: str, tab_view, file_type: int = FileTypePython, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._file_name = file_name
        self._file_type = file_type
        self.tab_view = tab_view

        self.createUI()

    def createUI(self):
        self._editor = Editor(self._file_name, self._file_type, self)

        if os.path.exists(self._file_name):
            self._editor.setText(slik.read(self._file_name))

        self.layout().addWidget(self._editor)

    def editor(self) -> Editor:
        return self._editor
