from src.imports import *
from src.editor.custom_lexers import PythonLexer, PlainTextLexer, RustLexer
from src.editor.auto_completer import AutoCompleter


class Editor(QsciScintilla):
    def __init__(self, file_name: str, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setUtf8(True)
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
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

        self.cursorPositionChanged.connect(self.getAutoCompletions)

        self.createLexer()
        self.createMargins()
        self.createStyle()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.newLine(event)

        else:
            super().keyPressEvent(event)

    def createLexer(self):
        if self._file_name.endswith('.py'):
            self.lexer = PythonLexer(self)

        elif self._file_name.endswith('.rs'):
            self.lexer = RustLexer(self)

        elif self._file_name.endswith('.md'):
            self.lexer = PlainTextLexer(self)

        else:
            self.lexer = PlainTextLexer(self)

        self.setLexer(self.lexer)

        self.api = QsciAPIs(self.lexer)
        self.auto_completer = AutoCompleter(self._file_name, self.api)
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
        self.markerDefine(QsciScintilla.MarkerSymbol.DownTriangle, QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.markerDefine(QsciScintilla.MarkerSymbol.RightTriangle, QsciScintilla.SC_MARKNUM_FOLDER)
        self.setMarkerForegroundColor(QColor('#454545'), QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.setMarkerBackgroundColor(QColor('#454545'), QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.setMarkerForegroundColor(QColor('#454545'), QsciScintilla.SC_MARKNUM_FOLDER)
        self.setMarkerBackgroundColor(QColor('#454545'), QsciScintilla.SC_MARKNUM_FOLDER)

        self.setMarginWidth(0, '000000')
        self.setMarginWidth(1, 45)

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

        font = QFont('JetBrains Mono', 14)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, QsciScintilla.STYLE_BRACELIGHT, font.family().encode())
        self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, QsciScintilla.STYLE_BRACELIGHT, font.pointSize())

        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, QsciScintilla.STYLE_BRACEBAD, font.family().encode())
        self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, QsciScintilla.STYLE_BRACEBAD, font.pointSize())

    def newLine(self, event):
        line, index = self.getCursorPosition()
        current_line_text = self.text(line).rstrip().split('#')[0].strip()

        indent = self.indentation(line)

        # increase indent
        if current_line_text.endswith(':'):
            indent += self.tabWidth()

        # exit indent if return
        elif current_line_text.endswith('return'):
            indent -= self.tabWidth()

        self.insert('\n')

        self.setIndentation(line + 1, indent)
        self.setCursorPosition(line + 1, indent)

    def setFileName(self, file_name: str):
        self._file_name = file_name

        self.createLexer()
        self.createMargins()
        self.createStyle()

    def getAutoCompletions(self, line: int, index: int):
        if not self.selectedText():
            self.auto_completer.getCompletion(line + 1, index, self.text())
            self.autoCompleteFromAPIs()

    def loadAutoCompletions(self):
        pass
