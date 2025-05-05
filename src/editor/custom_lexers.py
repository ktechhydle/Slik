from src.imports import *
from tree_sitter import Parser, Node, Language
import tree_sitter_python as PYTHON
import tree_sitter_rust as RUST
import types
import keyword
import builtins


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
        self.token_list = []
        self.keywords_list = []
        self.builtin_names = []

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
        self.parser = Parser(Language(PYTHON.language()))

    def createStyle(self):
        normal = QColor('#abb2bf')
        italic = QFont('JetBrains Mono', 14)
        italic.setItalic(True)

        self.setFont(italic, PythonLexer.COMMENTS)
        self.setColor(normal, PythonLexer.DEFAULT)
        self.setColor(normal, PythonLexer.BRACKETS)
        self.setColor(QColor('#7f848e'), PythonLexer.COMMENTS)
        self.setColor(QColor('#c678dd'), PythonLexer.KEYWORD)
        self.setColor(QColor('#e5C07b'), PythonLexer.CLASS_DEF)
        self.setColor(QColor('#61afef'), PythonLexer.FUNCTIONS)
        self.setColor(QColor('#61afef'), PythonLexer.FUNCTION_DEF)
        self.setColor(QColor('#56b6c2'), PythonLexer.TYPES)
        self.setColor(QColor('#d19a66'), PythonLexer.CONSTANTS)
        self.setColor(QColor('#98c379'), PythonLexer.STRING)

    def styleText(self, start, end):
        self.startStyling(start)

        # get text
        raw_bytes = self.editor.bytes(start, end)
        text = raw_bytes.data().decode('utf-8').replace('\0', '')
        tree = self.parser.parse(bytes(text, 'utf8'))

        def walk(node: Node):
            for child in node.children:
                if child.type == 'comment':
                    self.setStyling(child.end_byte - child.start_byte, PythonLexer.COMMENTS)

                else:
                    self.setStyling(child.end_byte - child.start_byte, PythonLexer.DEFAULT)

                walk(child)

        walk(tree.root_node)
        print(tree.root_node)

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
                    'try', 'except', 'finally', '"""', "'''")):
                level |= QsciScintilla.SC_FOLDLEVELHEADERFLAG

            if is_blank:
                level |= QsciScintilla.SC_FOLDLEVELWHITEFLAG

            self.editor.SendScintilla(QsciScintilla.SCI_SETFOLDLEVEL, line_num, level)


class RustLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor, 'Rust')
        self.setKeywords([

        ])
        self.setBuiltinNames([

        ])

    def createStyle(self):
        normal = QColor('#ffffff')

        self.setColor(normal, RustLexer.DEFAULT)
        self.setColor(normal, RustLexer.BRACKETS)
        self.setColor(QColor('#6a737d'), RustLexer.COMMENTS)
        self.setColor(QColor('#ff79c6'), RustLexer.KEYWORD)
        self.setColor(normal, RustLexer.CLASSES)
        self.setColor(QColor('#79c0ff'), RustLexer.FUNCTIONS)
        self.setColor(QColor('#53a7f4'), RustLexer.FUNCTION_DEF)
        self.setColor(normal, RustLexer.TYPES)
        self.setColor(QColor('#b392f0'), RustLexer.CONSTANTS)
        self.setColor(QColor('#9ecbff'), RustLexer.STRING)

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.editor.text()[start:end]
        self.generateTokens(text)

        string_flag = False
        comment_flag = False

        if start > 0:
            previous_style_nr = self.editor.SendScintilla(QsciScintilla.SCI_GETSTYLEAT, start - 1)

            if previous_style_nr == self.COMMENTS:
                comment_flag = False

        while True:
            curr_token = self.nextTok()

            if curr_token is None:
                break

            tok = curr_token[0]
            tok_len = curr_token[1]

            if comment_flag:
                self.setStyling(tok_len, PythonLexer.COMMENTS)

                if tok.endswith('\n') or tok.startswith('\n'):
                    comment_flag = False

                continue

            if string_flag:
                self.setStyling(curr_token[1], PythonLexer.STRING)

                if tok == '"' or tok == "'":
                    string_flag = False

                continue

            if tok == 'class':
                name, ni = self.skipSpacesPeek()
                brac_or_colon, _ = self.skipSpacesPeek(ni)

                if name[0].isidentifier() and brac_or_colon[0] in (':', '('):
                    self.setStyling(tok_len, PythonLexer.KEYWORD)
                    _ = self.nextTok(ni)
                    self.setStyling(name[1] + 1, PythonLexer.CLASSES)

                    continue

                else:
                    self.setStyling(tok_len, PythonLexer.KEYWORD)

                    continue

            elif tok == 'def':
                name, ni = self.skipSpacesPeek()

                if name[0].isidentifier():
                    self.setStyling(tok_len, PythonLexer.KEYWORD)
                    _ = self.nextTok(ni)
                    self.setStyling(name[1] + 1, PythonLexer.FUNCTION_DEF)

                    continue

                else:
                    self.setStyling(tok_len, PythonLexer.KEYWORD)

                    continue

            elif tok in self.keywords_list:
                self.setStyling(tok_len, PythonLexer.KEYWORD)

                continue

            elif tok.strip() == '.' and self.peekTok()[0].isidentifier():
                self.setStyling(tok_len, PythonLexer.DEFAULT)

                curr_token = self.nextTok()
                tok = curr_token[0]
                tok_len = curr_token[1]

                if self.peekTok()[0] == '(':
                    self.setStyling(tok_len, PythonLexer.FUNCTIONS)

                else:
                    self.setStyling(tok_len, PythonLexer.DEFAULT)

                continue

            elif tok.isnumeric() or tok == 'self':
                self.setStyling(tok_len, PythonLexer.CONSTANTS)

                continue

            elif tok in ['(', ')', '{', '}', '[', ']']:
                self.setStyling(tok_len, PythonLexer.BRACKETS)

                continue

            elif tok == "'" or tok == '"':
                self.setStyling(tok_len, PythonLexer.STRING)
                string_flag = True

                continue

            elif tok == '#':
                self.setStyling(tok_len, PythonLexer.COMMENTS)
                comment_flag = True

            elif tok in self.builtin_names or tok in [
                '+',
                '-',
                '*',
                '/',
                '%',
                '=',
                '<',
                '>',
            ]:
                self.setStyling(tok_len, PythonLexer.TYPES)

                continue

            else:
                self.setStyling(tok_len, PythonLexer.DEFAULT)


class PlainTextLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor, 'Plain Text')
        self.setKeywords([])
        self.setBuiltinNames([])

    def createStyle(self):
        normal = QColor('#ffffff')

        self.setColor(normal, PlainTextLexer.DEFAULT)

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.editor.text()[start:end]
        self.generateTokens(text)

        self.setStyling(len(text), PythonLexer.DEFAULT)
