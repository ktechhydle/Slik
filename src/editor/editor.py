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
        self.setCaretForegroundColor(QColor('white'))
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setTabWidth(4)

        self._file_type = file_type

        self.createLexer()
        self.createMargins()

    def createLexer(self):
        if self._file_type == Editor.FileTypePython:
            self.setLexer(PythonLexer())

        self.setPaper(QColor('#121212'))

    def createMargins(self):
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, '00000')
        self.setMarginLineNumbers(0, True)
        self.setMarginSensitivity(0, True)
        self.setMarginsBackgroundColor(QColor('#121212'))
        self.setMarginsForegroundColor(QColor('#ffffff'))
        self.setMarginType(2, QsciScintilla.MarginType.SymbolMargin)
        self.setMarginWidth(2, 12)
        self.setMarginSensitivity(2, True)
        self.setFolding(QsciScintilla.FoldStyle.CircledTreeFoldStyle, 2)
