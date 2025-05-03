from src.imports import *
from src.editor.custom_lexers import PythonLexer, PlainTextLexer, RustLexer
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
            self.lexer = PythonLexer(self)

        elif self._file_type == Editor.FileTypeRust:
            self.lexer = RustLexer()

        else:
            self.lexer = PlainTextLexer()

        self.setLexer(self.lexer)

        self.api = QsciAPIs(self.lexer)
        self.auto_completer = AutoCompleter(self._file_name, self._file_type, self.api)
        self.auto_completer.finished.connect(self.loadAutoCompletions)

    def createMargins(self):
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginsFont(QFont('JetBrains Mono'))
        self.setMarginLineNumbers(0, True)
        self.setMarginSensitivity(0, True)
        self.setMarginsBackgroundColor(QColor('#121212'))
        self.setMarginsForegroundColor(QColor('#454545'))

        self.setFolding(QsciScintilla.FoldStyle.PlainFoldStyle, 1)
        self.setFoldMarginColors(QColor('#121212'), QColor('#121212'))
        self.markerDefine(QsciScintilla.MarkerSymbol.Minus, QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.markerDefine(QsciScintilla.MarkerSymbol.ThreeDots, QsciScintilla.SC_MARKNUM_FOLDER)
        self.setMarkerForegroundColor(QColor('#606060'), QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.setMarkerBackgroundColor(QColor('#606060'), QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.setMarkerForegroundColor(QColor('#606060'), QsciScintilla.SC_MARKNUM_FOLDER)
        self.setMarkerBackgroundColor(QColor('#606060'), QsciScintilla.SC_MARKNUM_FOLDER)

        self.setMarginWidth(0, '00000')
        self.setMarginWidth(1, 25)

    def createStyle(self):
        self.setIndentationGuidesBackgroundColor(QColor('#383838'))
        self.setIndentationGuidesForegroundColor(QColor('#383838'))
        self.setEdgeColor(QColor('#383838'))
        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setWhitespaceBackgroundColor(QColor('#383838'))
        self.setWhitespaceForegroundColor(QColor('#ffffff'))
        self.setSelectionBackgroundColor(QColor('#214283'))
        self.setCaretForegroundColor(QColor('#ffffff'))
        self.setCaretLineBackgroundColor(QColor('#2b2b2b'))
        self.setCaretLineVisible(True)
        self.setMatchedBraceBackgroundColor(QColor('#505050'))
        self.setMatchedBraceForegroundColor(QColor('#ffffff'))
        self.setUnmatchedBraceBackgroundColor(QColor('#505050'))
        self.setUnmatchedBraceForegroundColor(QColor('#ff0000'))

    def getAutoCompletions(self, line: int, index: int):
        if not self.selectedText():
            self.auto_completer.getCompletion(line + 1, index, self.text())
            self.autoCompleteFromAPIs()

    def loadAutoCompletions(self):
        pass
