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

        self.setFont(QFont(regular))

        self.setColor(QColor('gray'), self.Comment)
        self.setColor(QColor('#ff79c6'), self.Keyword)
        self.setColor(QColor('#53a7f4'), self.FunctionMethodName)
        self.setColor(QColor('#ffffff'), self.ClassName)
        self.setColor(QColor('#9ecbff'), self.SingleQuotedString)
        self.setColor(QColor('#9ecbff'), self.SingleQuotedFString)
        self.setColor(QColor('#9ecbff'), self.DoubleQuotedString)
        self.setColor(QColor('#9ecbff'), self.DoubleQuotedFString)
        self.setColor(QColor('#9ecbff'), self.TripleSingleQuotedString)
        self.setColor(QColor('#9ecbff'), self.TripleSingleQuotedFString)
        self.setColor(QColor('#9ecbff'), self.TripleDoubleQuotedString)
        self.setColor(QColor('#9ecbff'), self.TripleDoubleQuotedFString)
        self.setColor(QColor('#9ecbff'), self.UnclosedString)
        self.setColor(QColor('#2aacb8'), self.Number)
