from src.imports import *


class PythonLexer(QsciLexerPython):
    def __init__(self):
        super().__init__()
        self.setFoldCompact(True)

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
        self.setColor(QColor('#ff79c6'), QsciLexerPython.Keyword)
        self.setColor(QColor('#ffffff'), QsciLexerPython.ClassName)
        self.setColor(QColor('#53a7f4'), QsciLexerPython.FunctionMethodName)
        self.setColor(QColor('#b3ae60'), QsciLexerPython.Decorator)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.SingleQuotedString)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.SingleQuotedFString)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.DoubleQuotedString)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.DoubleQuotedFString)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.TripleSingleQuotedString)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.TripleSingleQuotedFString)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.TripleDoubleQuotedString)
        self.setColor(QColor('#9ecbff'), QsciLexerPython.TripleDoubleQuotedFString)
        self.setColor(QColor('#ff0000'), QsciLexerPython.UnclosedString)
        self.setColor(QColor('#2aacb8'), QsciLexerPython.Number)


class PlainTextLexer(QsciLexer):
    def __init__(self):
        super().__init__()

    def createStyle(self):
        self.setPaper(QColor('#121212'))
        self.setFont(QFont('JetBrains Mono'))

        self.setColor(QColor('#ffffff'))
