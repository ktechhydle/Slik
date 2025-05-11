import slik
import tree_sitter_python as PYTHON
from tree_sitter import Parser, Language, Query
from PyQt6.Qsci import QsciLexerCustom, QsciScintilla
from PyQt6.QtGui import QColor, QFont


class BaseLexer(QsciLexerCustom):
    DEFAULT = 0
    KEYWORD = 1
    TYPES = 2
    STRING = 3
    KEYARGS = 4
    BRACKETS = 5
    COMMENTS = 6
    CONSTANTS = 7
    FUNCTIONS = 8
    CLASS_DEF = 9
    FUNCTION_DEF = 10
    DEFAULT_NAMES = [
        'default',
        'keyword',
        'class_def',
        'functions',
        'function_def',
        'string',
        'types',
        'keyargs',
        'brackets',
        'comments',
        'constants',
    ]

    def __init__(self, editor: QsciScintilla, language_name: str):
        super().__init__(editor)

        self.editor = editor
        self.language_name = language_name

        defaults = {}
        defaults['color'] = '#ffffff'
        defaults['paper'] = '#1e1e1e'
        defaults['font'] = ('JetBrains Mono', 14)

        self.setDefaultColor(QColor(defaults['color']))
        self.setDefaultPaper(QColor(defaults['paper']))
        self.setDefaultFont(QFont(defaults['font'][0], defaults['font'][1]))
        self.createStyle()

    def language(self):
        return self.language_name

    def description(self, style):
        if style == self.DEFAULT:
            return 'DEFAULT'

        elif style == self.KEYWORD:
            return 'KEYWORD'

        elif style == self.TYPES:
            return 'TYPES'

        elif style == self.STRING:
            return 'STRING'

        elif style == self.KEYARGS:
            return 'kWARGS'

        elif style == self.BRACKETS:
            return 'BRACKETS'

        elif style == self.COMMENTS:
            return 'COMMENTS'

        elif style == self.CONSTANTS:
            return 'CONSTANTS'

        elif style == self.FUNCTIONS:
            return 'FUNCTIONS'

        elif style == self.CLASS_DEF:
            return 'CLASS_DEF'

        elif style == self.FUNCTION_DEF:
            return 'FUNCTION_DEF'

        return ''

    def createStyle(self):
        pass

    def applyFolding(self):
        pass


class PythonLexer(BaseLexer):
    def __init__(self, editor: QsciScintilla):
        super().__init__(editor, 'Python')

        self.language = Language(PYTHON.language())
        self.parser = Parser(self.language)
        self.query = Query(
            self.language,
            slik.read('resources/tree_sitter/python_highlights.scm')
        )
        self.query_captures = {
            'keyword': PythonLexer.KEYWORD,
            'keyword.operator': PythonLexer.KEYWORD,
            'keyword.definition': PythonLexer.KEYWORD,
            'constant': PythonLexer.CONSTANTS,
            'function_definition.name': PythonLexer.FUNCTION_DEF,
            'class_definition.name': PythonLexer.CLASS_DEF,
            'string': PythonLexer.STRING,
            'comment': PythonLexer.COMMENTS,
            'function.call': PythonLexer.TYPES,
            'punctuation.bracket': PythonLexer.BRACKETS,
        }

    def createStyle(self):
        normal = QColor('#abb2bf')
        font = QFont('JetBrains Mono', 14)
        italic = font
        italic.setItalic(True)

        self.setFont(italic, PythonLexer.COMMENTS)
        self.setColor(normal, PythonLexer.DEFAULT)
        self.setColor(normal, PythonLexer.BRACKETS)
        self.setColor(QColor('#7f848e'), PythonLexer.COMMENTS)
        self.setColor(QColor('#c678dd'), PythonLexer.KEYWORD)
        self.setColor(QColor('#e5C07b'), PythonLexer.CLASS_DEF)
        self.setColor(QColor('#61afef'), PythonLexer.FUNCTION_DEF)
        self.setColor(QColor('#56b6c2'), PythonLexer.TYPES)
        self.setColor(QColor('#d19a66'), PythonLexer.CONSTANTS)
        self.setColor(QColor('#98c379'), PythonLexer.STRING)

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.editor.text(start, end)
        tree = self.parser.parse(bytes(text, 'utf-8'))
        root_node = tree.root_node
        matches = self.query.captures(root_node)

        for capture_name, nodes in matches.items():
            for node in nodes:
                style = self.query_captures.get(capture_name, PythonLexer.DEFAULT)
                length = node.end_byte - node.start_byte
                print(length, style)

                self.setStyling(length, style)

        self.applyFolding(start, end)

    def applyFolding(self, start, end):
        start_line = self.editor.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, start)
        end_line = self.editor.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, end)

        for line_num in range(start_line, end_line + 1):
            line_text = self.editor.text(line_num)
            indent = self.editor.SendScintilla(QsciScintilla.SCI_GETLINEINDENTATION, line_num)
            level = QsciScintilla.SC_FOLDLEVELBASE + indent // 4

            is_blank = not line_text.strip()

            if line_text.strip().startswith((
                    'def', 'class', 'if', 'elif', 'else', 'with',
                    'async', 'match', 'case', 'for', 'while',
                    'try', 'except', 'finally')):
                level |= QsciScintilla.SC_FOLDLEVELHEADERFLAG

            if is_blank:
                level |= QsciScintilla.SC_FOLDLEVELWHITEFLAG

            self.editor.SendScintilla(QsciScintilla.SCI_SETFOLDLEVEL, line_num, level)


class RustLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor, 'Rust')

    def createStyle(self):
        normal = QColor('#abb2bf')
        italic = QFont('JetBrains Mono', 14)
        italic.setItalic(True)

        self.setFont(italic, RustLexer.COMMENTS)
        self.setColor(normal, RustLexer.DEFAULT)
        self.setColor(normal, RustLexer.BRACKETS)
        self.setColor(QColor('#7f848e'), RustLexer.COMMENTS)
        self.setColor(QColor('#c678dd'), RustLexer.KEYWORD)
        self.setColor(QColor('#e5C07b'), RustLexer.CLASS_DEF)
        self.setColor(QColor('#61afef'), RustLexer.FUNCTIONS)
        self.setColor(QColor('#61afef'), RustLexer.FUNCTION_DEF)
        self.setColor(QColor('#56b6c2'), RustLexer.TYPES)
        self.setColor(QColor('#d19a66'), RustLexer.CONSTANTS)
        self.setColor(QColor('#98c379'), RustLexer.STRING)

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.editor.text()[start:end]


class PlainTextLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor, 'Plain Text')

    def createStyle(self):
        normal = QColor('#ffffff')

        self.setColor(normal, PlainTextLexer.DEFAULT)

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.editor.text()[start:end]

        self.setStyling(len(text), PythonLexer.DEFAULT)
