from src.imports import *
from src.editor.lexers import PythonLexer, PlainTextLexer
from src.editor.auto_completer import AutoCompleter


class Editor(QsciScintilla):
    FileTypePython = 0
    FileTypeRust = 1
    FileTypeHtml = 2
    FileTypeCSS = 3
    FileTypeMarkdown = 4
    FileTypePlainText = 5

    def __init__(self, file_name: str, file_type: int, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setUtf8(True)
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setAutoIndent(True)
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAPIs)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusNever)
        self.setEolMode(QsciScintilla.EolMode.EolWindows)
        self.setEolVisibility(False)
        self.setCallTipsStyle(QsciScintilla.CallTipsStyle.CallTipsNoContext)
        self.setCallTipsVisible(0)
        self.setCallTipsPosition(QsciScintilla.CallTipsPosition.CallTipsAboveText)
        self.setCallTipsBackgroundColor(QColor(0xff, 0xff, 0xff, 0xff))
        self.setCallTipsForegroundColor(QColor(0x50, 0x50, 0x50, 0xff))
        self.setCallTipsHighlightColor(QColor(0xff, 0x00, 0x00, 0xff))

        self._file_name = file_name
        self._file_type = file_type

        self.cursorPositionChanged.connect(self.getAutoCompletions)

        self.createLexer()
        self.createMargins()
        self.createStyle()

    def createLexer(self):
        if self._file_type == Editor.FileTypePython:
            self.lexer = PythonLexer()

            self.setLexer(self.lexer)

        else:
            self.lexer = PlainTextLexer()

            self.setLexer(self.lexer)

        self.api = QsciAPIs(self.lexer)
        self.auto_completer = AutoCompleter(self._file_name, self._file_type, self.api)
        self.auto_completer.finished.connect(self.loadAutoCompletions)

        for style in range(128):
            self.SendScintilla(QsciScintilla.SCI_STYLESETBACK, style, QColor('#121212'))

    def createMargins(self):
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginLineNumbers(0, True)
        self.setMarginSensitivity(0, True)
        self.setMarginsBackgroundColor(QColor('#121212'))
        self.setMarginsForegroundColor(QColor('#ffffff'))

        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle, 1)
        self.setFoldMarginColors(QColor('#121212'), QColor('#121212'))

        self.setMarginWidth(0, '00000')
        self.setMarginWidth(1, 25)

    def createStyle(self):
        self.setIndentationGuidesBackgroundColor(QColor('#383838'))
        self.setIndentationGuidesForegroundColor(QColor('#383838'))
        self.setEdgeColor(QColor('#121212'))
        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setWhitespaceBackgroundColor(QColor('#383838'))
        self.setWhitespaceForegroundColor(QColor('#ffffff'))
        self.setSelectionBackgroundColor(QColor('#214283'))
        self.setCaretForegroundColor(QColor('#ffffff'))
        self.setMatchedBraceBackgroundColor(QColor('#383838'))
        self.setMatchedBraceForegroundColor(QColor('#ffffff'))
        self.setUnmatchedBraceBackgroundColor(QColor('#383838'))
        self.setUnmatchedBraceForegroundColor(QColor('#ff0000'))

    def getAutoCompletions(self, line: int, index: int):
        if self._file_type == Editor.FileTypePython:
            self.auto_completer.getPyCompletion(line + 1, index, self.text())
            self.autoCompleteFromAPIs()

        else:
            self.auto_completer.getPlainTextCompletion(line + 1, index, self.text())
            self.autoCompleteFromAPIs()

    def loadAutoCompletions(self):
        pass
