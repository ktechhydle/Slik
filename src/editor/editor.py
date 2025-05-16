from PyQt6.Qsci import QsciScintilla, QsciAPIs
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QKeyEvent, QFont, QPixmap
from src.editor.auto_completer import AutoCompleter
from src.editor.lexers import PythonLexer, RustLexer, HTMLLexer, CSSLexer, MarkdownLexer, PlainTextLexer


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
        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColumn(120)
        self.setCaretLineVisible(True)
        self.setCaretWidth(3)
        self.setCallTipsStyle(QsciScintilla.CallTipsStyle.CallTipsContext)
        self.setCallTipsVisible(0)
        self.setCallTipsPosition(QsciScintilla.CallTipsPosition.CallTipsAboveText)

        self._file_name = file_name
        self._lexer = None

        self.cursorPositionChanged.connect(self.getAutoCompletions)
        self.textChanged.connect(self.textModified)

        self.createLexer()
        self.createMargins()
        self.createStyle()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.enter(event)

        elif event.key() in (
                Qt.Key.Key_ParenLeft,
                Qt.Key.Key_BracketLeft,
                Qt.Key.Key_BraceLeft,
                Qt.Key.Key_QuoteDbl,
                Qt.Key.Key_Apostrophe,
                Qt.Key.Key_QuoteLeft,
        ):
            self.wrapSelected(event)

        else:
            super().keyPressEvent(event)

    def setText(self, text: str, preserve=False):
        x, y = self.horizontalScrollBar().value(), self.verticalScrollBar().value()

        super().setText(text)

        if preserve:
            self.horizontalScrollBar().setValue(x)
            self.verticalScrollBar().setValue(y)

    def createLexer(self):
        if self._file_name.endswith('.py'):
            self._lexer = PythonLexer()

        elif self._file_name.endswith('.rs'):
            self._lexer = RustLexer(self)

        elif self._file_name.endswith('.html'):
            self._lexer = HTMLLexer()

        elif self._file_name.endswith('.css'):
            self._lexer = CSSLexer()

        elif self._file_name.endswith('.md'):
            self._lexer = MarkdownLexer()

        else:
            self._lexer = PlainTextLexer(self)
            self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsDocument)

        self.setLexer(self._lexer)

        self.api = QsciAPIs(self._lexer)
        self.auto_completer = AutoCompleter(self._file_name, self.api)
        self.auto_completer.finished.connect(self.loadAutoCompletions)

    def createMargins(self):
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginsFont(QFont('JetBrains Mono'))
        self.setMarginLineNumbers(0, True)
        self.setMarginSensitivity(0, True)
        self.setFolding(QsciScintilla.FoldStyle.PlainFoldStyle, 1)

        down_triangle = QPixmap('resources/icons/ui/triangle_down_icon.svg').scaled(18, 18)
        right_triangle = QPixmap('resources/icons/ui/triangle_right_icon.svg').scaled(18, 18)
        self.markerDefine(down_triangle, QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.markerDefine(right_triangle, QsciScintilla.SC_MARKNUM_FOLDER)

        self.setMarginWidth(0, '000000')
        self.setMarginWidth(1, 45)

    def createStyle(self):
        self.setMarginsBackgroundColor(QColor('#121212'))
        self.setMarginsForegroundColor(QColor('#454545'))
        self.setIndentationGuidesBackgroundColor(QColor('#383838'))
        self.setIndentationGuidesForegroundColor(QColor('#383838'))
        self.setFoldMarginColors(QColor('#121212'), QColor('#121212'))
        self.setWhitespaceBackgroundColor(QColor('#383838'))
        self.setWhitespaceForegroundColor(QColor('#ffffff'))
        self.setSelectionBackgroundColor(QColor('#214283'))
        self.setCaretForegroundColor(QColor('#ffffff'))
        self.setCaretLineBackgroundColor(QColor('#2b2b2b'))
        self.setMatchedBraceBackgroundColor(QColor('#505050'))
        self.setMatchedBraceForegroundColor(QColor('#ffffff'))
        self.setUnmatchedBraceBackgroundColor(QColor('#505050'))
        self.setUnmatchedBraceForegroundColor(QColor('#ff0000'))
        self.setCallTipsBackgroundColor(QColor('#1e1e1e'))
        self.setCallTipsForegroundColor(QColor('#61afef'))
        self.setCallTipsHighlightColor(QColor('#abb2bf'))
        self.setEdgeColor(QColor('#383838'))

        # fix the braces being too small
        font = QFont('JetBrains Mono', 14)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, QsciScintilla.STYLE_BRACELIGHT,
                                  font.family().encode())
        self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, QsciScintilla.STYLE_BRACELIGHT, font.pointSize())
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, QsciScintilla.STYLE_BRACEBAD, font.family().encode())
        self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, QsciScintilla.STYLE_BRACEBAD, font.pointSize())

    def enter(self, event: QKeyEvent):
        line, index = self.getCursorPosition()
        current_line_text = self.text(line)[:index].rstrip()
        indent = self.indentation(line)

        # python style indents
        if self.filename().endswith('.py'):
            if current_line_text.endswith(':'):
                indent += self.tabWidth()

            elif any(keyword in current_line_text for keyword in (
                    'return',
                    'pass',
                    'break',
                    'continue',
                    'raise',
                    '...')):
                indent -= self.tabWidth()

            else:
                super().keyPressEvent(event)

                return

            self.beginUndoAction()
            self.insert('\n')
            self.setIndentation(line + 1, indent)
            self.setCursorPosition(line + 1, indent)
            self.endUndoAction()

        # bracket style indentation
        elif self.filename().endswith(('.rs', '.css', '.qss', '.json')):
            self.beginUndoAction()

            if current_line_text.endswith('{') and '}' in self.text(line):
                self.insert('\n')
                self.insert('\n')
                self.setIndentation(line + 1, indent + self.tabWidth())
                self.setIndentation(line + 2, indent)
                self.setCursorPosition(line + 1, indent + self.tabWidth())

            elif current_line_text.endswith('{'):
                self.insert('\n')
                self.setIndentation(line + 1, indent + self.tabWidth())
                self.setCursorPosition(line + 1, indent + self.tabWidth())

            else:
                self.insert('\n')
                self.setIndentation(line + 1, indent)
                self.setCursorPosition(line + 1, indent)

            self.endUndoAction()

        else:
            super().keyPressEvent(event)

    def wrapSelected(self, event: QKeyEvent):
        pairs = {
            Qt.Key.Key_ParenLeft: ('(', ')'),
            Qt.Key.Key_BracketLeft: ('[', ']'),
            Qt.Key.Key_BraceLeft: ('{', '}'),
            Qt.Key.Key_QuoteDbl: ('"', '"'),
            Qt.Key.Key_Apostrophe: ("'", "'"),
            Qt.Key.Key_QuoteLeft: ('`', '`'),
        }

        left, right = pairs[event.key()]
        selected = self.selectedText()

        if selected:
            self.beginUndoAction()

            start_line, start_column, end_line, end_column = self.getSelection()

            self.replaceSelectedText(f'{left}{selected}{right}')

            self.endUndoAction()
            self.setSelection(start_line, start_column + 1, end_line, end_column + 1)

        else:
            super().keyPressEvent(event)

    def getAutoCompletions(self):
        if not self.selectedText():
            line, column = self.getCursorPosition()
            self.auto_completer.getCompletion(line + 1, column, self.text())
            self.autoCompleteFromAPIs()

    def loadAutoCompletions(self):
        pass

    def textModified(self):
        if self._lexer:
            line, column = self.getCursorPosition()
            start = self.positionFromLineIndex(line, 0)
            end = self.positionFromLineIndex(line, column)

            if hasattr(self._lexer, 'startStyling'): # only custom lexers have the "startStyling" method
                self._lexer.startStyling(start, end)

    def setFileName(self, file_name: str):
        self._file_name = file_name

        self.createLexer()
        self.createMargins()
        self.createStyle()

    def filename(self) -> str:
        return self._file_name
