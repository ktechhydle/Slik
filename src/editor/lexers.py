from src.imports import *
import keyword
import builtins
import types


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
    CLASSES = 9
    FUNCTION_DEF = 10
    DEFAULT_NAMES = [
        'default',
        'keyword',
        'classes',
        'functions',
        'function_def',
        'string',
        'types',
        'keyargs',
        'brackets',
        'comments',
        'constants',
    ]
    FONT_WEIGHTS = {
        'thin': QFont.Weight.Thin,
        'extralight': QFont.Weight.ExtraLight,
        'light': QFont.Weight.Light,
        'normal': QFont.Weight.Normal,
        'medium': QFont.Weight.Medium,
        'demibold': QFont.Weight.DemiBold,
        'bold': QFont.Weight.Bold,
        'extrabold': QFont.Weight.ExtraBold,
        'black': QFont.Weight.Black,
    }

    def __init__(self, editor, language_name):
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

        elif style == self.CLASSES:
            return 'CLASSES'

        elif style == self.FUNCTION_DEF:
            return 'FUNCTION_DEF'

        return ''

    def createStyle(self):
        pass

    def setKeywords(self, keywords: list[str]):
        self.keywords_list = keywords

    def setBuiltinNames(self, builtin_names: list[str]):
        self.builtin_names = builtin_names

    def generateTokes(self, text: str):
        p = re.compile(r'[*]\/|\/[*]|\s+|\w+|\W')

        self.token_list = [(token, len(bytearray(token, 'utf-8'))) for token in p.findall(text)]

    def nextTok(self, skip: int = None):
        if len(self.token_list) > 0:
            if skip is not None and skip != 0:
                for _ in range(skip - 1):
                    if len(self.token_list) > 0:
                        self.token_list.pop(0)

            return self.token_list.pop(0)

        else:
            return None

    def peekTok(self, n=0):
        try:
            return self.token_list[n]

        except IndexError:
            return ['']

    def skipSpacesPeek(self, skip=None):
        i = 0
        tok = " "

        if skip is not None:
            i = skip

        while tok[0].isspace():
            tok = self.peekTok(i)
            i += 1

        return tok, i


class PythonLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor, 'Python')
        self.setKeywords(keyword.kwlist)
        self.setBuiltinNames([
            name for name, obj in vars(builtins).items() if isinstance(obj, types.BuiltinFunctionType)
        ] + ['super', 'self'])

    def createStyle(self):
        normal = QColor('#ffffff')

        self.setColor(normal, PythonLexer.DEFAULT)
        self.setColor(normal, PythonLexer.BRACKETS)
        self.setColor(QColor('#6a737d'), PythonLexer.COMMENTS)
        self.setColor(QColor('#ff79c6'), PythonLexer.KEYWORD)
        self.setColor(QColor('#ff7b72'), PythonLexer.CLASSES)
        self.setColor(QColor('#79c0ff'), PythonLexer.FUNCTIONS)
        self.setColor(QColor('#ff7b72'), PythonLexer.FUNCTION_DEF)
        self.setColor(QColor('#b392f0'), PythonLexer.TYPES)
        self.setColor(QColor('#3fa3fc'), PythonLexer.CONSTANTS)
        self.setColor(QColor('#9ecbff'), PythonLexer.STRING)

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.editor.text()[start:end]
        self.generateTokes(text)

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

            elif tok.isnumeric():
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

            elif tok in self.builtin_names:
                self.setStyling(tok_len, PythonLexer.TYPES)

                continue

            else:
                self.setStyling(tok_len, PythonLexer.DEFAULT)


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
        self.generateTokes(text)

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
        self.generateTokes(text)

        self.setStyling(len(text), PythonLexer.DEFAULT)
