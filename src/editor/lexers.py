import re
import types
import builtins
import keyword
from PyQt6.Qsci import QsciLexerCustom, QsciScintilla, QsciLexerHTML, QsciLexerCSS, QsciLexerMarkdown, QsciLexerPython, QsciLexerJSON
from PyQt6.QtGui import QColor, QFont


class Style:
    COLOR_BG = QColor('#1e1e1e')
    COLOR_NORMAL = QColor('#abb2bf')
    COLOR_COMMENT = QColor('#7f848e')
    COLOR_KEYWORD = QColor('#c678dd')
    COLOR_CLASS_DEF = QColor('#e5C07b')
    COLOR_FUNCTION_DEF = QColor('#61afef')
    COLOR_BUILTIN = QColor('#56b6c2')
    COLOR_STRING = QColor('#98c379')
    COLOR_CONSTANT = QColor('#d19a66')
    COLOR_ERROR = QColor('#ff0000')
    COLOR_LINK = QColor('#5f9bfa')
    FONT_NORMAL = QFont('JetBrains Mono', 14)
    FONT_ITALIC = QFont('JetBrains Mono', 14)
    FONT_ITALIC.setItalic(True)
    FONT_BOLD = QFont('JetBrains Mono', 14)
    FONT_BOLD.setBold(True)
    FONT_UNDERLINE = QFont('JetBrains Mono', 14)
    FONT_UNDERLINE.setUnderline(True)


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
        self.setDefaultColor(QColor('#ffffff'))
        self.setDefaultPaper(Style.COLOR_BG)
        self.setDefaultFont(Style.FONT_NORMAL)

        self._editor = editor
        self._language_name = language_name
        self._tokens = []
        self._keywords = []
        self._builtins = []
        self._types = []

        self.createStyle()

    def language(self):
        return self._language_name

    def description(self, style):
        if style == self.DEFAULT:
            return 'DEFAULT'

        elif style == self.KEYWORD:
            return 'COLOR_KEYWORD'

        elif style == self.BUILTINS:
            return 'BUILTINS'

        elif style == self.STRING:
            return 'COLOR_STRING'

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
            return 'COLOR_CLASS_DEF'

        elif style == self.FUNCTION_DEF:
            return 'COLOR_FUNCTION_DEF'

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


class PythonLexer(QsciLexerPython):
    def __init__(self, editor: QsciScintilla):
        super().__init__()
        self.setDefaultColor(QColor('#ffffff'))
        self.setDefaultPaper(Style.COLOR_BG)
        self.setDefaultFont(Style.FONT_NORMAL)
        self.setFoldCompact(False)
        self.setFoldQuotes(True)
        self.setFoldComments(True)

        self._editor = editor

        self.createStyle()

    def keywords(self, key_set: int):
        keywords = ''

        if key_set == 1:
            keyword_list = keyword.kwlist
            keyword_list.append('self')

            for kw in keyword.kwlist:
                keywords += kw + ' ' # seperate by a space

        elif key_set == 2:
            built_ins = [name for name, obj in vars(builtins).items()]

            for remove in ['exec', 'exit']:
                if remove in built_ins:
                    built_ins.remove(remove)

            for built_in in built_ins:
                keywords += built_in + ' '

        return keywords

    def createStyle(self):
        self.setFont(Style.FONT_ITALIC, PythonLexer.Comment)
        self.setFont(Style.FONT_NORMAL, PythonLexer.Default)
        self.setFont(Style.FONT_NORMAL, PythonLexer.Keyword)
        self.setFont(Style.FONT_NORMAL, PythonLexer.Identifier)
        self.setFont(Style.FONT_NORMAL, PythonLexer.Operator)
        self.setFont(Style.FONT_NORMAL, PythonLexer.ClassName)
        self.setFont(Style.FONT_NORMAL, PythonLexer.FunctionMethodName)
        self.setFont(Style.FONT_NORMAL, PythonLexer.SingleQuotedString)
        self.setFont(Style.FONT_NORMAL, PythonLexer.SingleQuotedFString)
        self.setFont(Style.FONT_NORMAL, PythonLexer.DoubleQuotedString)
        self.setFont(Style.FONT_NORMAL, PythonLexer.DoubleQuotedFString)
        self.setFont(Style.FONT_NORMAL, PythonLexer.TripleSingleQuotedString)
        self.setFont(Style.FONT_NORMAL, PythonLexer.TripleSingleQuotedFString)
        self.setFont(Style.FONT_NORMAL, PythonLexer.TripleDoubleQuotedString)
        self.setFont(Style.FONT_NORMAL, PythonLexer.TripleDoubleQuotedFString)
        self.setFont(Style.FONT_NORMAL, PythonLexer.UnclosedString)

        self.setColor(Style.COLOR_NORMAL, PythonLexer.Default)
        self.setColor(Style.COLOR_NORMAL, PythonLexer.Identifier)
        self.setColor(Style.COLOR_BUILTIN, PythonLexer.HighlightedIdentifier)
        self.setColor(Style.COLOR_NORMAL, PythonLexer.Operator)
        self.setColor(Style.COLOR_COMMENT, PythonLexer.Comment)
        self.setColor(Style.COLOR_COMMENT, PythonLexer.CommentBlock)
        self.setColor(Style.COLOR_KEYWORD, PythonLexer.Keyword)
        self.setColor(Style.COLOR_CLASS_DEF, PythonLexer.ClassName)
        self.setColor(Style.COLOR_FUNCTION_DEF, PythonLexer.FunctionMethodName)
        self.setColor(Style.COLOR_CONSTANT, PythonLexer.Decorator)
        self.setColor(Style.COLOR_CONSTANT, PythonLexer.Number)
        self.setColor(Style.COLOR_STRING, PythonLexer.SingleQuotedString)
        self.setColor(Style.COLOR_STRING, PythonLexer.SingleQuotedFString)
        self.setColor(Style.COLOR_STRING, PythonLexer.DoubleQuotedString)
        self.setColor(Style.COLOR_STRING, PythonLexer.DoubleQuotedFString)
        self.setColor(Style.COLOR_STRING, PythonLexer.TripleSingleQuotedString)
        self.setColor(Style.COLOR_STRING, PythonLexer.TripleSingleQuotedFString)
        self.setColor(Style.COLOR_STRING, PythonLexer.TripleDoubleQuotedString)
        self.setColor(Style.COLOR_STRING, PythonLexer.TripleDoubleQuotedFString)
        self.setColor(Style.COLOR_ERROR, PythonLexer.UnclosedString)

        self.setPaper(Style.COLOR_BG, PythonLexer.UnclosedString)


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
        self.setFont(Style.FONT_ITALIC, RustLexer.COMMENTS)
        self.setColor(Style.COLOR_NORMAL, RustLexer.DEFAULT)
        self.setColor(Style.COLOR_NORMAL, RustLexer.BRACKETS)
        self.setColor(Style.COLOR_NORMAL, RustLexer.FUNCTIONS)
        self.setColor(Style.COLOR_COMMENT, RustLexer.COMMENTS)
        self.setColor(Style.COLOR_KEYWORD, RustLexer.KEYWORD)
        self.setColor(Style.COLOR_CLASS_DEF, RustLexer.CLASS_DEF)
        self.setColor(Style.COLOR_FUNCTION_DEF, RustLexer.FUNCTION_DEF)
        self.setColor(Style.COLOR_CONSTANT, RustLexer.DECORATOR)
        self.setColor(Style.COLOR_BUILTIN, RustLexer.BUILTINS)
        self.setColor(Style.COLOR_BUILTIN, RustLexer.TYPES)
        self.setColor(Style.COLOR_CONSTANT, RustLexer.CONSTANTS)
        self.setColor(Style.COLOR_STRING, RustLexer.STRING)

    def styleText(self, start, end):
        text = self.editor().text()[start:end]
        self.generateTokens(text)
        self.startStyling(start)

        # loop optimizations
        sendScintilla = self.editor().SendScintilla
        setStyling = self.setStyling
        keywordList = self.keywordList
        builtinList = self.builtinList
        typeList = self.typeList
        peekToken = self.peekToken
        nextToken = self.nextToken
        skipSpacesPeek = self.skipSpacesPeek

        string_flag = False
        string_tok = None
        comment_flag = False

        if start > 0:
            previous_style_nr = sendScintilla(QsciScintilla.SCI_GETSTYLEAT, start - 1)

            if previous_style_nr == RustLexer.COMMENTS:
                comment_flag = False

        while True:
            curr_token = nextToken()

            if curr_token is None:
                break

            tok = curr_token[0]
            tok_len = curr_token[1]

            if comment_flag:
                setStyling(tok_len, RustLexer.COMMENTS)

                if tok.endswith('\n') or tok.startswith('\n'):
                    comment_flag = False

                continue

            if string_flag:
                setStyling(tok_len, RustLexer.STRING)

                if tok == string_tok:
                    string_flag = False
                    string_tok = None

                continue

            if tok in ('struct', 'enum'):
                name, ni = skipSpacesPeek()
                brac, _ = skipSpacesPeek(ni)

                if name[0].isidentifier() and brac[0] == '{':
                    setStyling(tok_len, RustLexer.KEYWORD)
                    _ = nextToken(ni)
                    setStyling(name[1] + 1, RustLexer.CLASS_DEF)

                else:
                    setStyling(tok_len, RustLexer.KEYWORD)

                continue

            elif tok == 'fn':
                name, ni = skipSpacesPeek()

                if name[0].isidentifier():
                    setStyling(tok_len, RustLexer.KEYWORD)
                    _ = nextToken(ni)
                    setStyling(name[1] + 1, RustLexer.FUNCTION_DEF)

                else:
                    setStyling(tok_len, RustLexer.KEYWORD)

                continue

            elif tok == '"':
                setStyling(tok_len, RustLexer.STRING)
                string_flag = True
                string_tok = tok

                continue

            elif tok == '!':
                if peekToken()[0] == '(': # macro
                    setStyling(tok_len, RustLexer.BUILTINS)

                continue

            elif tok == '/':
                if peekToken()[0] == '/': # this is a comment hence the '//'
                    _ = nextToken() # consume '/'
                    comment_text = tok
                    comment_len = tok_len + 1 # include the consumed '/'

                    while True:
                        peek = peekToken()

                        if peek is None or '\n' in peek[0]:
                            break

                        next_tok = nextToken()

                        if next_tok is None:
                            break

                        comment_text += next_tok[0]
                        comment_len += next_tok[1]

                    setStyling(comment_len, RustLexer.COMMENTS)

                continue

            elif tok == '#':
                attribute_text = tok
                attribute_len = tok_len

                while True:
                    peek = peekToken()

                    if peek is None or '\n' in peek[0]:
                        break

                    next_tok = nextToken()

                    if next_tok is None:
                        break

                    attribute_text += next_tok[0]
                    attribute_len += next_tok[1]

                setStyling(attribute_len, RustLexer.DECORATOR)

                continue

            elif tok.isnumeric():
                setStyling(tok_len, RustLexer.CONSTANTS)

                continue

            elif tok in ['(', ')', '{', '}', '[', ']']:
                setStyling(tok_len, RustLexer.BRACKETS)

                continue

            elif tok in keywordList():
                setStyling(tok_len, RustLexer.KEYWORD)

                continue

            elif tok in builtinList():
                setStyling(tok_len, RustLexer.BUILTINS)

                continue

            elif tok in typeList():
                setStyling(tok_len, RustLexer.TYPES)

                continue

            else:
                setStyling(tok_len, RustLexer.DEFAULT)

        self.applyFolding(start, end)

    def applyFolding(self, start: int, end: int):
        start_line = self.editor().SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, start)
        end_line = self.editor().SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, end)

        for line_num in range(start_line, end_line + 1):
            line_text = self.editor().text(line_num)
            indent = self.editor().SendScintilla(QsciScintilla.SCI_GETLINEINDENTATION, line_num)
            level = QsciScintilla.SC_FOLDLEVELBASE + indent // self.editor().tabWidth()

            is_blank = not line_text.strip()

            if line_text.strip().startswith((
                    'pub', 'use', 'fn', 'struct', 'enum', 'impl', 'trait', 'if', 'else',
                    'async', 'match', 'for', 'while', 'loop')):
                level |= QsciScintilla.SC_FOLDLEVELHEADERFLAG

            elif 'else' in line_text:
                level |= QsciScintilla.SC_FOLDLEVELHEADERFLAG

            if is_blank:
                level |= QsciScintilla.SC_FOLDLEVELWHITEFLAG

            self.editor().SendScintilla(QsciScintilla.SCI_SETFOLDLEVEL, line_num, level)


class HTMLLexer(QsciLexerHTML):
    def __init__(self):
        super().__init__()
        self.setDefaultColor(QColor('#ffffff'))
        self.setDefaultPaper(Style.COLOR_BG)
        self.setDefaultFont(Style.FONT_NORMAL)
        self.setFoldCompact(False)

        self.createStyle()

    def createStyle(self):
        self.setFont(Style.FONT_NORMAL, HTMLLexer.Default)
        self.setFont(Style.FONT_ITALIC, HTMLLexer.HTMLComment)

        self.setColor(Style.COLOR_NORMAL, HTMLLexer.Default)
        self.setColor(Style.COLOR_COMMENT, HTMLLexer.HTMLComment)
        self.setColor(Style.COLOR_CONSTANT, HTMLLexer.HTMLNumber)
        self.setColor(Style.COLOR_CONSTANT, HTMLLexer.HTMLValue)
        self.setColor(Style.COLOR_STRING, HTMLLexer.HTMLSingleQuotedString)
        self.setColor(Style.COLOR_STRING, HTMLLexer.HTMLDoubleQuotedString)
        self.setColor(Style.COLOR_KEYWORD, HTMLLexer.Tag)
        self.setColor(Style.COLOR_KEYWORD, HTMLLexer.UnknownTag)
        self.setColor(Style.COLOR_BUILTIN, HTMLLexer.OtherInTag)
        self.setColor(Style.COLOR_BUILTIN, HTMLLexer.Attribute)
        self.setColor(Style.COLOR_KEYWORD, HTMLLexer.UnknownAttribute)
        self.setColor(Style.COLOR_KEYWORD, HTMLLexer.Entity)

        self.setPaper(Style.COLOR_BG, HTMLLexer.Default)

        # style internal js (javascript sucks btw pls dont use it)
        self.setFont(Style.FONT_NORMAL, HTMLLexer.JavaScriptDefault)
        self.setFont(Style.FONT_ITALIC, HTMLLexer.JavaScriptComment)
        self.setFont(Style.FONT_ITALIC, HTMLLexer.JavaScriptCommentDoc)
        self.setFont(Style.FONT_ITALIC, HTMLLexer.JavaScriptCommentLine)
        self.setFont(Style.FONT_NORMAL, HTMLLexer.JavaScriptWord)
        self.setFont(Style.FONT_NORMAL, HTMLLexer.JavaScriptKeyword)
        self.setFont(Style.FONT_NORMAL, HTMLLexer.JavaScriptSymbol)
        self.setFont(Style.FONT_NORMAL, HTMLLexer.JavaScriptRegex)
        self.setFont(Style.FONT_NORMAL, HTMLLexer.JavaScriptStart)
        self.setFont(Style.FONT_NORMAL, HTMLLexer.JavaScriptNumber)
        self.setFont(Style.FONT_NORMAL, HTMLLexer.JavaScriptSingleQuotedString)
        self.setFont(Style.FONT_NORMAL, HTMLLexer.JavaScriptDoubleQuotedString)
        self.setFont(Style.FONT_NORMAL, HTMLLexer.JavaScriptUnclosedString)

        self.setColor(Style.COLOR_NORMAL, HTMLLexer.JavaScriptDefault)
        self.setColor(Style.COLOR_COMMENT, HTMLLexer.JavaScriptComment)
        self.setColor(Style.COLOR_COMMENT, HTMLLexer.JavaScriptCommentDoc)
        self.setColor(Style.COLOR_COMMENT, HTMLLexer.JavaScriptCommentLine)
        self.setColor(Style.COLOR_NORMAL, HTMLLexer.JavaScriptWord)
        self.setColor(Style.COLOR_NORMAL, HTMLLexer.JavaScriptKeyword)
        self.setColor(Style.COLOR_NORMAL, HTMLLexer.JavaScriptSymbol)
        self.setColor(Style.COLOR_NORMAL, HTMLLexer.JavaScriptRegex)
        self.setColor(Style.COLOR_NORMAL, HTMLLexer.JavaScriptStart)
        self.setColor(Style.COLOR_NORMAL, HTMLLexer.JavaScriptNumber)
        self.setColor(Style.COLOR_NORMAL, HTMLLexer.JavaScriptSingleQuotedString)
        self.setColor(Style.COLOR_NORMAL, HTMLLexer.JavaScriptDoubleQuotedString)
        self.setColor(Style.COLOR_NORMAL, HTMLLexer.JavaScriptUnclosedString)

        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptDefault)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptComment)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptCommentDoc)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptCommentLine)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptWord)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptKeyword)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptSymbol)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptRegex)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptStart)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptNumber)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptSingleQuotedString)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptDoubleQuotedString)
        self.setPaper(Style.COLOR_BG, HTMLLexer.JavaScriptUnclosedString)


class CSSLexer(QsciLexerCSS):
    def __init__(self):
        super().__init__()
        self.setDefaultColor(QColor('#ffffff'))
        self.setDefaultPaper(Style.COLOR_BG)
        self.setDefaultFont(Style.FONT_NORMAL)
        self.setFoldComments(True)
        self.setFoldCompact(False)

        self.createStyle()

    def createStyle(self):
        self.setFont(Style.FONT_NORMAL, CSSLexer.Tag)
        self.setFont(Style.FONT_ITALIC, CSSLexer.Comment)

        self.setColor(Style.COLOR_NORMAL, CSSLexer.Default)
        self.setColor(Style.COLOR_NORMAL, CSSLexer.Operator)
        self.setColor(Style.COLOR_NORMAL, CSSLexer.CSS1Property)
        self.setColor(Style.COLOR_NORMAL, CSSLexer.CSS2Property)
        self.setColor(Style.COLOR_NORMAL, CSSLexer.CSS3Property)
        self.setColor(Style.COLOR_NORMAL, CSSLexer.UnknownProperty)
        self.setColor(Style.COLOR_COMMENT, CSSLexer.Comment)
        self.setColor(Style.COLOR_KEYWORD, CSSLexer.Tag)
        self.setColor(Style.COLOR_CONSTANT, CSSLexer.Value)
        self.setColor(QColor('#e06c75'), CSSLexer.Variable)
        self.setColor(Style.COLOR_BUILTIN, CSSLexer.IDSelector)
        self.setColor(Style.COLOR_BUILTIN, CSSLexer.UnknownPseudoClass)
        self.setColor(Style.COLOR_BUILTIN, CSSLexer.PseudoClass)
        self.setColor(Style.COLOR_STRING, CSSLexer.DoubleQuotedString)
        self.setColor(Style.COLOR_STRING, CSSLexer.SingleQuotedString)


class JSONLexer(QsciLexerJSON):
    def __init__(self):
        super().__init__()
        self.setDefaultColor(QColor('#ffffff'))
        self.setDefaultPaper(Style.COLOR_BG)
        self.setDefaultFont(Style.FONT_NORMAL)
        self.setFoldCompact(False)

        self.createStyle()

    def createStyle(self):
        self.setFont(Style.FONT_NORMAL, JSONLexer.Default)
        self.setFont(Style.FONT_NORMAL, JSONLexer.Keyword)
        self.setFont(Style.FONT_NORMAL, JSONLexer.KeywordLD)
        self.setFont(Style.FONT_ITALIC, JSONLexer.CommentLine)
        self.setFont(Style.FONT_ITALIC, JSONLexer.CommentBlock)

        self.setColor(Style.COLOR_NORMAL, JSONLexer.Default)
        self.setColor(Style.COLOR_NORMAL, JSONLexer.Operator)
        self.setColor(Style.COLOR_COMMENT, JSONLexer.CommentLine)
        self.setColor(Style.COLOR_COMMENT, JSONLexer.CommentBlock)
        self.setColor(Style.COLOR_BUILTIN, JSONLexer.Property)
        self.setColor(Style.COLOR_CONSTANT, JSONLexer.Keyword)
        self.setColor(Style.COLOR_CONSTANT, JSONLexer.KeywordLD)
        self.setColor(Style.COLOR_CONSTANT, JSONLexer.Number)
        self.setColor(Style.COLOR_CONSTANT, JSONLexer.EscapeSequence)
        self.setColor(Style.COLOR_STRING, JSONLexer.String)
        self.setColor(Style.COLOR_ERROR, JSONLexer.UnclosedString)
        self.setColor(Style.COLOR_ERROR, JSONLexer.Error)

        self.setPaper(Style.COLOR_BG, JSONLexer.Default)
        self.setPaper(Style.COLOR_BG, JSONLexer.Error)


class TOMLLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor, 'TOML')
        self.setKeywords(['true', 'false', '='])

    def createStyle(self):
        self.setFont(Style.FONT_NORMAL, TOMLLexer.DEFAULT)
        self.setFont(Style.FONT_ITALIC, TOMLLexer.COMMENTS)
        self.setColor(Style.COLOR_NORMAL, TOMLLexer.DEFAULT)
        self.setColor(Style.COLOR_NORMAL, TOMLLexer.BRACKETS)
        self.setColor(Style.COLOR_COMMENT, TOMLLexer.COMMENTS)
        self.setColor(Style.COLOR_BUILTIN, TOMLLexer.KEYWORD)
        self.setColor(Style.COLOR_CONSTANT, TOMLLexer.BUILTINS)
        self.setColor(Style.COLOR_CONSTANT, TOMLLexer.CONSTANTS)
        self.setColor(Style.COLOR_STRING, TOMLLexer.STRING)

    def styleText(self, start, end):
        text = self.editor().text()[start:end]
        self.generateTokens(text)

        sendScintilla = self.editor().SendScintilla
        setStyling = self.setStyling
        keywordList = self.keywordList
        builtinList = self.builtinList
        typeList = self.typeList
        peekToken = self.peekToken
        nextToken = self.nextToken

        string_flag = False
        string_tok = None
        comment_flag = False

        if start > 0:
            previous_style_nr = sendScintilla(QsciScintilla.SCI_GETSTYLEAT, start - 1)

            if previous_style_nr == TOMLLexer.COMMENTS:
                comment_flag = False

        while True:
            curr_token = nextToken()

            if curr_token is None:
                break

            tok = curr_token[0]
            tok_len = curr_token[1]

            if comment_flag:
                setStyling(tok_len, RustLexer.COMMENTS)

                if tok.endswith('\n') or tok.startswith('\n'):
                    comment_flag = False

                continue

            if string_flag:
                setStyling(tok_len, RustLexer.STRING)

                if tok == string_tok:
                    string_flag = False
                    string_tok = None

                continue

            elif tok == '"' or tok == "'":
                setStyling(tok_len, TOMLLexer.STRING)
                string_flag = True
                string_tok = tok

                continue

            elif tok == '#':
                setStyling(tok_len, TOMLLexer.COMMENTS)
                comment_flag = True

                continue

            elif tok.isidentifier() and tok not in keywordList():
                setStyling(tok_len, TOMLLexer.BUILTINS)

                continue

            elif tok.isnumeric():
                setStyling(tok_len, TOMLLexer.CONSTANTS)

                continue

            elif tok in ['(', ')', '{', '}', '[', ']']:
                setStyling(tok_len, TOMLLexer.BRACKETS)

                continue

            elif tok in keywordList():
                setStyling(tok_len, TOMLLexer.KEYWORD)

                continue

            elif tok in builtinList():
                setStyling(tok_len, TOMLLexer.BUILTINS)

                continue

            elif tok in typeList():
                setStyling(tok_len, TOMLLexer.TYPES)

                continue

            else:
                setStyling(tok_len, TOMLLexer.DEFAULT)


class MarkdownLexer(QsciLexerMarkdown):
    def __init__(self):
        super().__init__()
        self.setDefaultColor(QColor('#ffffff'))
        self.setDefaultPaper(Style.COLOR_BG)
        self.setDefaultFont(Style.FONT_NORMAL)

        self.createStyle()

    def createStyle(self):
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.Default)
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.Header1)
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.Header2)
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.Header3)
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.Header4)
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.Header5)
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.Header6)
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.EmphasisAsterisks)
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.StrongEmphasisAsterisks)
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.CodeBlock)
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.CodeBackticks)
        self.setFont(Style.FONT_NORMAL, MarkdownLexer.CodeDoubleBackticks)
        self.setFont(Style.FONT_ITALIC, MarkdownLexer.EmphasisUnderscores)
        self.setFont(Style.FONT_ITALIC, MarkdownLexer.StrongEmphasisUnderscores)
        self.setFont(Style.FONT_ITALIC, MarkdownLexer.StrikeOut)
        self.setFont(Style.FONT_UNDERLINE, MarkdownLexer.Link)
        self.setFont(Style.FONT_BOLD, MarkdownLexer.HorizontalRule)
        self.setColor(Style.COLOR_NORMAL, MarkdownLexer.Default)
        self.setColor(Style.COLOR_NORMAL, MarkdownLexer.HorizontalRule)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.CodeBlock)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.CodeBackticks)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.CodeDoubleBackticks)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.Header1)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.Header2)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.Header3)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.Header4)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.Header5)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.Header6)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.EmphasisAsterisks)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.StrongEmphasisAsterisks)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.EmphasisUnderscores)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.StrongEmphasisUnderscores)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.BlockQuote)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.OrderedListItem)
        self.setColor(Style.COLOR_CONSTANT, MarkdownLexer.UnorderedListItem)
        self.setColor(Style.COLOR_LINK, MarkdownLexer.Link)

        # ensure the -, `, and > don't have a background
        self.setPaper(Style.COLOR_BG, MarkdownLexer.HorizontalRule)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.OrderedListItem)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.UnorderedListItem)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.Prechar)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.BlockQuote)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.Header1)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.Header2)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.Header3)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.Header4)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.Header5)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.Header6)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.CodeBlock)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.CodeBackticks)
        self.setPaper(Style.COLOR_BG, MarkdownLexer.CodeDoubleBackticks)


class PlainTextLexer(BaseLexer):
    def __init__(self, editor):
        super().__init__(editor, 'Plain Text')

    def createStyle(self):
        self.setColor(Style.COLOR_NORMAL, PlainTextLexer.DEFAULT)

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.editor().text()[start:end]

        self.setStyling(len(text), PlainTextLexer.DEFAULT)
