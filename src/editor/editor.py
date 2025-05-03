from src.imports import *
from src.editor.lexers import PythonLexer


class Editor(QsciScintilla):
    FileTypePython = 0
    FileTypeRust = 1
    FileTypeHtml = 2
    FileTypeCSS = 3
    FileTypeMarkdown = 3

    def __init__(self, file_type: int, parent=None):
        super().__init__(parent)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor('#303030'))

        self._file_type = file_type

        self.createUI()

    def createUI(self):
        if self._file_type == Editor.FileTypePython:
            self.setLexer(PythonLexer())

        self.setPaper(QColor('#121212'))
