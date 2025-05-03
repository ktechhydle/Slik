from src.imports import *


class PythonLexer(QsciLexerPython):
    def __init__(self):
        super().__init__()

        self.createStyle()

    def createStyle(self):
        self.setPaper(QColor('#121212'))

        regular = QFont('JetBrains Mono')
        italic = QFont('JetBrains Mono')
        italic.setItalic(True)
        bold = QFont('JetBrains Mono')
        bold.setBold(True)

        self.setFont(regular)
        self.setFont(bold, QsciLexerPython.ClassName)
        self.setFont(bold, QsciLexerPython.FunctionMethodName)
        self.setFont(italic, QsciLexerPython.Decorator)

        self.setColor(QColor('gray'), QsciLexerPython.Comment)
        self.setColor(QColor('#ff79c6'), QsciLexerPython.Keyword)
        self.setColor(QColor('#ffffff'), QsciLexerPython.ClassName)
        self.setColor(QColor('#53a7f4'), QsciLexerPython.FunctionMethodName)
        self.setColor(QColor('#b3ae60'), QsciLexerPython.Decorator)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.SingleQuotedString)
        self.setColor(QColor('#b3ae60'), QsciLexerPython.SingleQuotedFString)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.DoubleQuotedString)
        self.setColor(QColor('#b3ae60'), QsciLexerPython.DoubleQuotedFString)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.TripleSingleQuotedString)
        self.setColor(QColor('#b3ae60'), QsciLexerPython.TripleSingleQuotedFString)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.TripleDoubleQuotedString)
        self.setColor(QColor('#b3ae60'), QsciLexerPython.TripleDoubleQuotedFString)
        self.setColor(QColor('#ff0000'), QsciLexerPython.UnclosedString)
        self.setColor(QColor('#2aacb8'), QsciLexerPython.Number)


class RustLexer(QsciLexerCustom):
    DEFAULT, KEYWORD, COMMENT, STRING, NUMBER, FUNCTION, TYPE = range(7)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.createStyle()
        self.keywords = {
            'fn', 'let', 'mut', 'struct', 'enum', 'impl', 'use', 'pub', 'mod', 'trait', 'const',
            'static', 'match', 'if', 'else', 'while', 'loop', 'for', 'in', 'break', 'continue',
            'return', 'as', 'crate', 'super', 'self', 'ref', 'type', 'where', 'dyn', 'async', 'await'
        }

    def language(self):
        return 'Rust'

    def description(self, style):
        return {
            self.DEFAULT: 'Default',
            self.KEYWORD: 'Keyword',
            self.COMMENT: 'Comment',
            self.STRING: 'String',
            self.NUMBER: 'Number',
            self.FUNCTION: 'Function',
            self.TYPE: 'Type'
        }.get(style, '')

    def styleText(self, start, end):
        editor = self.editor()
        if editor is None:
            return

        text = editor.text()[start:end]
        self.startStyling(start)

        i = 0
        token_regex = re.finditer(r'\b\w+\b|//.*|"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\'|\d+', text)

        last_end = 0
        for match in token_regex:
            begin, end_ = match.span()
            self.setStyling(begin - last_end, self.DEFAULT)

            token = match.group()
            if token in self.keywords:
                self.setStyling(end_ - begin, self.KEYWORD)
            elif token.startswith('//'):
                self.setStyling(end_ - begin, self.COMMENT)
            elif token.startswith('"') or token.startswith("'"):
                self.setStyling(end_ - begin, self.STRING)
            elif re.match(r'^\d+$', token):
                self.setStyling(end_ - begin, self.NUMBER)
            else:
                self.setStyling(end_ - begin, self.DEFAULT)

            last_end = end_

        # Style remaining text as default
        remaining = len(text) - last_end
        if remaining > 0:
            self.setStyling(remaining, self.DEFAULT)

    def createStyle(self):
        self.setPaper(QColor('#121212'))

        regular = QFont('JetBrains Mono')
        bold = QFont('JetBrains Mono')
        bold.setBold(True)
        italic = QFont('JetBrains Mono')
        italic.setItalic(True)

        self.setFont(regular, self.DEFAULT)
        self.setColor(QColor('#ffffff'), self.DEFAULT)

        self.setFont(regular, self.KEYWORD)
        self.setColor(QColor('#ff79c6'), self.KEYWORD)

        self.setFont(regular, self.COMMENT)
        self.setColor(QColor('gray'), self.COMMENT)

        self.setFont(regular, self.STRING)
        self.setColor(QColor('#9ecbff'), self.STRING)

        self.setFont(regular, self.NUMBER)
        self.setColor(QColor('#2aacb8'), self.NUMBER)

        self.setFont(regular, self.FUNCTION)
        self.setColor(QColor('#53a7f4'), self.FUNCTION)

        self.setFont(italic, self.TYPE)
        self.setColor(QColor('#ffffff'), self.TYPE)


class PlainTextLexer(QsciLexer):
    def __init__(self):
        super().__init__()

    def createStyle(self):
        self.setPaper(QColor('#121212'))
        self.setFont(QFont('JetBrains Mono'))

        self.setColor(QColor('#ffffff'))

    def description(self, style: int):
        pass
