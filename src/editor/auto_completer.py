from src.imports import *


class AutoCompleter(QThread):
    FileTypePython = 0
    FileTypeRust = 1
    FileTypeHtml = 2
    FileTypeCSS = 3
    FileTypeMarkdown = 4
    FileTypePlainText = 5

    def __init__(self, file_name: str, file_type, api: QsciAPIs):
        super(AutoCompleter, self).__init__(None)

        self._file_name = file_name
        self._file_type = file_type
        self._api = api

        self.line = 0
        self.index = 0
        self.text = ''

    def run(self):
        try:
            if self._file_type == AutoCompleter.FileTypePython:
                self.script = jedi.Script(self.text, path=self._file_name)
                self.loadAutoCompletions(self.script.complete(self.line, self.index))

            else:
                self.loadAutoCompletions([])

        except Exception as e:
            print(e)

        self.finished.emit()

    def loadAutoCompletions(self, completions):
        self._api.clear()
        [self._api.add(i.name) for i in completions]
        self._api.prepare()

    def getPyCompletion(self, line: int, index: int, text: str):
        self.line = line
        self.index = index
        self.text = text.replace('\t', '    ')
        self.start()

    def getPlainTextCompletion(self, line: int, index: int, text: str):
        self.line = line
        self.index = index
        self.text = text.replace('\t', '    ')
        self.start()