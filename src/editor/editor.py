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
        self.setBackspaceUnindents(True)
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAPIs)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusNever)
        self.setEolMode(QsciScintilla.EolMode.EolWindows)
        self.setEolVisibility(False)
        self.setCallTipsStyle(QsciScintilla.CallTipsStyle.CallTipsContext)
        self.setCallTipsVisible(0)
        self.setCallTipsPosition(QsciScintilla.CallTipsPosition.CallTipsAboveText)
        self.setCallTipsBackgroundColor(QColor(0xff, 0xff, 0xff, 0xff))
        self.setCallTipsForegroundColor(QColor(0x50, 0x50, 0x50, 0xff))
        self.setCallTipsHighlightColor(QColor(0xff, 0x00, 0x00, 0xff))

        self._file_name = file_name

        self.cursorPositionChanged.connect(self.getAutoCompletions)
        #self.textChanged.connect(self.getAutoCompletions)

        self.createLexer()
        self.createMargins()
        self.createStyle()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.enter(event)

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
            self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsDocument)

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

        # fix the braces being too small
        font = QFont('JetBrains Mono', 14)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, QsciScintilla.STYLE_BRACELIGHT,
                                  font.family().encode())
        self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, QsciScintilla.STYLE_BRACELIGHT, font.pointSize())
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, QsciScintilla.STYLE_BRACEBAD, font.family().encode())
        self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, QsciScintilla.STYLE_BRACEBAD, font.pointSize())

    def enter(self, event: QKeyEvent):
        # python style indents
        if self.filename().endswith('.py'):
            line, index = self.getCursorPosition()
            current_line_text = self.text(line)[:index].rstrip()
            indent = self.indentation(line)

            if current_line_text.endswith(':'):
                indent += self.tabWidth()

            elif any(keyword in self.text(line).rstrip().split('#')[0].strip() for keyword in (
                    'return',
                    'pass',
                    'break',
                    'continue',
                    'raise', 
                    '...')):
                indent -= self.tabWidth()

            self.beginUndoAction()
            self.insert('\n')
            self.setIndentation(line + 1, indent)
            self.setCursorPosition(line + 1, indent)
            self.endUndoAction()

        # bracket style indentation
        elif self.filename().endswith(('.rs', '.css', '.qss', '.json')):
            line, index = self.getCursorPosition()
            current_line_text = self.text(line)[:index].rstrip()
            indent = self.indentation(line)

            self.beginUndoAction()

            if current_line_text.endswith('{'):
                self.insert('\n')
                self.insert('\n')
                self.setIndentation(line + 1, indent + self.tabWidth())
                self.setIndentation(line + 2, indent)
                self.setCursorPosition(line + 1, indent + self.tabWidth())

            else:
                self.insert('\n')
                self.setIndentation(line + 1, indent)
                self.setCursorPosition(line + 1, indent)

            self.endUndoAction()

        else:
            super().keyPressEvent(event)

    def backspace(self):
        line, column = self.getCursorPosition()

        if column > 0:
            prev_char = self.text(line)[column - 1]
            next_char = self.text(line)[column] if column < len(self.text(line)) else ''

            pairs = {
                "'": "'",
                '"': '"',
                '(': ')',
                '{': '}',
                '[': ']',
                '`': '`'
            }

            if prev_char in pairs and next_char == pairs[prev_char]:
                self.setSelection(line, column, line, column + 1)
                self.removeSelectedText()

                return

    def getAutoCompletions(self, line: int, index: int):
        if not self.selectedText():
            self.auto_completer.getCompletion(line + 1, index, self.text())
            self.autoCompleteFromAPIs()

    def loadAutoCompletions(self):
        pass

    def setFileName(self, file_name: str):
        self._file_name = file_name

        self.createLexer()
        self.createMargins()
        self.createStyle()

    def filename(self) -> str:
        return self._file_name
