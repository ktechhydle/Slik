import re
import types
import builtins
import keyword
from PyQt6.Qsci import QsciLexerCustom, QsciScintilla, QsciLexerCSS
from PyQt6.QtGui import QColor, QFont


class BaseLexer(QsciLexerCustom):
    DEFAULT = 0
    KEYWORD = 1
    BUILTINS = 2
    STRING = 3
    KEYARGS = 4
    BRACKETS = 5
    COMMENTS = 6
    CONSTANTS = 7
    FUNCTIONS = 8
    CLASS_DEF = 9
    FUNCTION_DEF = 10
    DECORATOR = 11
    TYPES = 12
    DEFAULT_NAMES = [
        'default',
        'keyword',
        'class_def',
        'functions',
        'function_def',
        'decorator',
        'string',
        'types',
        'keyargs',
        'brackets',
        'comments',
        'constants',
    ]

    def __init__(self, editor: QsciScintilla, language_name: str):
        super().__init__(editor)

        self._editor = editor
        self._language_name = language_name
        self._tokens = []
        self._keywords = []
        self._builtins = []
        self._types = []

        defaults = {}
        defaults['color'] = '#ffffff'
        defaults['paper'] = '#1e1e1e'
        defaults['font'] = ('JetBrains Mono', 14)

        self.setDefaultColor(QColor(defaults['color']))
        self.setDefaultPaper(QColor(defaults['paper']))
        self.setDefaultFont(QFont(defaults['font'][0], defaults['font'][1]))
        self.createStyle()

    def language(self):
        return self._language_name

    def description(self, style):
        if style == self.DEFAULT:
            return 'DEFAULT'

        elif style == self.KEYWORD:
            return 'KEYWORD'

        elif style == self.BUILTINS:
            return 'BUILTINS'

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

        elif style == self.DECORATOR:
            return 'DECORATOR'

        elif style == self.TYPES:
            return 'TYPES'

        return ''

    def generateTokens(self, text: str):
        p = re.compile(r'[*]\/|\/[*]|\s+|\w+|\W')

        self._token_list = [(token, len(bytearray(token, 'utf-8'))) for token in p.findall(text)]

    def nextToken(self, skip: int = None):
        if len(self._token_list) > 0:
            if skip is not None and skip != 0:
                for _ in range(skip - 1):
                    if len(self._token_list) > 0:
                        self._token_list.pop(0)

            return self._token_list.pop(0)

        else:
            return None

    def peekToken(self, n=0):
        try:
            return self._token_list[n]

        except IndexError:
            return ['']

    def skipSpacesPeek(self, skip=None):
        i = 0
        tok = " "

        if skip is not None:
            i = skip

        while tok[0].isspace():
            tok = self.peekToken(i)
            i += 1

        return tok, i

    def createStyle(self):
        pass

    def applyFolding(self, start: int, end: int):
        pass

    def setKeywords(self, keywords: list[str]):
        self._keywords = keywords

    def setBuiltinNames(self, builtin_names: list[str]):
        self._builtins = builtin_names

    def setTypes(self, types: list[str]):
        self._types = types

    def keywordList(self) -> list[str]:
        return self._keywords

    def builtinList(self) -> list[str]:
        return self._builtins

    def typeList(self) -> list[str]:
        return self._types

    def editor(self) -> QsciScintilla:
        return self._editor


class PythonLexer(BaseLexer):
    def __init__(self, editor: QsciScintilla):
        super().__init__(editor, 'Python')
        self.setKeywords(keyword.kwlist + ['self'])
        self.setBuiltinNames([name for name, obj in vars(builtins).items() if isinstance(obj, types.BuiltinFunctionType)])
        self.setTypes([name for name, obj in vars(builtins).items() if isinstance(obj, type)])

    def createStyle(self):
        normal = QColor('#abb2bf')
        font = QFont('JetBrains Mono', 14)
        italic = font
        italic.setItalic(True)

        self.setFont(italic, PythonLexer.COMMENTS)
        self.setColor(normal, PythonLexer.DEFAULT)
        self.setColor(normal, PythonLexer.BRACKETS)
        self.setColor(QColor(normal), PythonLexer.FUNCTIONS)
        self.setColor(QColor('#7f848e'), PythonLexer.COMMENTS)
        self.setColor(QColor('#c678dd'), PythonLexer.KEYWORD)
        self.setColor(QColor('#e5C07b'), PythonLexer.CLASS_DEF)
        self.setColor(QColor('#61afef'), PythonLexer.FUNCTION_DEF)
        self.setColor(QColor('#d19a66'), PythonLexer.DECORATOR)
        self.setColor(QColor('#56b6c2'), PythonLexer.BUILTINS)
        self.setColor(QColor('#56b6c2'), PythonLexer.TYPES)
        self.setColor(QColor('#d19a66'), PythonLexer.CONSTANTS)
        self.setColor(QColor('#98c379'), PythonLexer.STRING)

    def styleText(self, start, end):
        text = self.editor().text()[start:end]
        self.generateTokens(text)

        string_flag = False
        comment_flag = False

        if start > 0:
            previous_style_nr = self.editor().SendScintilla(QsciScintilla.SCI_GETSTYLEAT, start - 1)

            if previous_style_nr == PythonLexer.COMMENTS:
                comment_flag = False

        while True:
            curr_token = self.nextToken()

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
                    _ = self.nextToken(ni)
                    self.setStyling(name[1] + 1, PythonLexer.CLASS_DEF)

                    continue

                else:
                    self.setStyling(tok_len, PythonLexer.KEYWORD)

                    continue

            elif tok == 'def':
                name, ni = self.skipSpacesPeek()

                if name[0].isidentifier():
                    self.setStyling(tok_len, PythonLexer.KEYWORD)
                    _ = self.nextToken(ni)
                    self.setStyling(name[1] + 1, PythonLexer.FUNCTION_DEF)

                    continue

                else:
                    self.setStyling(tok_len, PythonLexer.KEYWORD)

                    continue

            elif tok == "'" or tok == '"':
                self.setStyling(tok_len, PythonLexer.STRING)
                string_flag = True

                continue

            elif tok == '#':
                comment_text = tok
                comment_len = tok_len

                while True:
                    peek = self.peekToken()

                    if peek is None or '\n' in peek[0]:
                        break

                    next_tok = self.nextToken()

                    if next_tok is None:
                        break

                    comment_text += next_tok[0]
                    comment_len += next_tok[1]

                self.setStyling(comment_len, PythonLexer.COMMENTS)

                continue

            elif tok == '@':
                decorator_text = tok
                decorator_len = tok_len

                while True:
                    peek = self.peekToken()

                    if peek is None or '\n' in peek[0]:
                        break

                    next_tok = self.nextToken()

                    if next_tok is None:
                        break

                    decorator_text += next_tok[0]
                    decorator_len += next_tok[1]

                self.setStyling(decorator_len, PythonLexer.DECORATOR)

            elif tok in ('f', 'b', 'r', 'br'):
                self.setStyling(tok_len, PythonLexer.STRING)

                continue

            elif tok.strip() == '.' and self.peekToken()[0].isidentifier():
                self.setStyling(tok_len, PythonLexer.DEFAULT)

                curr_token = self.nextToken()
                tok = curr_token[0]
                tok_len = curr_token[1]

                if self.peekToken()[0] == '(':
                    self.setStyling(tok_len, PythonLexer.FUNCTIONS)

                else:
                    self.setStyling(tok_len, PythonLexer.DEFAULT)

                continue

            elif tok.isnumeric():
                self.setStyling(tok_len, PythonLexer.CONSTANTS)

                continue

            elif tok in ['(', ')', '{', '}', '[', ']']:
                self.setStyling(tok_len, PythonLexer.BRACKETS)

                continue

            elif tok in self.keywordList():
                self.setStyling(tok_len, PythonLexer.KEYWORD)

                continue

            elif tok in self.builtinList():
                self.setStyling(tok_len, PythonLexer.BUILTINS)

                continue

            elif tok in self.typeList():
                self.setStyling(tok_len, PythonLexer.TYPES)

                continue

            else:
                self.setStyling(tok_len, PythonLexer.DEFAULT)

        self.applyFolding(start, end)

    def applyFolding(self, start: int, end: int):
        start_line = self.editor().SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, start)
        end_line = self.editor().SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, end)

        for line_num in range(start_line, end_line + 1):
            line_text = self.editor().text(line_num)
            indent = self.editor().SendScintilla(QsciScintilla.SCI_GETLINEINDENTATION, line_num)
            level = QsciScintilla.SC_FOLDLEVELBASE + indent // 4

            is_blank = not line_text.strip()

            if line_text.strip().startswith((
                    'def', 'class', 'if', 'elif', 'else', 'with',
                    'async', 'match', 'case', 'for', 'while',
                    'try', 'except', 'finally')):
                level |= QsciScintilla.SC_FOLDLEVELHEADERFLAG

            if is_blank:
                level |= QsciScintilla.SC_FOLDLEVELWHITEFLAG

            self.editor().SendScintilla(QsciScintilla.SCI_SETFOLDLEVEL, line_num, level)


class RustLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor, 'Rust')
        self.setKeywords([
            'abstract', 'as', 'async', 'await', 'become', 'box', 'break',
            'const', 'continue', 'crate', 'do', 'dyn', 'else', 'enum', 'extern',
            'false', 'final', 'fn', 'for', 'if', 'impl', 'in', 'let', 'loop',
            'macro', 'match', 'mod', 'move', 'mut', 'override', 'priv', 'pub',
            'ref', 'return', 'self', 'Self', 'static', 'struct', 'super', 'trait',
            'true', 'try', 'type', 'typeof', 'unsafe', 'unsized', 'use', 'virtual',
            'where', 'while', 'yield'
        ])
        self.setBuiltinNames([
            'assert', 'assert_eq', 'assert_ne', 'cfg', 'column', 'compile_error',
            'concat', 'concat_idents', 'env', 'eprint', 'eprintln', 'file',
            'format', 'format_args', 'include', 'include_bytes', 'include_str',
            'is_x86_feature_detected', 'line', 'local_path', 'module_path',
            'option_env', 'panic', 'print', 'println', 'stringify', 'todo',
            'unimplemented', 'unreachable', 'vec'
        ])
        self.setTypes([
            'i8', 'i16', 'i32', 'i64', 'i128', 'isize',
            'u8', 'u16', 'u32', 'u64', 'u128', 'usize',
            'f32', 'f64',
            'bool', 'char', 'str',
            'Option', 'Result', 'Vec', 'String',
            'Box', '&',
        ])

    def createStyle(self):
        normal = QColor('#abb2bf')
        font = QFont('JetBrains Mono', 14)
        italic = font
        italic.setItalic(True)

        self.setFont(italic, RustLexer.COMMENTS)
        self.setColor(normal, RustLexer.DEFAULT)
        self.setColor(normal, RustLexer.BRACKETS)
        self.setColor(QColor(normal), RustLexer.FUNCTIONS)
        self.setColor(QColor('#7f848e'), RustLexer.COMMENTS)
        self.setColor(QColor('#c678dd'), RustLexer.KEYWORD)
        self.setColor(QColor('#e5C07b'), RustLexer.CLASS_DEF)
        self.setColor(QColor('#61afef'), RustLexer.FUNCTION_DEF)
        self.setColor(QColor('#d19a66'), RustLexer.DECORATOR)
        self.setColor(QColor('#56b6c2'), RustLexer.BUILTINS)
        self.setColor(QColor('#56b6c2'), RustLexer.TYPES)
        self.setColor(QColor('#d19a66'), RustLexer.CONSTANTS)
        self.setColor(QColor('#98c379'), RustLexer.STRING)

    def styleText(self, start, end):
        text = self.editor().text()[start:end]
        self.generateTokens(text)

        string_flag = False
        comment_flag = False

        if start > 0:
            previous_style_nr = self.editor().SendScintilla(QsciScintilla.SCI_GETSTYLEAT, start - 1)

            if previous_style_nr == RustLexer.COMMENTS:
                comment_flag = False

        while True:
            curr_token = self.nextToken()

            if curr_token is None:
                break

            tok = curr_token[0]
            tok_len = curr_token[1]

            if comment_flag:
                self.setStyling(tok_len, RustLexer.COMMENTS)

                if tok.endswith('\n') or tok.startswith('\n'):
                    comment_flag = False

                continue

            if string_flag:
                self.setStyling(curr_token[1], RustLexer.STRING)

                if tok == '"' or tok == "'":
                    string_flag = False

                continue

            if tok in ('struct', 'enum'):
                name, ni = self.skipSpacesPeek()
                brac, _ = self.skipSpacesPeek(ni)

                if name[0].isidentifier() and brac[0] == '{':
                    self.setStyling(tok_len, RustLexer.KEYWORD)
                    _ = self.nextToken(ni)
                    self.setStyling(name[1] + 1, RustLexer.CLASS_DEF)

                    continue

                else:
                    self.setStyling(tok_len, RustLexer.KEYWORD)

                    continue

            elif tok == 'fn':
                name, ni = self.skipSpacesPeek()

                if name[0].isidentifier():
                    self.setStyling(tok_len, RustLexer.KEYWORD)
                    _ = self.nextToken(ni)
                    self.setStyling(name[1] + 1, RustLexer.FUNCTION_DEF)

                    continue

                else:
                    self.setStyling(tok_len, RustLexer.KEYWORD)

                    continue

            elif tok == "'" or tok == '"':
                self.setStyling(tok_len, RustLexer.STRING)
                string_flag = True

                continue

            elif tok == '/':
                if self.peekToken()[0] == '/': # this is a comment hence the '//'
                    comment_text = tok
                    comment_len = tok_len

                    while True:
                        peek = self.peekToken()

                        if peek is None or '\n' in peek[0]:
                            break

                        next_tok = self.nextToken()

                        if next_tok is None:
                            break

                        comment_text += next_tok[0]
                        comment_len += next_tok[1]

                    self.setStyling(comment_len, RustLexer.COMMENTS)

                    continue

            elif tok == '#':
                attribute_text = tok
                attribute_len = tok_len

                while True:
                    peek = self.peekToken()

                    if peek is None or '\n' in peek[0]:
                        break

                    next_tok = self.nextToken()

                    if next_tok is None:
                        break

                    attribute_text += next_tok[0]
                    attribute_len += next_tok[1]

                self.setStyling(attribute_len, RustLexer.DECORATOR)

            elif tok.isnumeric():
                self.setStyling(tok_len, RustLexer.CONSTANTS)

                continue

            elif tok in ['(', ')', '{', '}', '[', ']']:
                self.setStyling(tok_len, RustLexer.BRACKETS)

                continue

            elif tok in self.keywordList():
                self.setStyling(tok_len, RustLexer.KEYWORD)

                continue

            elif tok in self.builtinList():
                self.setStyling(tok_len, RustLexer.BUILTINS)

                continue

            elif tok in self.typeList():
                self.setStyling(tok_len, RustLexer.TYPES)

                continue

            else:
                self.setStyling(tok_len, RustLexer.DEFAULT)

        self.applyFolding(start, end)

    def applyFolding(self, start: int, end: int):
        start_line = self.editor().SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, start)
        end_line = self.editor().SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, end)

        for line_num in range(start_line, end_line + 1):
            line_text = self.editor().text(line_num)
            indent = self.editor().SendScintilla(QsciScintilla.SCI_GETLINEINDENTATION, line_num)
            level = QsciScintilla.SC_FOLDLEVELBASE + indent // 4

            is_blank = not line_text.strip()

            if line_text.strip().startswith((
                    'pub', 'fn', 'struct', 'enum', 'impl', 'trait', 'if', 'else',
                    'async', 'match', 'for', 'while', 'loop')):
                level |= QsciScintilla.SC_FOLDLEVELHEADERFLAG

            if is_blank:
                level |= QsciScintilla.SC_FOLDLEVELWHITEFLAG

            self.editor().SendScintilla(QsciScintilla.SCI_SETFOLDLEVEL, line_num, level)


class CSSLexer(QsciLexerCSS):
    def __init__(self):
        super().__init__()
        self.setDefaultColor(QColor('#ffffff'))
        self.setDefaultPaper(QColor('#1e1e1e'))
        self.setDefaultFont(QFont('JetBrains Mono', 14))
        self.setFoldComments(True)
        self.setFoldCompact(False)

        self.createStyle()

    def createStyle(self):
        normal = QColor('#abb2bf')
        font = QFont('JetBrains Mono', 14)
        italic = QFont('JetBrains Mono', 14)
        italic.setItalic(True)

        self.setFont(italic, CSSLexer.Comment)
        self.setFont(font, CSSLexer.Tag)
        self.setColor(normal, CSSLexer.Default)
        self.setColor(normal, CSSLexer.Operator)
        self.setColor(normal, CSSLexer.CSS1Property)
        self.setColor(normal, CSSLexer.CSS2Property)
        self.setColor(normal, CSSLexer.CSS3Property)
        self.setColor(normal, CSSLexer.UnknownProperty)
        self.setColor(QColor('#7f848e'), CSSLexer.Comment)
        self.setColor(QColor('#c678dd'), CSSLexer.Tag)
        self.setColor(QColor('#d19a66'), CSSLexer.Value)
        self.setColor(QColor('#e06c75'), CSSLexer.Variable)
        self.setColor(QColor('#56b6c2'), CSSLexer.IDSelector)
        self.setColor(QColor('#56b6c2'), CSSLexer.UnknownPseudoClass)
        self.setColor(QColor('#56b6c2'), CSSLexer.PseudoClass)
        self.setColor(QColor('#98c379'), CSSLexer.DoubleQuotedString)
        self.setColor(QColor('#98c379'), CSSLexer.SingleQuotedString)


class PlainTextLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor, 'Plain Text')

    def createStyle(self):
        normal = QColor('#ffffff')

        self.setColor(normal, PlainTextLexer.DEFAULT)

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.editor().text()[start:end]

        self.setStyling(len(text), PlainTextLexer.DEFAULT)
